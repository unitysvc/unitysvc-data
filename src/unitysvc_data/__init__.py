"""Standard examples and presets for UnitySVC data packages.

Pure-data package: ships example files under ``examples/`` organised by
gateway and preset family, preset factories that return populated
document records, and a JSON sentinel walker the sellers SDK calls at
upload time. The same machinery is intended to serve other parts of the
platform that need versioned, named references to bundled content.

Preferred (preset-name) API:

- :func:`doc_preset` — return a full document record for a preset,
  from a bare name or a ``{"$preset": ..., "$with": {...}}`` sentinel.
- :func:`file_preset` — return the raw UTF-8 content of a preset's
  bundled example file.
- :func:`list_presets` — enumerate every registered preset name
  (versioned + aliases).
- :data:`PRESETS` — mapping of preset name → factory function.
- :data:`ALIASES` — mapping of version-less family name → latest
  versioned preset name.
- :data:`MANIFEST` — parsed ``_manifest.json`` content.
- :data:`OVERRIDABLE` — fields that may be overridden in ``$with``.
- :func:`register_jinja_globals` — expose every preset factory as a
  Jinja2 global (for generated repos that render ``listing.json.j2``).

Low-level (path-based) API — prefer the preset API above unless you
specifically need to address files by their on-disk layout:

- :func:`example_path`, :func:`read_example`, :func:`list_examples` —
  resolve and read bundled example files by their path under
  ``examples/``. These break if we ever reorganise the tree; preset
  names don't.
"""

from __future__ import annotations

from importlib.resources import files as _files
from pathlib import Path

from ._version import __version__

_ROOT = _files(__name__).joinpath("examples")


def example_path(name: str) -> Path:
    """Return an absolute filesystem path for the bundled example *name*.

    **Low-level.** Prefer :func:`file_preset` and :func:`doc_preset`
    for anything that can key off a preset name — those are stable
    across any future reorganisation of ``examples/``.

    *name* is a path relative to ``examples/`` (e.g.
    ``"s3/connectivity/connectivity-v1.py.j2"``). Raises
    :class:`FileNotFoundError` if the file is not part of the
    installed package.
    """
    target = _ROOT.joinpath(name)
    if not target.is_file():
        raise FileNotFoundError(f"Unknown example: {name!r}")
    return Path(str(target))


def read_example(name: str) -> str:
    """Read the raw UTF-8 content of a bundled example by path.

    **Low-level.** See :func:`example_path` for the name contract and
    why :func:`file_preset` is usually the right choice.
    """
    return example_path(name).read_text(encoding="utf-8")


def list_examples() -> list[str]:
    """Return every bundled example filename, relative to ``examples/``.

    **Low-level.** For enumerating presets by name, use
    :func:`list_presets`. This function exposes on-disk paths
    (including the gateway/family structure), which is rarely what a
    consumer wants.

    README files and hidden files are excluded.
    """
    root = Path(str(_ROOT))
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.name != "README.md"
        and not path.name.startswith(".")
    )


# Imported last so presets.py can compute its own _EXAMPLES_ROOT without
# reaching back into this module while __init__ is still loading.
# The ``from .presets import ...`` line also runs the ``@preset``
# decorators that populate :data:`PRESET_FNS` — so downstream consumers
# (notably ``unitysvc_core.load_data_file``) can enumerate every
# decorated preset without knowing their names ahead of time.
from ._registry import PRESET_FNS, preset  # noqa: E402  (placement is deliberate)
from .presets import (  # noqa: E402  (placement is deliberate)
    ALIASES,
    MANIFEST,
    OVERRIDABLE,
    PRESETS,
    doc_preset,
    file_preset,
    list_presets,
    register_jinja_globals,
)

__all__ = [
    "__version__",
    # Preferred preset API.
    "doc_preset",
    "file_preset",
    "list_presets",
    "PRESETS",
    "ALIASES",
    "MANIFEST",
    "OVERRIDABLE",
    "register_jinja_globals",
    # Decorator-driven registry — downstream tools enumerate these to
    # discover every preset type without hard-coding function names.
    "preset",
    "PRESET_FNS",
    # Low-level path-based API.
    "example_path",
    "read_example",
    "list_examples",
]
