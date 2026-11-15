"""HTML Artifacts and UI generators."""

import importlib
import os
import threading
from typing import Optional

from src.ui import html_generator

_RELOAD_LOCK = threading.Lock()
_last_html_mtime_ns: Optional[int] = None


def render_latest_html(form_type: Optional[str] = "hub") -> str:
    """Return HTML for form_type, reloading html_generator if its file changed on disk."""
    global _last_html_mtime_ns
    path = getattr(html_generator, "__file__", None)
    if path:
        with _RELOAD_LOCK:
            try:
                mtime_ns = os.stat(path).st_mtime_ns
            except OSError:
                mtime_ns = None
            if mtime_ns is not None:
                if _last_html_mtime_ns is None:
                    _last_html_mtime_ns = mtime_ns
                elif mtime_ns != _last_html_mtime_ns:
                    importlib.reload(html_generator)
                    _last_html_mtime_ns = mtime_ns
    return html_generator.generate_html(form_type)
