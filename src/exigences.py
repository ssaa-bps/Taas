"""Étape 1 : découper une spécification en exigences (exigence_prompt.txt)."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .mapping import Module, modules_text
from .prompts import parse_json, render
from .specs import Spec

log = logging.getLogger("gherkin")

STATUS_CODE = "generee"


@dataclass(frozen=True)
class Exigence:
    code: str            # SPEC-SUP-001
    libelle: str
    spec_code: str
    module_code: str
    status_code: str = STATUS_CODE
    module_technical: Optional[str] = None
    module_label: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {"exigenceCode": self.code, "libelle": self.libelle, "specCode": self.spec_code,
                "statusCode": self.status_code, "moduleCode": self.module_code}

    @property
    def number(self) -> str:
        """'001' dans un code comme SPEC-SUP-001."""
        return self.code.rsplit("-", 1)[-1]


def catalog_text(modules: Dict[str, Module]) -> str:
    return modules_text(modules)


def module_tag_name(module: Module) -> str:
    """Libellé de module utilisable dans un tag Gherkin (pas d'espace)."""
    return re.sub(r"\s+", "_", module.label.strip())


# --------------------------------------------------------------------------- #
# Prompt et lecture de la réponse
# --------------------------------------------------------------------------- #
def build_prompt(template: str, spec: Spec, modules: Dict[str, Module],
                 max_exigences: int = 12) -> str:
    return render(template, {"{speccode}": spec.code, "__MAX_EXIGENCES__": str(max_exigences)},
                  [("{catalogue}", "CATALOGUE DES MODULES", catalog_text(modules)),
                   ("{spec}", "SPÉCIFICATION", spec.as_prompt_text())])


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def parse_exigences(text: str, spec: Spec, modules: Dict[str, Module],
                    limit: int = 0) -> List[Exigence]:
    """Valide le JSON du modèle. Le code SPEC-<MODULE>-<NNN> est recalculé ici (séquentiel par module),
    plutôt que de faire confiance à la numérotation du modèle."""
    data: Any = parse_json(text)
    items = data.get("exigences") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("JSON has no 'exigences' list")

    counters: Dict[str, int] = {}
    seen = set()
    result: List[Exigence] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        libelle = str(item.get("libelle") or "").strip()
        module_code = str(item.get("moduleCode") or "").strip().lower()
        if not module_code:  # repli : déduit de "SPEC-SUP-001"
            parts = str(item.get("exigenceCode") or "").split("-")
            module_code = parts[1].lower() if len(parts) == 3 else ""
        if limit and len(result) >= limit:
            log.warning("Exigence limit reached (%d): remaining exigences ignored", limit)
            break
        if not libelle:
            log.warning("Exigence ignored: empty 'libelle'")
            continue
        if module_code not in modules:
            log.warning("Exigence ignored (module '%s' not in the catalog): %s", module_code, libelle[:80])
            continue
        if _norm(libelle) in seen:
            log.warning("Exigence ignored (duplicate): %s", libelle[:80])
            continue
        seen.add(_norm(libelle))
        counters[module_code] = counters.get(module_code, 0) + 1
        module = modules[module_code]
        result.append(Exigence(code=f"SPEC-{module_code.upper()}-{counters[module_code]:03d}",
                               libelle=libelle, spec_code=spec.code, module_code=module_code,
                               module_technical=module.technical, module_label=module.label))
    return result
