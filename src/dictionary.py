"""Étape 2 : dictionnaire de steps (dictionary/steps.yaml) complété avec dictionary_prompt.txt."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Sequence

import yaml

from .exigences import Exigence
from .prompts import parse_json, render
from .specs import Spec

log = logging.getLogger("gherkin")

# Une phrase du dictionnaire ne commence jamais par un mot-clé Gherkin ni par "je sais que".
_KEYWORD_RE = re.compile(
    r"^(given|when|then|and|but|soit|étant donné|etant donne|quand|lorsque|alors|et|mais)\b|^\*|^je sais que\b",
    re.IGNORECASE,
)
_PARAM_RE = re.compile(r"\{[^{}]*\}")


def load_steps(path: Path) -> List[str]:
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    steps = raw.get("steps") if isinstance(raw, dict) else raw
    return [str(s).strip() for s in (steps or []) if str(s).strip()]


def _key(step: str) -> str:
    """Forme de comparaison : sans casse, apostrophes unifiées, paramètres {x} ramenés à {}."""
    step = step.replace("’", "'").replace('"', "'")
    return re.sub(r"\s+", " ", _PARAM_RE.sub("{}", step).casefold()).strip()


def _matches_template(step: str, template: str) -> bool:
    """Indique si `step` est une instanciation concrète d'un modèle paramétré."""
    template = re.sub(r"\s+", " ", template.replace("’", "'").replace('"', "'")).strip()
    step = re.sub(r"\s+", " ", step.replace("’", "'").replace('"', "'")).strip()
    parameters = list(_PARAM_RE.finditer(template))
    if not parameters:
        return False

    pattern = []
    position = 0
    for parameter in parameters:
        pattern.append(re.escape(template[position:parameter.start()]))
        pattern.append(".+?")
        position = parameter.end()
    pattern.append(re.escape(template[position:]))
    return re.fullmatch("".join(pattern), step, re.IGNORECASE) is not None


_WORD_RE = re.compile(r"[a-zà-öø-ÿ0-9]{4,}", re.IGNORECASE)
_STOP = {"avec", "dans", "pour", "sont", "être", "elle", "leur", "cette", "plus", "sans", "dont", "tout",
         "that", "with", "from", "this", "have", "will", "must", "when", "then", "given", "peut", "peuvent",
         "tant", "utilisateur", "doit", "doivent", "ainsi", "lorsque", "aussi", "chaque"}


def _words(text: str) -> set:
    text = _PARAM_RE.sub(" ", text)
    return {w.casefold() for w in _WORD_RE.findall(text)} - _STOP


def select_relevant(steps: Sequence[str], context: str, limit: int) -> List[str]:
    """Réduit le dictionnaire envoyé au LLM aux `limit` phrases les plus proches du contexte (spécification +
    exigences). Le fichier steps.yaml n'est pas modifié. Le résultat ne dépend que de `context` : il est donc
    identique pour tous les appels d'une même spécification, ce qui permet à Ollama de réutiliser le début du
    prompt déjà traité (cache de préfixe) au lieu de le retraiter à chaque exigence.
    Les phrases historiques « je sais que ... » sont ignorées. Ordre du fichier conservé."""
    usable = [(i, s) for i, s in enumerate(steps) if not _KEYWORD_RE.match(s.strip())]
    if len(usable) <= limit:
        return [s for _, s in usable]
    ctx = _words(context)
    def score(item):
        return -(2 * len(_words(item[1]) & ctx) + ("{" in item[1]))
    scored = sorted(usable, key=lambda item: (score(item), item[0]))[:limit]
    return [s for _, s in sorted(scored)]


def filter_new(candidates: Sequence[object], existing: Sequence[str], limit: int) -> List[str]:
    """Garde les phrases valides et réellement nouvelles, sans doublon ni variante instanciée d'un modèle."""
    known = {_key(s) for s in existing}
    templates = [s for s in existing if _PARAM_RE.search(s)]
    kept: List[str] = []
    for cand in candidates:
        step = str(cand).strip() if isinstance(cand, str) else ""
        if not step or _KEYWORD_RE.match(step):
            continue
        if _key(step) in known or any(_matches_template(step, template) for template in templates):
            continue
        known.add(_key(step))
        kept.append(step)
        if _PARAM_RE.search(step):
            templates.append(step)
        if len(kept) >= limit:
            break
    return kept


def build_prompt(template: str, spec: Spec, exigences: Sequence[Exigence], existing: Sequence[str],
                 max_steps: int) -> str:
    description = f"{spec.title}\n" if spec.title else ""
    description += "\n".join(
        f"- {e.libelle}" + (f" [module : {e.module_label} ({e.module_code})]" if e.module_label else "")
        for e in exigences)
    existing_text = "\n".join(f"- {s}" for s in existing) if existing else "(dictionnaire vide)"
    return render(
        template,
        {"__MAX_STEPS__": str(max_steps)},
        [("{description}", "DESCRIPTION FONCTIONNELLE", description),
         ("{dictionnaire}", "DICTIONNAIRE EXISTANT", existing_text)],
    )


def parse_steps(text: str) -> List[object]:
    data = parse_json(text)
    steps = data.get("steps") if isinstance(data, dict) else data
    if not isinstance(steps, list):
        raise ValueError("JSON has no 'steps' list")
    return steps


def append_steps(path: Path, steps: Sequence[str]) -> None:
    """Ajoute les phrases à la fin du fichier sans réécrire (ni reformater) les phrases existantes."""
    if not steps:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        content = path.read_text(encoding="utf-8")
        if content and not content.endswith("\n"):
            content += "\n"
    else:
        content = "steps:\n"
    for step in steps:
        content += yaml.safe_dump([step], allow_unicode=True, default_flow_style=False, width=10 ** 6)
    path.write_text(content, encoding="utf-8")
