"""Spécifications d'entrée : fichiers YAML, DOCX, PDF et XLSX du dossier specs/client.

Format YAML :
    code: SPEC-FRN-001        # obligatoire, devient {speccode} dans exigence_prompt.txt
    titre: Gestion du cycle fournisseur   # facultatif
    contenu: |                # obligatoire (alias acceptés : content, description)
      texte de la spécification...
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Sequence
from zipfile import BadZipFile

import yaml

from .config import Config

SPEC_EXTENSIONS = {".yaml", ".yml", ".docx", ".pdf", ".xlsx"}
_CONTENT_KEYS = ("contenu", "content", "description")


@dataclass(frozen=True)
class Spec:
    code: str
    title: str
    content: str
    path: Path

    @property
    def stem(self) -> str:
        return self.path.stem

    def as_prompt_text(self) -> str:
        return f"{self.title}\n\n{self.content}" if self.title else self.content


def load_spec(path: Path) -> Spec:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return _load_yaml_spec(path)
    if suffix == ".docx":
        title, content = _load_docx(path)
    elif suffix == ".pdf":
        title, content = _load_pdf(path)
    elif suffix == ".xlsx":
        title, content = _load_xlsx(path)
    else:
        raise ValueError(f"{path.name}: unsupported specification format '{suffix or '(no extension)'}'")

    if not content.strip():
        raise ValueError(f"{path.name}: no readable text found in the specification")
    code = re.sub(r"[^A-Za-z0-9]+", "-", path.stem).strip("-").upper() or "DOCUMENT"
    return Spec(code=f"SPEC-{code}", title=title, content=content.strip(), path=path)


def _load_yaml_spec(path: Path) -> Spec:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path.name}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name}: expected a YAML mapping with 'code' and 'contenu'")

    code = str(raw.get("code") or "").strip()
    if not code:
        raise ValueError(f"{path.name}: 'code' is required (e.g. SPEC-FRN-001)")
    content = next((str(raw[k]).strip() for k in _CONTENT_KEYS if raw.get(k)), "")
    if not content:
        raise ValueError(f"{path.name}: 'contenu' is required and must not be empty")
    return Spec(code=code, title=str(raw.get("titre") or raw.get("title") or "").strip(),
                content=content, path=path)


def _load_docx(path: Path) -> tuple[str, str]:
    try:
        from docx import Document
        from docx.opc.exceptions import PackageNotFoundError
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise ValueError("DOCX support requires python-docx; install it with 'pip install python-docx'") from exc

    try:
        document = Document(str(path))
    except (PackageNotFoundError, BadZipFile) as exc:
        raise ValueError(f"{path.name}: invalid or corrupted DOCX file") from exc
    blocks = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            text = Paragraph(child, document).text.strip()
            if text:
                blocks.append(text)
        elif child.tag.endswith("}tbl"):
            table = Table(child, document)
            for row in table.rows:
                cells = [cell.text.strip().replace("\n", " / ") for cell in row.cells]
                if any(cells):
                    blocks.append(" | ".join(cells))
    return path.stem, "\n".join(blocks)


def _load_pdf(path: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        raise ValueError("PDF support requires pypdf; install it with 'pip install pypdf'") from exc

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ValueError(f"{path.name}: encrypted PDFs are not supported")
        pages = [page.extract_text() or "" for page in reader.pages]
    except PdfReadError as exc:
        raise ValueError(f"{path.name}: invalid or corrupted PDF file: {exc}") from exc
    return path.stem, "\n\n".join(text.strip() for text in pages if text.strip())


def _load_xlsx(path: Path) -> tuple[str, str]:
    from openpyxl.utils.exceptions import InvalidFileException

    try:
        from openpyxl import load_workbook
        workbook = load_workbook(path, read_only=True, data_only=True)
        blocks = []
        try:
            for sheet in workbook.worksheets:
                rows = []
                for row in sheet.iter_rows(values_only=True):
                    values = [str(value).strip() if value is not None else "" for value in row]
                    if any(values):
                        rows.append(" | ".join(values))
                if rows:
                    blocks.append(f"Feuille : {sheet.title}\n" + "\n".join(rows))
        finally:
            workbook.close()
    except (InvalidFileException, BadZipFile) as exc:
        raise ValueError(f"{path.name}: invalid or corrupted XLSX file: {exc}") from exc
    return path.stem, "\n\n".join(blocks)


def collect_specs(cfg: Config, explicit: Sequence[Path]) -> List[Path]:
    """Fichiers donnés en argument, sinon toutes les spécifications prises en charge."""
    if explicit:
        return [Path(p) for p in explicit]
    if not cfg.specs_dir.is_dir():
        return []
    return sorted(f for f in cfg.specs_dir.rglob("*") if f.is_file() and f.suffix.lower() in SPEC_EXTENSIONS)
