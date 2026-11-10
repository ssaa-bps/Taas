"""Catalogue unique des modules fonctionnels lu depuis mapping/modules.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass(frozen=True)
class Module:
    code: str
    technical: Optional[str]
    label: str


def _clean(value: object) -> Optional[str]:
    text = "" if value is None else str(value).strip()
    return None if not text or text.lower() in ("null", "none") else text


def load_modules(path: Path) -> Dict[str, Module]:
    if not path.is_file():
        raise FileNotFoundError(f"Module catalogue not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    modules: Dict[str, Module] = {}
    for item in raw.get("modules") or []:
        code = (_clean(item.get("Functional Module")) or "").lower()
        if not code:
            continue
        modules[code] = Module(code=code, technical=_clean(item.get("Technical module")),
                               label=_clean(item.get("Label (EN)")) or code)
    if not modules:
        raise ValueError(f"{path.name}: no module defined")
    return modules


def modules_text(modules: Dict[str, Module]) -> str:
    """Une ligne par module : code = libellé [module technique]."""
    return "\n".join(f"- {module.code} = {module.label}" +
                     (f" [{module.technical}]" if module.technical else "")
                     for module in modules.values())
