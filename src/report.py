"""Tableau récapitulatif des exécutions (Excel) : une ligne ajoutée à chaque exécution."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

log = logging.getLogger("gherkin")

# (clé, titre de colonne, largeur)
COLUMNS = [
    ("date", "Date", 19),
    ("spec", "Specification", 16),
    ("step", "Step", 12),
    ("exigence", "Exigence", 16),
    ("model", "Model", 24),
    ("language", "Language", 10),
    ("status", "Status", 14),
    ("items", "Items", 9),
    ("input_tokens", "Input tokens", 13),
    ("output_tokens", "Output tokens", 14),
    ("total_tokens", "Total tokens", 13),
    ("prompt_time", "Prompt time (s)", 16),
    ("gen_time", "Generation time (s)", 19),
    ("total_time", "Total time (s)", 15),
    ("tokens_per_s", "Tokens/s", 10),
    ("cpu_avg", "Ollama CPU avg (%)", 18),
    ("cpu_peak", "Ollama CPU peak (%)", 19),
    ("ram_avg", "Ollama RAM avg (GB)", 19),
    ("ram_peak", "Ollama RAM peak (GB)", 20),
    ("gpu_avg", "GPU avg (%)", 12),
    ("gpu_peak", "GPU peak (%)", 13),
    ("vram_peak", "GPU mem peak (GB)", 18),
    ("llm_total_gb", "LLM size (GB)", 14),
    ("llm_vram_gb", "LLM in VRAM (GB)", 17),
    ("llm_ram_gb", "LLM in RAM (GB)", 16),
    ("placement", "Placement", 18),
    ("cpu", "CPU", 38),
    ("cores", "Cores", 20),
    ("ram_total_gb", "RAM total (GB)", 15),
    ("gpu", "GPU", 34),
    ("output_file", "Output file", 34),
    ("error", "Error", 40),
]

_HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
_OK_FILL = PatternFill("solid", fgColor="E2EFDA")
_KO_FILL = PatternFill("solid", fgColor="F8CBAD")
_ALT_FILL = PatternFill("solid", fgColor="F2F2F2")
_THIN = Side(style="thin", color="BFBFBF")
_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)


def _same_layout(results_file: Path) -> bool:
    try:
        ws = load_workbook(results_file, read_only=True).active
        header = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    except Exception:  # noqa: BLE001
        return False
    return header == [title for _, title, _ in COLUMNS]


def append_result(results_file: Path, record: Dict[str, Any]) -> None:
    """Ajoute une ligne au fichier Excel (le crée avec mise en forme s'il n'existe pas)."""
    results_file = Path(results_file)
    results_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        if results_file.is_file() and not _same_layout(results_file):
            backup = results_file.with_name(f"{results_file.stem}_old_{datetime.now():%Y%m%d_%H%M%S}{results_file.suffix}")
            results_file.rename(backup)
            log.warning("%s has an older column layout: renamed to %s, a new file is created",
                        results_file.name, backup.name)
        if results_file.is_file():
            wb = load_workbook(results_file)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Executions"
            for col, (_, title, width) in enumerate(COLUMNS, start=1):
                cell = ws.cell(row=1, column=col, value=title)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = _HEADER_FILL
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = _BORDER
                ws.column_dimensions[get_column_letter(col)].width = width
            ws.row_dimensions[1].height = 32
            ws.freeze_panes = "D2"

        row = ws.max_row + 1
        ok = str(record.get("status", "")).upper().startswith("OK")
        for col, (key, _, _) in enumerate(COLUMNS, start=1):
            value = record.get(key)
            cell = ws.cell(row=row, column=col, value=value if value not in (None, "") else "-")
            cell.border = _BORDER
            cell.alignment = Alignment(vertical="center", horizontal="left" if isinstance(value, str) else "center")
            if row % 2 == 1:
                cell.fill = _ALT_FILL
            if key == "status":
                cell.fill = _OK_FILL if ok else _KO_FILL
                cell.font = Font(bold=True)
        ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{row}"
        wb.save(results_file)
        log.info("Results table updated: %s", results_file.name)
    except PermissionError:
        log.warning("Cannot write %s (is it open in Excel? close it and run again)", results_file.name)
    except Exception as exc:  # noqa: BLE001
        log.warning("Cannot update results table %s: %s", results_file.name, exc)


# --------------------------------------------------------------------------- #
# Tableaux affichés dans le terminal (console VS Code) à la fin de chaque exécution :
# une colonne par information, une ligne par exécution.
# --------------------------------------------------------------------------- #
_CONSOLE_TABLES = [
    ("PERFORMANCE", [
        ("Spec", "spec"), ("Step", "step"), ("Exigence", "exigence"), ("Model", "model"), ("Status", "status"),
        ("Items", "items"),
        ("In tokens", "input_tokens"), ("Out tokens", "output_tokens"), ("Total Token", "total_tokens_calc"),
        ("Prompt (s)", "prompt_time"), ("Gen (s)", "gen_time"), ("Total (s)", "total_time"),
        ("Total Minute", "total_minutes"), ("Tokens/s", "tokens_per_s"),
    ]),
    ("LLM RESOURCES", [
        ("CPU avg %", "cpu_avg"), ("CPU peak %", "cpu_peak"), ("RAM avg GB", "ram_avg"),
        ("RAM peak GB", "ram_peak"), ("GPU avg %", "gpu_avg"), ("GPU peak %", "gpu_peak"),
        ("GPU mem GB", "vram_peak"), ("LLM VRAM GB", "llm_vram_gb"), ("LLM RAM GB", "llm_ram_gb"),
        ("Placement", "placement"),
    ]),
    #--("MACHINE", [
    #--("CPU", "cpu"), ("Cores", "cores"), ("RAM total GB", "ram_total_gb"), ("GPU", "gpu"),
    #--]),
]


def _with_computed(record: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute les colonnes calculées affichées dans le terminal."""
    rec = dict(record)
    tin, tout = record.get("input_tokens"), record.get("output_tokens")
    if isinstance(tin, (int, float)) and isinstance(tout, (int, float)):
        rec["total_tokens_calc"] = int(tin + tout)            # Total Token = In tokens + Out tokens
    total_s = record.get("total_time")
    if isinstance(total_s, (int, float)):
        rec["total_minutes"] = f"{total_s / 60:.2f}"          # Total Minute = Total (s) / 60
    return rec


def _fmt(value: Any) -> str:
    if value in (None, ""):
        return "-"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def _render(title: str, columns, rows) -> str:
    """Tableau ASCII : une colonne par information, une ligne par enregistrement (+ éventuelle ligne TOTAL)."""
    headers = [h for h, _ in columns]
    body = [[_fmt(r.get(k)) for _, k in columns] for r in rows]
    widths = [max(len(h), *(len(line[i]) for line in body)) for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    fmt = lambda cells: "|" + "|".join(f" {c.center(w)} " for c, w in zip(cells, widths)) + "|"
    lines = [title, sep, fmt(headers), sep]
    for n, line in enumerate(body):
        if n == len(body) - 1 and rows[n].get("_total"):
            lines.append(sep)
        lines.append(fmt(line))
    lines.append(sep)
    return "\n".join(lines)


def _total_row(records) -> Dict[str, Any]:
    def total(key: str) -> float:
        return sum(r[key] for r in records if isinstance(r.get(key), (int, float)))

    def peak(key: str):
        values = [r[key] for r in records if isinstance(r.get(key), (int, float))]
        return max(values) if values else None

    ok = sum(1 for r in records if str(r.get("status", "")).upper().startswith("OK"))
    row = {"_total": True, "spec": "TOTAL", "step": f"{len(records)} calls", "exigence": "-",
           "model": records[0].get("model"), "status": f"{ok} OK / {len(records) - ok} FAILED",
           "items": int(total("items")),
           "input_tokens": int(total("input_tokens")), "output_tokens": int(total("output_tokens")),
           "prompt_time": round(total("prompt_time"), 1), "gen_time": round(total("gen_time"), 1),
           "total_time": round(total("total_time"), 1),
           "cpu_peak": peak("cpu_peak"), "ram_peak": peak("ram_peak"), "gpu_peak": peak("gpu_peak"),
           "vram_peak": peak("vram_peak")}
    row["tokens_per_s"] = round(total("output_tokens") / total("gen_time"), 1) if total("gen_time") else None
    return row


def print_final_summary(records, files=()) -> None:
    """Tableaux récapitulatifs affichés UNE SEULE FOIS, à la fin de l'exécution (après la génération de tous
    les fichiers) : une ligne par appel au LLM et une ligne TOTAL."""
    if not records:
        return
    rows = [_with_computed(r) for r in records]
    rows.append(_with_computed(_total_row(records)))
    title = f" EXECUTION SUMMARY - {records[0].get('model', '?')} "
    banner = "\n".join(["=" * (len(title) + 2), f"|{title}|", "=" * (len(title) + 2)])
    parts = [banner] + [_render(t, cols, rows) for t, cols in _CONSOLE_TABLES]
    if files:
        parts.append("Generated files:\n" + "\n".join(f"  - {f}" for f in files))
    errors = [f"  - {r.get('step')} {r.get('exigence') or ''}: {r['error']}" for r in records if r.get("error")]
    if errors:
        parts.append("Errors:\n" + "\n".join(errors))
    print("\n" + "\n\n".join(parts) + "\n", flush=True)
