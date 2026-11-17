from pathlib import Path

import pytest

from interviewer.io_utils import (
    AmbiguousPdfError,
    NoPdfFoundError,
    list_pdfs,
    resolve_file,
)


def _touch_pdf(folder: Path, name: str) -> Path:
    path = folder / name
    path.write_bytes(b"%PDF-1.4\n")
    return path


def test_list_pdfs_ignores_non_pdfs(tmp_path: Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    (tmp_path / "notes.txt").write_text("not a pdf")
    assert [p.name for p in list_pdfs(tmp_path)] == ["a.pdf"]


def test_resolve_file_uses_explicit_path(tmp_path: Path) -> None:
    explicit = _touch_pdf(tmp_path, "explicit.pdf")
    other = tmp_path / "other"
    other.mkdir()
    result = resolve_file(other, "job description", explicit=explicit)
    assert result == explicit


def test_resolve_file_rejects_missing_explicit_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_file(tmp_path, "job description", explicit=tmp_path / "missing.pdf")


def test_resolve_file_auto_picks_single_candidate(tmp_path: Path) -> None:
    only = _touch_pdf(tmp_path, "only.pdf")
    assert resolve_file(tmp_path, "job description") == only


def test_resolve_file_raises_when_folder_is_empty(tmp_path: Path) -> None:
    with pytest.raises(NoPdfFoundError):
        resolve_file(tmp_path, "job description")


def test_resolve_file_raises_without_chooser_when_ambiguous(tmp_path: Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    _touch_pdf(tmp_path, "b.pdf")
    with pytest.raises(AmbiguousPdfError):
        resolve_file(tmp_path, "job description")


def test_resolve_file_defers_to_chooser_when_ambiguous(tmp_path: Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    b = _touch_pdf(tmp_path, "b.pdf")

    def chooser(candidates: list[Path], label: str) -> Path:
        assert label == "job description"
        return next(c for c in candidates if c.name == "b.pdf")

    assert resolve_file(tmp_path, "job description", chooser=chooser) == b
