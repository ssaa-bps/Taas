"""Matériel : configuration de la machine, mémoire du modèle (ollama ps) et
mesure en direct de la charge CPU / RAM / GPU pendant la génération (comme le Gestionnaire des tâches)."""
from __future__ import annotations

import logging
import platform
import shutil
import subprocess
import threading
from typing import Any, Dict, List, Optional

log = logging.getLogger("gherkin")

SAMPLE_INTERVAL = 1.0  # secondes entre deux mesures


def _run(cmd: List[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def _gb(n_bytes: float) -> float:
    return round(n_bytes / 1024 ** 3, 2)


def cpu_name() -> str:
    system = platform.system()
    name = ""
    if system == "Windows":
        out = _run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"])
        name = out.splitlines()[0].strip() if out else ""
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        name = line.split(":", 1)[1].strip()
                        break
        except OSError:
            pass
    elif system == "Darwin":
        name = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
    return name or platform.processor() or "unknown"


def gpu_list() -> List[str]:
    """GPU NVIDIA via nvidia-smi (si disponible)."""
    if not shutil.which("nvidia-smi"):
        return []
    out = _run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
    gpus = []
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 2:
            gpus.append(f"{parts[0]} ({float(parts[1]) / 1024:.1f} GB VRAM)")
    return gpus


def system_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {"cpu": cpu_name(), "cores": "", "ram_total_gb": None,
                            "gpu": " + ".join(gpu_list()) or "none"}
    try:
        import psutil
        info["cores"] = f"{psutil.cpu_count(logical=False) or 0} physical / {psutil.cpu_count(logical=True) or 0} logical"
        info["ram_total_gb"] = _gb(psutil.virtual_memory().total)
    except ImportError:
        pass
    return info


def log_system_info(info: Dict[str, Any]) -> None:
    log.info("Hardware - CPU: %s", info["cpu"])
    log.info("Hardware - CPU cores: %s", info["cores"] or "unavailable (pip install psutil)")
    log.info("Hardware - RAM total: %s GB", info["ram_total_gb"])
    log.info("Hardware - GPU: %s", info["gpu"] if info["gpu"] != "none" else "none detected (nvidia-smi not found)")


def model_usage(client: Any, model: str) -> Dict[str, Any]:
    """Mémoire du modèle chargé (RAM vs VRAM), d'après `ollama ps`."""
    usage: Dict[str, Any] = {"total_gb": None, "vram_gb": None, "ram_gb": None, "placement": ""}
    try:
        loaded = client.ps().models
    except Exception as exc:  # noqa: BLE001
        log.info("LLM memory usage: unavailable (%s)", exc)
        return usage

    entry: Optional[Any] = next(
        (m for m in loaded if model in {getattr(m, "model", None), getattr(m, "name", None)}),
        loaded[0] if loaded else None,
    )
    if entry is None:
        log.info("LLM memory usage: model not loaded anymore")
        return usage

    total = entry.size or 0
    vram = entry.size_vram or 0
    usage["total_gb"], usage["vram_gb"], usage["ram_gb"] = _gb(total), _gb(vram), _gb(max(total - vram, 0))
    if total:
        gpu_pct = round(100 * vram / total)
        usage["placement"] = f"{gpu_pct}% GPU / {100 - gpu_pct}% CPU"
    log.info("LLM memory usage - total: %s GB", usage["total_gb"])
    log.info("LLM memory usage - VRAM (GPU): %s GB", usage["vram_gb"])
    log.info("LLM memory usage - RAM (CPU): %s GB", usage["ram_gb"])
    log.info("LLM processor placement: %s", usage["placement"] or "unknown")
    return usage


class ResourceMonitor:
    """Mesure toutes les secondes, pendant la génération, la charge d'Ollama
    (CPU en % de la machine, RAM en Go, comme le Gestionnaire des tâches) et du GPU NVIDIA.

    Processus suivis : tout processus dont le nom contient « ollama », le processus qui écoute
    sur le port du serveur Ollama et tous leurs processus enfants (le « runner » du modèle).
    Si aucun n'est trouvé (Ollama dans WSL / Docker...), repli sur la charge de toute la machine.
    """

    def __init__(self, host: str = "http://127.0.0.1:11434", interval: float = SAMPLE_INTERVAL):
        self.interval = interval
        self.port = _port_from_host(host)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.cpu: List[float] = []
        self.ram: List[float] = []
        self.gpu_util: List[float] = []
        self.gpu_mem: List[float] = []
        self.seen: Dict[int, str] = {}      # pid -> nom, pour le diagnostic
        self.mode = "process"               # "process" ou "system" (repli)
        self._baseline_ram = 0.0
        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            self._psutil = None
        self._nvidia = bool(shutil.which("nvidia-smi"))
        self._procs: Dict[int, Any] = {}

    # -- recherche des processus Ollama --------------------------------------
    def _server_pids(self) -> List[int]:
        ps = self._psutil
        try:
            conns = ps.net_connections(kind="tcp")
        except Exception:  # noqa: BLE001
            return []
        return [c.pid for c in conns if c.status == "LISTEN" and c.laddr and c.laddr.port == self.port and c.pid]

    def _ollama_processes(self) -> List[Any]:
        ps = self._psutil
        found: Dict[int, Any] = {}
        for p in ps.process_iter(["pid", "name"]):
            if "ollama" in (p.info["name"] or "").lower():
                found[p.pid] = p
        for pid in self._server_pids():
            try:
                root = self._procs.get(pid) or ps.Process(pid)
                found[pid] = root
                for child in root.children(recursive=True):
                    found[child.pid] = child
            except Exception:  # noqa: BLE001
                continue
        # Ajoute aussi les enfants des processus « ollama » (runner lancé sous un autre nom)
        for p in list(found.values()):
            try:
                for child in p.children(recursive=True):
                    found.setdefault(child.pid, child)
            except Exception:  # noqa: BLE001
                continue
        # Réutilise les objets déjà vus : cpu_percent() a besoin de la mesure précédente
        self._procs = {pid: self._procs.get(pid, p) for pid, p in found.items()}
        for pid, p in self._procs.items():
            if pid not in self.seen:
                try:
                    self.seen[pid] = p.name()
                except Exception:  # noqa: BLE001
                    self.seen[pid] = "?"
        return list(self._procs.values())

    def _sample(self) -> None:
        if self._psutil is not None:
            ps = self._psutil
            n_cpu = ps.cpu_count(logical=True) or 1
            procs = self._ollama_processes()
            if procs:
                cpu = ram = 0.0
                for p in procs:
                    try:
                        cpu += p.cpu_percent(interval=None)
                        ram += p.memory_info().rss
                    except Exception:  # noqa: BLE001
                        continue
                self.cpu.append(min(cpu / n_cpu, 100.0))
                self.ram.append(_gb(ram))
            else:
                self.mode = "system"
                self.cpu.append(ps.cpu_percent(interval=None))
                self.ram.append(max(_gb(ps.virtual_memory().used) - self._baseline_ram, 0.0))
        if self._nvidia:
            out = _run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                        "--format=csv,noheader,nounits"])
            try:
                util, mem = [float(x) for x in out.splitlines()[0].split(",")]
                self.gpu_util.append(util)
                self.gpu_mem.append(round(mem / 1024, 2))
            except Exception:  # noqa: BLE001
                pass

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._sample()
            self._stop.wait(self.interval)

    def start(self) -> None:
        if self._psutil is not None:
            self._baseline_ram = _gb(self._psutil.virtual_memory().used)
            self._psutil.cpu_percent(interval=None)   # amorce la mesure système
            self._ollama_processes()
            for p in self._procs.values():
                try:
                    p.cpu_percent(interval=None)       # amorce (la 1re mesure vaut toujours 0)
                except Exception:  # noqa: BLE001
                    pass
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> Dict[str, Any]:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

        def stats(values: List[float]):
            return (round(sum(values) / len(values), 1), round(max(values), 1)) if values else (None, None)

        res: Dict[str, Any] = {}
        res["cpu_avg"], res["cpu_peak"] = stats(self.cpu)
        res["ram_avg"], res["ram_peak"] = stats(self.ram)
        res["gpu_avg"], res["gpu_peak"] = stats(self.gpu_util)
        res["vram_avg"], res["vram_peak"] = stats(self.gpu_mem)
        res["samples"] = len(self.cpu) or len(self.gpu_util)

        if self._psutil is None:
            log.warning("Live usage unavailable: psutil is not installed (python -m pip install psutil)")
        elif self.mode == "system":
            log.warning("No Ollama process found on this machine (Ollama in WSL/Docker/remote?): "
                        "CPU/RAM below are for the WHOLE machine, not only Ollama")
        else:
            log.info("Live usage - monitored processes: %s",
                     ", ".join(f"{n}({pid})" for pid, n in sorted(self.seen.items())) or "none")
        label = "Machine" if self.mode == "system" else "Ollama"
        log.info("Live usage (%d samples) - %s CPU: avg %s%% / peak %s%% (of the whole machine)",
                 res["samples"], label, res["cpu_avg"], res["cpu_peak"])
        log.info("Live usage - %s RAM: avg %s GB / peak %s GB", label, res["ram_avg"], res["ram_peak"])
        if self._nvidia:
            log.info("Live usage - GPU: avg %s%% / peak %s%% | GPU memory used: avg %s GB / peak %s GB",
                     res["gpu_avg"], res["gpu_peak"], res["vram_avg"], res["vram_peak"])
        else:
            log.info("Live usage - GPU: no NVIDIA GPU detected (nvidia-smi not found), GPU values not available")
        return res


def _port_from_host(host: str) -> int:
    try:
        return int(host.rsplit(":", 1)[1].split("/")[0])
    except Exception:  # noqa: BLE001
        return 11434
