"""PDF text extraction and input-file resolution for the input folders."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pypdf import PdfReader

Chooser = Callable[[list[Path], str], Path]


class NoPdfFoundError(RuntimeError):
    """Raised when a folder has no PDF files to pick from."""


class AmbiguousPdfError(RuntimeError):
    """Raised when a folder has multiple PDFs and no chooser was supplied."""

    def __init__(self, folder: Path, candidates: list[Path]):
        self.folder = folder
        self.candidates = candidates
        super().__init__(
            f"Multiple PDF files found in {folder}/: "
            f"{', '.join(p.name for p in candidates)}. Pick one explicitly."
        )


def list_pdfs(folder: Path) -> list[Path]:
    """Return PDF files directly inside `folder`, sorted by name."""
    return sorted(p for p in folder.glob("*.pdf") if p.is_file())


def resolve_file(
    folder: Path,
    label: str,
    explicit: Path | None = None,
    chooser: Chooser | None = None,
) -> Path:
    """Resolve which PDF to use for `label` (e.g. "job description").

    If `explicit` is given it is used as-is. Otherwise `folder` is scanned for PDFs:
    exactly one candidate is auto-selected, zero raises `NoPdfFoundError`, and more than
    one is handed to `chooser` (if given) or raises `AmbiguousPdfError`.
    """
    if explicit is not None:
        if not explicit.is_file():
            raise FileNotFoundError(f"{label} file not found: {explicit}")
        return explicit

    candidates = list_pdfs(folder)
    if not candidates:
        raise NoPdfFoundError(f"No PDF files found in {folder}/ for the {label}.")
    if len(candidates) == 1:
        return candidates[0]
    if chooser is not None:
        return chooser(candidates, label)
    raise AmbiguousPdfError(folder, candidates)


def extract_pdf_text(path: Path) -> str:
    """Extract and concatenate the text content of every page in a PDF."""
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()
