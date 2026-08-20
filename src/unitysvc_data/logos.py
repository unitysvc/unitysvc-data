"""Model-family logo resolution (unitysvc/unitysvc#1858).

A catalog row for ``parasail/qwen3-235b`` should show the Qwen mark, not
Parasail's. The seller-facing surface for that is an offering's ``logo``
field — a URL string that the platform converts to a ``Document`` with
``category=logo``, joined by ``service_mview`` as ``offering_logo``
alongside ``provider_logo``. Absent an offering logo, the provider's is
used, so "no match" is a valid, useful answer.

Why this isn't authored per service
-----------------------------------
The LLM catalogs generate their param files from ``update_params.py``,
which rewrites everything under ``services/specs/``. A logo written
there is destroyed by the next populate run, and the ``service.json``
sidecar can't hold one either (``ServiceStatus`` is ``extra="ignore"``,
so the key is silently dropped on upload). The durable spot is the
offering template, which the populate script never touches — and the
template can pass the model id into a preset because Jinja renders
before ``load_data_file`` expands preset sentinels::

    "logo": {{ {"$logo_preset": offering_name} | tojson }},

renders to ``{"$logo_preset": "deepseek-v4-pro"}``, which this module
resolves to a URL.

Why a registry rather than a function full of branches
------------------------------------------------------
The alternative was one function carrying both the conditions and the
URLs. Two things argue against it. Every other preset in this package is
data (``examples/`` scanned into ``_manifest.json``) with a thin lookup
on top, and adding a model family should be the same kind of change — a
data edit, reviewable as data. And the URL and the patterns that select
it belong in one place: split across a regex table and a URL table they
drift, and the drift is silent because a mis-selected logo is a wrong
picture, never an error.

So the family table lives in :mod:`logos.toml` and this module is only
the matcher. Adding a family touches no code.

Logos are *not* modelled as ``examples/`` presets, despite ending up as
Documents at the backend. A preset record there is a body file plus a
mime type plus a category; a logo is a URL with no body. Forcing one
through the other's shape would mean bending the ``Preset`` dataclass,
its mime/extension validation, and the manifest builder to carry a
record type that shares none of their fields.
"""

from __future__ import annotations

import re
import tomllib
from functools import lru_cache
from importlib.resources import files as _files
from typing import Any, NamedTuple

from ._registry import preset

#: Vendor prefixes that upstreams staple onto a model id. Bedrock ships
#: ``anthropic.claude-sonnet-4`` and ``zai.glm-4.6``; regional Bedrock
#: ids add ``us.`` / ``eu.`` / ``apac.`` on top. Stripped before matching
#: so a family pattern doesn't have to enumerate every host's spelling.
_VENDOR_PREFIX = re.compile(r"^(?:us|eu|apac)\.|^(?:anthropic|amazon|meta|mistral|cohere|ai21|deepseek|qwen|zai)\.")


class LogoFamily(NamedTuple):
    """One resolved registry entry."""

    name: str
    owner: str
    url: str
    patterns: tuple[re.Pattern[str], ...]


def normalise_model_id(model_id: str) -> str:
    """Reduce a model id to the form :data:`logos.toml` patterns match against.

    Lowercases, keeps only the last path segment (``Qwen/Qwen3-8B`` is a
    Hugging Face org/model pair), and strips vendor prefixes — repeatedly,
    since regional Bedrock ids carry two (``us.anthropic.claude-...``).

    >>> normalise_model_id("us.anthropic.claude-sonnet-4")
    'claude-sonnet-4'
    >>> normalise_model_id("Qwen/Qwen3-235B-A22B")
    'qwen3-235b-a22b'
    """
    base = str(model_id).split("/")[-1].lower()
    while True:
        stripped = _VENDOR_PREFIX.sub("", base)
        if stripped == base:
            return base
        base = stripped


@lru_cache(maxsize=1)
def _registry() -> tuple[LogoFamily, ...]:
    """Parse and compile logos.toml once per process.

    Compiling every pattern at load turns a typo into an immediate
    ``re.error`` naming the family, instead of a pattern that quietly
    never matches and a logo that quietly never appears.
    """
    raw = _files(__package__).joinpath("logos.toml").read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))

    families: list[LogoFamily] = []
    seen: set[str] = set()
    for entry in data.get("family", []):
        name = entry["name"]
        if name in seen:
            raise ValueError(f"logos.toml: duplicate family {name!r}")
        seen.add(name)
        try:
            patterns = tuple(re.compile(p) for p in entry["patterns"])
        except re.error as exc:
            raise ValueError(f"logos.toml: bad pattern in family {name!r}: {exc}") from exc
        if not patterns:
            raise ValueError(f"logos.toml: family {name!r} declares no patterns")
        families.append(LogoFamily(name=name, owner=entry["owner"], url=entry["url"], patterns=patterns))
    if not families:
        raise ValueError("logos.toml: registry is empty")
    return tuple(families)


def resolve_family(model_id: str) -> LogoFamily | None:
    """Return the family a model id belongs to, or ``None``.

    An exact family name wins over pattern matching, so ``"qwen"``
    addresses the Qwen entry directly and a caller who knows the family
    never depends on the regexes. Otherwise the first entry with a
    matching pattern wins, in file order.
    """
    base = normalise_model_id(model_id)
    registry = _registry()

    for family in registry:
        if family.name == base:
            return family

    for family in registry:
        if any(pattern.search(base) for pattern in family.patterns):
            return family
    return None


def list_logo_families() -> list[LogoFamily]:
    """Every registered family, in file order. For tooling and tests."""
    return list(_registry())


@preset
def logo_preset(source: Any, **kwargs: Any) -> str | None:
    """Return the logo URL for a model id, or ``None`` when unmatched.

    Seller-facing usage, as a ``$logo_preset`` sentinel in a parsed
    ``offering.json`` (or in the ``.j2`` that renders one)::

        {"$logo_preset": "deepseek-v4-pro"}    # matched by pattern
        {"$logo_preset": "qwen"}               # addressed by family name

    Returning ``None`` is the designed outcome for an unrecognised model,
    not a failure: the resulting ``"logo": null`` creates no document and
    is dropped at the API boundary (``ServiceOfferingData`` is
    ``extra="ignore"`` and has no ``logo`` field), leaving the provider
    logo in place. Callers therefore need no conditional around the key.

    Unlike :func:`doc_preset` this takes no overrides — the value is a
    single URL, so there is nothing to override. It must be the sentinel
    dict's only key: ``expand_presets`` raises on sibling keys beside a
    preset that expands to a scalar.
    """
    if kwargs:
        raise ValueError(
            f"logo_preset takes no overrides (got {sorted(kwargs)!r}); it resolves to a "
            f"single URL. Pass the model id alone: {{'$logo_preset': '<model-id>'}}."
        )
    if not isinstance(source, str):
        raise ValueError(f"logo_preset expects a model id string, got {type(source).__name__}: {source!r}")
    family = resolve_family(source)
    return family.url if family else None
