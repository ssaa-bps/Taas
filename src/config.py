"""Chargement de la configuration (config.yaml)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(frozen=True)
class Config:
    # --- LLM ---
    model: str
    host: str
    temperature: float
    num_ctx: int
    num_predict: Optional[int]
    think: Optional[bool]
    keep_alive: str
    timeout: float
    # --- Génération ---
    gherkin_language: str
    max_steps: int
    max_exigences: int
    max_scenarios: int
    max_dictionary_steps: int
    num_predict_exigences: int
    num_predict_dictionary: int
    num_predict_gherkin: int
    # --- Chemins ---
    exigence_prompt_file: Path
    dictionary_prompt_file: Path
    gherkin_prompt_file: Path
    steps_file: Path
    modules_file: Path
    specs_dir: Path
    output_dir: Path
    log_file: Path
    results_file: Path

    def ollama_options(self, step: str = "") -> Dict[str, Any]:
        """Options envoyées à Ollama (paramètre `options` de chat).
        Chaque étape a son propre plafond de tokens générés : sur CPU, la génération coûte ~3 tokens/s."""
        options: Dict[str, Any] = {
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
        }
        cap = {"exigences": self.num_predict_exigences, "dictionary": self.num_predict_dictionary,
               "gherkin": self.num_predict_gherkin}.get(step) or self.num_predict
        if cap is not None:
            options["num_predict"] = cap
        return options


def load_config(path: Path) -> Config:
    """Lit le fichier YAML et retourne un objet Config."""
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    llm = raw.get("llm") or {}
    gen = raw.get("generation") or {}
    paths = raw.get("paths") or {}
    base = path.parent

    def resolve(key: str, default: str) -> Path:
        value = Path(str(paths.get(key, default)))
        return value if value.is_absolute() else (base / value)

    model = str(llm.get("model", "")).strip()
    if not model:
        raise ValueError("config.yaml: 'llm.model' is required")

    think = llm.get("think", None)
    if think is not None:
        think = bool(think)

    num_predict = llm.get("num_predict", None)
    if num_predict is not None:
        num_predict = int(num_predict)

    max_steps = int(gen.get("max_steps", 40))
    if max_steps < 1:
        raise ValueError("config.yaml: 'generation.max_steps' must be >= 1")

    def positive(key: str, default: int) -> int:
        value = int(gen.get(key, default))
        if value < 1:
            raise ValueError(f"config.yaml: 'generation.{key}' must be >= 1")
        return value

    def cap(key: str, default: int) -> int:
        return int(llm.get(key, default))

    return Config(
        model=model,
        host=str(llm.get("host", "http://127.0.0.1:11434")),
        temperature=float(llm.get("temperature", 0.2)),
        num_ctx=int(llm.get("num_ctx", 16384)),
        num_predict=num_predict,
        think=think,
        keep_alive=str(llm.get("keep_alive", "30m")),
        timeout=float(llm.get("timeout", 1800)),
        gherkin_language=str(gen.get("gherkin_language", "en")).strip() or "en",
        max_steps=max_steps,
        max_exigences=positive("max_exigences", 12),
        max_scenarios=positive("max_scenarios", 4),
        max_dictionary_steps=positive("max_dictionary_steps", 60),
        num_predict_exigences=cap("num_predict_exigences", 1200),
        num_predict_dictionary=cap("num_predict_dictionary", 800),
        num_predict_gherkin=cap("num_predict_gherkin", 1500),
        exigence_prompt_file=resolve("exigence_prompt_file", "packages/scenario-generator/exigence_prompt.txt"),
        dictionary_prompt_file=resolve("dictionary_prompt_file", "packages/scenario-generator/dictionary_prompt.txt"),
        gherkin_prompt_file=resolve("gherkin_prompt_file", "packages/scenario-generator/gherkin_prompt.txt"),
        steps_file=resolve("steps_file", "dictionary/steps.yaml"),
        modules_file=resolve("modules_file", "mapping/modules.yaml"),
        specs_dir=resolve("specs_dir", "specs"),
        output_dir=resolve("output_dir", "scenarios/client"),
        log_file=resolve("log_file", "logs/execution.log"),
        results_file=resolve("results_file", "logs/executions.xlsx"),
    )
