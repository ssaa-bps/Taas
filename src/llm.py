"""Appels à Ollama : un seul endroit pour mesurer, journaliser et enregistrer chaque appel."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ollama import Client, ResponseError

from .config import Config
from .hardware import ResourceMonitor, log_system_info, model_usage, system_info
from .report import append_result

log = logging.getLogger("gherkin")


def _seconds(nanoseconds: Optional[int]) -> float:
    return (nanoseconds or 0) / 1e9


@dataclass
class Call:
    """Résultat d'un appel : le texte du modèle et la ligne de métriques à compléter puis publier."""
    text: str
    record: Dict[str, Any] = field(default_factory=dict)


class LLM:
    def __init__(self, cfg: Config, client: Optional[Client] = None):
        self.cfg = cfg
        self.client = client or Client(host=cfg.host, timeout=cfg.timeout)
        self._sysinfo: Optional[Dict[str, Any]] = None
        self.output_files: List[str] = []         # fichiers .feature générés
        self.records: List[Dict[str, Any]] = []   # une ligne par appel, affichée en tableau à la fin

    # ------------------------------------------------------------------ #
    def _chat(self, prompt: str, json_mode: bool, step: str = "") -> Any:
        kwargs: dict = {
            "model": self.cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "options": self.cfg.ollama_options(step),
            "keep_alive": self.cfg.keep_alive,
        }
        if json_mode:
            kwargs["format"] = "json"      # force une sortie JSON valide
        if self.cfg.think is not None:
            kwargs["think"] = self.cfg.think

        try:
            return self.client.chat(**kwargs)
        except ResponseError as exc:
            # Certains modèles ne gèrent pas le paramètre "think" : on réessaie sans.
            if "think" in kwargs and "think" in str(exc).lower():
                log.warning("Model '%s' does not support 'think'; retrying without it", self.cfg.model)
                kwargs.pop("think")
                return self.client.chat(**kwargs)
            raise

    # ------------------------------------------------------------------ #
    def ask(self, step: str, prompt: str, *, spec: str, exigence: str = "", json_mode: bool = False) -> Call:
        """Envoie `prompt` au modèle. `step` : exigences | dictionary | gherkin.

        En cas d'erreur d'Ollama, la ligne d'échec est publiée ici puis l'exception est relancée.
        En cas de succès, l'appelant complète la ligne (items, statut) et appelle `finish()`.
        """
        cfg = self.cfg
        record: Dict[str, Any] = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "spec": spec, "step": step,
            "exigence": exigence, "model": cfg.model, "language": cfg.gherkin_language, "status": "FAILED",
        }
        started = time.perf_counter()
        log.info("Starting step '%s' - spec: %s%s", step, spec, f" - exigence: {exigence}" if exigence else "")

        monitor = ResourceMonitor(cfg.host)
        monitor.start()
        try:
            response = self._chat(prompt, json_mode, step)
        except KeyboardInterrupt:
            monitor.stop()
            self.finish(Call("", record), "INTERRUPTED", items=None, error="Interrupted by user (Ctrl+C)")
            raise
        except Exception as exc:  # noqa: BLE001
            monitor.stop()
            record["error"] = (f"Model not found: {cfg.model}" if getattr(exc, "status_code", None) == 404
                               else str(exc)[:200])
            self.finish(Call("", record), "FAILED", items=None)
            raise
        live = monitor.stop()

        elapsed = time.perf_counter() - started
        tin = response.prompt_eval_count or 0
        tout = response.eval_count or 0
        prompt_s = _seconds(response.prompt_eval_duration)
        gen_s = _seconds(response.eval_duration)

        log.info("Model: %s", response.model or cfg.model)
        log.info("Input tokens: %d", tin)
        log.info("Output tokens: %d", tout)
        log.info("Total tokens: %d", tin + tout)
        log.info("Prompt processing time: %.3f seconds", prompt_s)
        log.info("Generation time: %.3f seconds", gen_s)
        log.info("Total execution time: %.3f seconds", elapsed)
        if tin + tout >= cfg.num_ctx:
            log.warning("Prompt + answer reach num_ctx (%d tokens): the input may have been truncated. "
                        "Increase llm.num_ctx in config.yaml.", cfg.num_ctx)

        if self._sysinfo is None:
            self._sysinfo = system_info()
            log_system_info(self._sysinfo)
        sysinfo = self._sysinfo
        usage = model_usage(self.client, cfg.model)

        record.update(
            input_tokens=tin, output_tokens=tout, total_tokens=tin + tout,
            prompt_time=round(prompt_s, 3), gen_time=round(gen_s, 3), total_time=round(elapsed, 3),
            tokens_per_s=round(tout / gen_s, 1) if gen_s else None,
            cpu_avg=live["cpu_avg"], cpu_peak=live["cpu_peak"], ram_avg=live["ram_avg"], ram_peak=live["ram_peak"],
            gpu_avg=live["gpu_avg"], gpu_peak=live["gpu_peak"], vram_peak=live["vram_peak"],
            llm_total_gb=usage["total_gb"], llm_vram_gb=usage["vram_gb"], llm_ram_gb=usage["ram_gb"],
            placement=usage["placement"],
            cpu=sysinfo["cpu"], cores=sysinfo["cores"], ram_total_gb=sysinfo["ram_total_gb"], gpu=sysinfo["gpu"],
        )
        return Call(text=response.message.content or "", record=record)

    # ------------------------------------------------------------------ #
    def finish(self, call: Call, status: str, items: Optional[int], output_file: str = "", error: str = "") -> None:
        """Complète la ligne de l'appel, l'ajoute à l'Excel et affiche le récapitulatif."""
        rec = call.record
        rec["status"] = status
        if items is not None:
            rec["items"] = items
        if output_file:
            rec["output_file"] = output_file
        if error:
            rec["error"] = error[:200]
        append_result(self.cfg.results_file, rec)
        self.records.append(dict(rec))
        log.info("//// %s | %s | %s ////", rec.get("model"), rec.get("step"), status)
