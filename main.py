#!/usr/bin/env python3
"""Génère des scénarios Gherkin à partir de spécifications YAML, avec un LLM local (Ollama).

Pour chaque spécification : exigences -> dictionnaire de steps -> un fichier .feature par exigence.

Exemples :
    python main.py                                  # traite toutes les spécifications du dossier specs
    python main.py specs/client/fournisseurs.yaml   # traite une seule spécification
    python main.py --model ministral-3:8b           # change de modèle sans toucher à config.yaml
"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from pathlib import Path

from src.config import load_config
from src.generator import run
from src.logging_setup import setup_logging
from src.specs import collect_specs

DEFAULT_CONFIG = Path(__file__).resolve().parent / "config.yaml"


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Gherkin test cases from specification files.")
    parser.add_argument(
        "specs", nargs="*", type=Path,
        help="spec file(s) (.yaml, .yml, .docx, .pdf, .xlsx); default: all supported files in specs_dir",
    )
    parser.add_argument("-c", "--config", type=Path, default=DEFAULT_CONFIG, help="path to config.yaml")
    parser.add_argument("-m", "--model", help="override llm.model from the config")
    parser.add_argument("-l", "--language", help="override generation.gherkin_language (en, fr, ...)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if args.model:
        cfg = dataclasses.replace(cfg, model=args.model)
    if args.language:
        cfg = dataclasses.replace(cfg, gherkin_language=args.language)

    setup_logging(cfg.log_file)
    log = logging.getLogger("gherkin")

    spec_files = collect_specs(cfg, args.specs)
    if not spec_files:
        log.error("No specification file found (looked in %s)", cfg.specs_dir)
        return 2

    try:
        failures = run(cfg, spec_files)
    except KeyboardInterrupt:
        log.warning("Execution interrupted by user (Ctrl+C)")
        return 130
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 2

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
