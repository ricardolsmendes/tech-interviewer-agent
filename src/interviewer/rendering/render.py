"""Jinja2 rendering of structured crew outputs into the project's HTML templates."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_STATUS_CLASSES = {
    "Met": "met",
    "Partial": "partial-cell",
    "Not met": "gap",
}

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["status_class"] = lambda status: _STATUS_CLASSES[status]
_env.globals["today"] = lambda: date.today().isoformat()


def render_to_file(template_name: str, context: dict, out_path: Path) -> None:
    """Render `template_name` with `context` and write the result to `out_path`."""
    template = _env.get_template(template_name)
    html = template.render(**context)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
