"""Construction des prompts et lecture des réponses JSON du LLM."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Sequence, Tuple

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_FENCE_RE = re.compile(r"```(?:[A-Za-z]+)?[ \t]*\n(.*?)```", re.DOTALL)


def load_template(prompt_file: Path) -> str:
    if not prompt_file.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8")


def render(template: str, scalars: Dict[str, str], sections: Sequence[Tuple[str, str, str]] = ()) -> str:
    """Remplit un prompt.

    - `scalars` : {"{speccode}": "SPEC-FRN-001", "__MAX_STEPS__": "40"} remplacés partout.
    - `sections` : (marqueur, titre, contenu). Si le marqueur (ex. "{spec}") est dans le prompt, il est
      remplacé ; sinon le contenu est ajouté à la fin sous la forme  TITRE / <<< contenu >>>.

    Un seul passage de remplacement : un marqueur contenu dans une spécification n'est jamais
    réinterprété, et les accolades JSON du prompt ne posent pas de problème (pas de str.format).
    """
    values: Dict[str, str] = dict(scalars)
    appendix = []
    for marker, title, content in sections:
        if marker in template:
            values[marker] = content
        else:
            appendix.append(f"{title}\n<<<\n{content}\n>>>")

    if values:
        pattern = re.compile("|".join(re.escape(k) for k in sorted(values, key=len, reverse=True)))
        template = pattern.sub(lambda m: values[m.group(0)], template)

    return template.rstrip() + ("\n\n" + "\n\n".join(appendix) if appendix else "") + "\n"


def parse_json(text: str) -> Any:
    """Extrait un objet JSON d'une réponse (retire <think>, ```json ... ``` et le texte autour)."""
    text = _THINK_RE.sub("", text or "").strip()
    fenced = _FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    if not text:
        raise ValueError("empty model response")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    salvaged = _salvage_truncated(text)
    if salvaged is not None:
        return salvaged
    raise ValueError("model response is not valid JSON")


def _salvage_truncated(text: str) -> Any:
    """Réponse coupée par le plafond de tokens : garde les éléments complets déjà générés.
    Ferme le JSON après chacune des dernières accolades fermantes jusqu'à ce qu'il soit valide."""
    start = text.find("{")
    if start == -1:
        return None
    body = text[start:]
    ends = [i for i, ch in enumerate(body) if ch == "}"][-60:]
    for end in reversed(ends):
        for closer in ("]}", "]}}", "}", "]"):
            try:
                return json.loads(body[:end + 1] + closer)
            except json.JSONDecodeError:
                continue
    return None
