import pathlib

import pytest

from interviewer import io_utils


def _touch_pdf(folder: pathlib.Path, name: str) -> pathlib.Path:
    path = folder / name
    path.write_bytes(b"%PDF-1.4\n")
    return path


def test_list_pdfs_ignores_non_pdfs(tmp_path: pathlib.Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    (tmp_path / "notes.txt").write_text("not a pdf")
    assert [p.name for p in io_utils.list_pdfs(tmp_path)] == ["a.pdf"]


def test_resolve_file_uses_explicit_path(tmp_path: pathlib.Path) -> None:
    explicit = _touch_pdf(tmp_path, "explicit.pdf")
    other = tmp_path / "other"
    other.mkdir()
    result = io_utils.resolve_file(other, "job description", explicit=explicit)
    assert result == explicit


def test_resolve_file_rejects_missing_explicit_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(FileNotFoundError):
        io_utils.resolve_file(tmp_path, "job description", explicit=tmp_path / "missing.pdf")


def test_resolve_file_auto_picks_single_candidate(tmp_path: pathlib.Path) -> None:
    only = _touch_pdf(tmp_path, "only.pdf")
    assert io_utils.resolve_file(tmp_path, "job description") == only


def test_resolve_file_raises_when_folder_is_empty(tmp_path: pathlib.Path) -> None:
    with pytest.raises(io_utils.NoPdfFoundError):
        io_utils.resolve_file(tmp_path, "job description")


def test_resolve_file_raises_without_chooser_when_ambiguous(tmp_path: pathlib.Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    _touch_pdf(tmp_path, "b.pdf")
    with pytest.raises(io_utils.AmbiguousPdfError):
        io_utils.resolve_file(tmp_path, "job description")


def test_resolve_file_defers_to_chooser_when_ambiguous(tmp_path: pathlib.Path) -> None:
    _touch_pdf(tmp_path, "a.pdf")
    b = _touch_pdf(tmp_path, "b.pdf")

    def chooser(candidates: list[pathlib.Path], label: str) -> pathlib.Path:
        assert label == "job description"
        return next(c for c in candidates if c.name == "b.pdf")

    assert io_utils.resolve_file(tmp_path, "job description", chooser=chooser) == b
