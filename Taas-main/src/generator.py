"""Orchestration : spécification -> exigences -> dictionnaire -> un fichier .feature par exigence."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from ollama import Client, ResponseError

from . import dictionary
from .config import Config
from .exigences import Exigence, build_prompt as build_exigence_prompt, parse_exigences
from .llm import LLM
from .mapping import Module, load_modules
from .prompts import load_template, parse_json, render
from .report import print_final_summary
from .specs import Spec, load_spec

log = logging.getLogger("gherkin")

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_FENCE_RE = re.compile(r"```(?:gherkin|feature|cucumber)?[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE)
_FEATURE_RE = re.compile(
    r"^[ \t]*(Feature|Fonctionnalit[ée]|Funktionalit[äa]t|Caracter[ií]stica|Funcionalidad|Funzionalit[àa])\s*:",
    re.MULTILINE | re.IGNORECASE,
)
_SCENARIO_RE = re.compile(
    r"^[ \t]*(Scenario|Sc[ée]nario|Plan du sc[ée]nario|Szenario|Escenario|Scenario Outline)\b",
    re.MULTILINE | re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Réponse du modèle -> fichier .feature
# --------------------------------------------------------------------------- #
def extract_gherkin(text: Optional[str]) -> str:
    """Nettoie la réponse : retire <think>, les blocs ``` et tout ce qui précède l'en-tête du Feature."""
    text = _THINK_RE.sub("", text or "").strip()
    fenced = _FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    match = re.search(r"^[ \t]*(#\s*language\s*:|@)", text, re.MULTILINE | re.IGNORECASE)
    feature = _FEATURE_RE.search(text)
    starts = [m.start() for m in (match, feature) if m]
    return text[min(starts):].strip() if starts else text.strip()


def count_scenarios(gherkin: str) -> int:
    return len(_SCENARIO_RE.findall(gherkin))


def safe_model_name(model: str) -> str:
    """Nom de modèle utilisable dans un nom de fichier (':' et '/' interdits sous Windows)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", model).strip("-") or "model"


def scenario_id(exigence: Exigence) -> str:
    """Remplace le préfixe SPEC- par SC-."""
    return exigence.code.replace("SPEC-", "SC-", 1)


def tag_feature(gherkin: str, exigence: Exigence, module: Module) -> str:
    """Insère les tags calculés du scénario et du module avant la ligne Feature.
    Les tags éventuellement écrits par le modèle sont remplacés ; '# language:' reste en première ligne."""
    feature = _FEATURE_RE.search(gherkin)
    if not feature:
        raise ValueError("no 'Feature:' line in the model output")
    header = [ln for ln in gherkin[:feature.start()].splitlines() if ln.strip() and not ln.strip().startswith("@")]
    tags = f"@id:{scenario_id(exigence)} @module:{module.code} @exigence:{exigence.code}"
    return "\n".join(header + [tags]) + "\n" + gherkin[feature.start():].lstrip(" \t")


def build_gherkin_prompt(template: str, exigence: Exigence, spec: Spec, steps: Sequence[str], language: str,
                         max_scenarios: int = 4) -> str:
    """Les parties identiques pour toutes les exigences (règles, spécification, dictionnaire) viennent en premier,
    l'exigence en dernier : Ollama réutilise alors le début du prompt déjà traité (cache de préfixe)."""
    return render(
        template,
        {"{gherkin_language}": language, "__MAX_SCENARIOS__": str(max_scenarios)},
        [("{spec}", "SPECIFICATION (context only)", spec.as_prompt_text()),
         ("{steps}", "STEP DICTIONARY", "\n".join(f"- {s}" for s in steps) or "(empty)"),
         ("{exigence}", "REQUIREMENT", f"{exigence.code} : {exigence.libelle}")],
    )


# --------------------------------------------------------------------------- #
# Réponse JSON (nouveau gherkin_prompt.txt) -> texte Gherkin
# --------------------------------------------------------------------------- #
_KEYWORDS = {
    "en": {"feature": "Feature", "scenario": "Scenario", "given": "Given", "when": "When", "then": "Then",
           "and": "And", "but": "But"},
    "fr": {"feature": "Fonctionnalité", "scenario": "Scénario", "given": "Soit", "when": "Quand", "then": "Alors",
           "and": "Et", "but": "Mais"},
}


def scenarios_from_json(text: Optional[str]) -> Optional[dict]:
    """Retourne l'objet {"feature": ..., "scenarios": [...]} si la réponse est du JSON de ce format, sinon None."""
    if not text or '"scenarios"' not in text:
        return None
    try:
        data = parse_json(text)
    except ValueError:
        return None
    if isinstance(data, dict) and isinstance(data.get("scenarios"), list):
        return data
    return None


def json_to_gherkin(data: dict, language: str, max_scenarios: int) -> "tuple[str, List[str]]":
    """Convertit le JSON du modèle en texte Gherkin. Retourne (gherkin, nouvelles phrases proposées)."""
    kw = _KEYWORDS.get(language.lower(), _KEYWORDS["en"])
    lines: List[str] = []
    if language.lower() in _KEYWORDS and language.lower() != "en":
        lines.append(f"# language: {language.lower()}")
    lines.append(f"{kw['feature']}: {str(data.get('feature') or 'Feature').strip()}")
    new_phrases: List[str] = []
    count = 0
    for sc in data["scenarios"]:
        if not isinstance(sc, dict) or not isinstance(sc.get("steps"), list):
            continue
        steps = [st for st in sc["steps"] if isinstance(st, dict) and str(st.get("text") or "").strip()]
        if not steps:
            continue
        if count >= max_scenarios:
            break
        count += 1
        lines += ["", f"  {kw['scenario']}: {str(sc.get('name') or f'Scenario {count}').strip()}"]
        previous = ""
        for st in steps:
            key = str(st.get("keyword") or "").strip().lower()
            key = key if key in kw else "and"
            if key == previous and key in ("given", "when", "then"):
                key = "and"
            previous = key if key != "and" else previous
            lines.append(f"    {kw[key]} {str(st['text']).strip()}")
            if st.get("new_phrase"):
                new_phrases.append(str(st["new_phrase"]).strip())
    return "\n".join(lines), new_phrases


# --------------------------------------------------------------------------- #
# Les trois étapes
# --------------------------------------------------------------------------- #
def step_exigences(llm: LLM, cfg: Config, spec: Spec, modules: Dict[str, Module],
                   out_dir: Path) -> List[Exigence]:
    template = load_template(cfg.exigence_prompt_file)
    call = llm.ask("exigences", build_exigence_prompt(template, spec, modules, cfg.max_exigences),
                   spec=spec.stem, json_mode=True)
    try:
        exigences = parse_exigences(call.text, spec, modules, limit=cfg.max_exigences)
    except ValueError as exc:
        llm.finish(call, "FAILED", items=0, error=str(exc))
        raise
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "exigences.json"
    path.write_text(json.dumps({"exigences": [e.to_dict() for e in exigences]}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    log.info("Exigences found: %d (%s)", len(exigences), path.name)
    llm.finish(call, "OK" if exigences else "OK (no exigence)", items=len(exigences), output_file=path.name)
    return exigences


def step_dictionary(llm: LLM, cfg: Config, spec: Spec, exigences: Sequence[Exigence]) -> List[str]:
    """Ajoute à dictionary/steps.yaml les phrases manquantes ; retourne le dictionnaire à jour."""
    existing = dictionary.load_steps(cfg.steps_file)
    context = spec.as_prompt_text() + "\n" + "\n".join(e.libelle for e in exigences)
    template = load_template(cfg.dictionary_prompt_file)
    # Seules les phrases proches de la spécification sont envoyées au LLM (steps.yaml reste complet).
    shown = dictionary.select_relevant(existing, context, cfg.max_dictionary_steps)
    log.info("Dictionary sent to the LLM: %d of %d step(s)", len(shown), len(existing))
    prompt = dictionary.build_prompt(template, spec, exigences, shown, cfg.max_steps)
    call = llm.ask("dictionary", prompt, spec=spec.stem, json_mode=True)
    try:
        new_steps = dictionary.filter_new(dictionary.parse_steps(call.text), existing, cfg.max_steps)
    except ValueError as exc:
        llm.finish(call, "FAILED", items=0, error=str(exc))
        raise
    dictionary.append_steps(cfg.steps_file, new_steps)
    log.info("Dictionary: %d existing step(s), %d new step(s) added to %s", len(existing), len(new_steps),
             cfg.steps_file.name)
    llm.finish(call, "OK", items=len(new_steps), output_file=cfg.steps_file.name)
    # Même dictionnaire pour toutes les exigences de la spécification (cache de préfixe d'Ollama).
    return dictionary.select_relevant(existing, context, cfg.max_dictionary_steps) + new_steps


def step_gherkin(llm: LLM, cfg: Config, template: str, spec: Spec, exigence: Exigence, module: Module,
                 steps: Sequence[str], out_dir: Path) -> Path:
    prompt = build_gherkin_prompt(template, exigence, spec, steps, cfg.gherkin_language, cfg.max_scenarios)
    json_mode = '"scenarios"' in template        # le prompt demande du JSON : on force une sortie JSON valide
    call = llm.ask("gherkin", prompt, spec=spec.stem, exigence=exigence.code, json_mode=json_mode)
    new_phrases: List[str] = []
    try:
        data = scenarios_from_json(call.text)
        if data is not None:
            gherkin, new_phrases = json_to_gherkin(data, cfg.gherkin_language, cfg.max_scenarios)
        else:
            gherkin = extract_gherkin(call.text)
        scenarios = count_scenarios(gherkin)
        if scenarios == 0:
            raise ValueError("the model output does not look like valid Gherkin (no scenario found)")
        gherkin = tag_feature(gherkin, exigence, module)
    except ValueError as exc:
        log.warning("%s: %s", exigence.code, exc)
        llm.finish(call, "FAILED", items=0, error=str(exc))
        raise
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{exigence.code}.feature"
    path.write_text(gherkin + "\n", encoding="utf-8")
    if new_phrases:
        added = dictionary.filter_new(new_phrases, dictionary.load_steps(cfg.steps_file), cfg.max_steps)
        dictionary.append_steps(cfg.steps_file, added)
        if added:
            log.info("Dictionary: %d new step(s) proposed by the scenarios added to %s", len(added),
                     cfg.steps_file.name)
    llm.output_files.append(str(path.relative_to(cfg.output_dir)))
    log.info("Scenarios generated: %d", scenarios)
    log.info("Output file: %s", path.relative_to(cfg.output_dir))
    llm.finish(call, "OK", items=scenarios, output_file=str(path.relative_to(cfg.output_dir)))
    return path


# --------------------------------------------------------------------------- #
# Boucle principale
# --------------------------------------------------------------------------- #
def process_spec(llm: LLM, cfg: Config, spec_path: Path, modules: Dict[str, Module],
                 gherkin_template: str) -> int:
    """Traite une spécification. Retourne le nombre d'échecs."""
    spec = load_spec(spec_path)
    out_dir = cfg.output_dir / f"{spec.stem}_{safe_model_name(cfg.model)}"
    log.info("Starting Gherkin generation")
    log.info("Spec file: %s (%s)", spec_path.name, spec.code)

    exigences = step_exigences(llm, cfg, spec, modules, out_dir)
    if not exigences:
        log.warning("No functional requirement found in %s: nothing to generate", spec_path.name)
        return 0

    try:
        steps = step_dictionary(llm, cfg, spec, exigences)
    except ConnectionError:
        raise
    except (ResponseError, ValueError) as exc:  # le dictionnaire existant reste utilisable
        log.warning("Dictionary update failed (%s): continuing with the existing dictionary", exc)
        steps = dictionary.load_steps(cfg.steps_file)

    failures = 0
    for exigence in exigences:
        try:
            step_gherkin(llm, cfg, gherkin_template, spec, exigence, modules[exigence.module_code], steps, out_dir)
        except (ResponseError, ValueError) as exc:
            log.error("Gherkin generation failed for %s: %s", exigence.code, exc)
            failures += 1
    if failures == 0:
        log.info("Gherkin generation completed successfully")
    return failures


def run(cfg: Config, spec_files: Sequence[Path], client: Optional[Client] = None) -> int:
    """Traite chaque spécification. Retourne le nombre d'échecs."""
    modules = load_modules(cfg.modules_file)
    gherkin_template = load_template(cfg.gherkin_prompt_file)
    # Vérifie dès le début que tous les prompts existent (évite d'échouer après un long appel).
    load_template(cfg.exigence_prompt_file)
    load_template(cfg.dictionary_prompt_file)

    llm = LLM(cfg, client)
    failures = 0
    try:
        for spec_path in spec_files:
            try:
                failures += process_spec(llm, cfg, spec_path, modules, gherkin_template)
            except ConnectionError:
                log.error("Cannot reach Ollama at %s. Is the server running? (ollama serve)", cfg.host)
                return failures + 1  # inutile de continuer si le serveur est injoignable
            except ResponseError as exc:
                if getattr(exc, "status_code", None) == 404:
                    log.error("Model '%s' not found. Install it with: ollama pull %s", cfg.model, cfg.model)
                    return failures + 1
                log.error("Ollama error for %s: %s", spec_path.name, exc)
                failures += 1
            except (ValueError, FileNotFoundError) as exc:
                log.error("Generation failed for %s: %s", spec_path.name, exc)
                failures += 1
        return failures
    finally:
        # Tableau récapitulatif : affiché une seule fois, à la toute fin (même si l'exécution est interrompue).
        print_final_summary(llm.records, llm.output_files)
