"""Decorator-driven registry for preset sentinel callables.

Any function decorated with :func:`preset` is registered under its
``__name__`` in :data:`PRESET_FNS`, where downstream consumers
(notably ``unitysvc-core``'s ``load_data_file``) discover them. Adding
a new preset type — for example a ``schema_preset`` or
``policy_preset`` — is then purely a matter of decorating the
function and releasing a new ``unitysvc-data``; every consumer picks
it up automatically on the next install.

The decorator wraps each function with the **sentinel calling
convention**: the value in a ``{"$<name>": value}`` sentinel is
passed to the wrapped function, with the seller-facing flat form

    {"name": "<preset>", "<override>": ...}

transparently unpacked into ``fn(name, **overrides)``. Any other
shape (bare string, the internal ``{"$preset": ..., "$with": {...}}``
form that ``doc_preset`` understands, etc.) is forwarded verbatim.

The original (undecorated) function is returned unchanged so callers
can keep using it programmatically:

    >>> from unitysvc_data import doc_preset
    >>> doc_preset("s3_connectivity", is_public=False)
    {...}

The registry lookup uses the wrapped, sentinel-aware version.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

#: Registered preset callables keyed by sentinel name (without the
#: leading ``$``). Populated by :func:`preset` at import time.
PRESET_FNS: dict[str, Callable[[Any], Any]] = {}


def preset(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Register *fn* in :data:`PRESET_FNS` under its ``__name__``.

    The registered entry is a thin wrapper that unpacks the
    seller-facing flat sentinel form before delegating::

        {"name": "<preset>", "<override>": ...}   ->   fn("<preset>", **overrides)

    Any other value (bare string, dict without a string ``name`` key,
    etc.) is forwarded to ``fn`` unchanged — the underlying function
    is responsible for validating its own input.

    Returns the undecorated function so programmatic callers keep the
    original signature.
    """

    @functools.wraps(fn)
    def _sentinel_entrypoint(source: Any) -> Any:
        if isinstance(source, dict) and isinstance(source.get("name"), str):
            name = source["name"]
            overrides = {k: v for k, v in source.items() if k != "name"}
            return fn(name, **overrides)
        return fn(source)

    PRESET_FNS[fn.__name__] = _sentinel_entrypoint
    return fn
