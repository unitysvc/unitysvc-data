"""Tests for the model-family logo registry and resolver.

The failure mode this file exists to catch is silent: a mis-attributed
family renders the wrong picture, never an error. So the expectation
table below is drawn from **real model ids** in the unitysvc-services-*
catalogs — including the ones that broke earlier drafts — rather than
from ids invented to match the patterns.
"""

from __future__ import annotations

import re

import pytest

from unitysvc_data import list_logo_families, logo_preset, resolve_family
from unitysvc_data.logos import normalise_model_id

# (model_id, expected family name or None). Real ids from the catalogs.
RESOLUTIONS: list[tuple[str, str | None]] = [
    # --- straightforward, one per registered family ---
    ("qwen3-235b-a22b", "qwen"),
    ("mistral-large-2411", "mistral"),
    ("glm-4.6", "glm"),
    ("deepseek-v4-pro", "deepseek"),
    ("llama-3.3-70b-instruct", "llama"),
    ("gemma-3-27b-it", "gemma"),
    ("kimi-k2-instruct", "kimi"),
    ("aya-expanse-32b", "aya"),
    ("command-a-plus-05-2026", "command"),
    ("gpt-oss-120b", "gpt-oss"),
    ("nemotron-4-340b", "nemotron"),
    ("minimax-m2", "minimax"),
    ("granite-3.3-8b", "granite"),
    ("claude-sonnet-4", "claude"),
    ("phi4-mini", "phi"),
    # --- vendor prefixes, single and stacked (Bedrock, regional Bedrock) ---
    ("anthropic.claude-sonnet-4", "claude"),
    ("us.anthropic.claude-sonnet-4", "claude"),
    ("zai.glm-4.6", "glm"),
    ("openai.gpt-oss-120b", "gpt-oss"),
    # --- org/model paths (Hugging Face) ---
    ("Qwen/Qwen3-235B-A22B", "qwen"),
    ("deepseek-ai/DeepSeek-V3.2", "deepseek"),
    # --- host-specific spellings ---
    ("zai-glm-4.7", "glm"),  # Cerebras uses a hyphen, so no prefix strip
    ("parasail-gpt-oss-20b", "gpt-oss"),
    ("llama-3.1-8b-instant", "llama"),
    # --- the "-stral" house all resolves to Mistral ---
    ("mixtral-8x7b", "mistral"),
    ("codestral-2501", "mistral"),
    ("devstral-small-2507", "mistral"),
    ("pixtral-12b", "mistral"),
    ("voxtral-mini", "mistral"),
    # --- Qwen's reasoning / vision lines ship under the Qwen mark ---
    ("qwq-32b", "qwen"),
    ("qvq-72b-preview", "qwen"),
    # --- derivatives: the base family's mark is the useful cue ---
    ("codellama", "llama"),
    ("hermes-3-llama-3.1-70b", "llama"),
    ("autoglm-phone-9b-multilingual", "glm"),  # AutoGLM is Zhipu's
    # --- regressions: these matched the WRONG family in earlier drafts ---
    ("everythinglm", None),  # Ollama model, unrelated to Zhipu GLM
    ("c4ai-aya-expanse-32b", "aya"),  # not command, despite the c4ai prefix
    ("c4ai-aya-vision-32b", "aya"),
    ("c4ai-command-r-08-2024", "command"),  # c4ai + command still resolves
    # --- generic capability words must not be claimed by any vendor ---
    ("embed-english-v3.0", None),
    ("embed-multilingual-v3.0", None),
    ("rerank-v3.5", None),
    ("bge-m3", None),
    ("all-minilm", None),
    # --- hosted GPT is not gpt-oss; bare "gpt" must not match ---
    ("gpt-4o", None),
    # --- long tail: no family, falls back to the provider logo ---
    ("aion-3.0", None),
    ("mimo-v2.5-pro", None),
    ("apertus-70b-instruct-2509", None),
    ("greg-2-ultra", None),
    ("cogito-671b-v2.1", None),
]


@pytest.mark.parametrize("model_id,expected", RESOLUTIONS)
def test_resolves_to_expected_family(model_id: str, expected: str | None) -> None:
    family = resolve_family(model_id)
    assert (family.name if family else None) == expected


@pytest.mark.parametrize("model_id,expected", RESOLUTIONS)
def test_preset_returns_that_family_url(model_id: str, expected: str | None) -> None:
    """logo_preset is the thin wrapper — it must agree with resolve_family."""
    url = logo_preset(model_id)
    if expected is None:
        assert url is None
    else:
        by_name = {f.name: f for f in list_logo_families()}
        assert url == by_name[expected].url


def test_family_name_addresses_entry_directly() -> None:
    """An exact family name resolves without going through the patterns,
    so a caller who knows the family never depends on the regexes."""
    for family in list_logo_families():
        assert resolve_family(family.name) is family


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("us.anthropic.claude-sonnet-4", "claude-sonnet-4"),
        ("anthropic.claude-sonnet-4", "claude-sonnet-4"),
        ("Qwen/Qwen3-235B-A22B", "qwen3-235b-a22b"),
        ("GPT-OSS-120B", "gpt-oss-120b"),
        ("plain-model", "plain-model"),
    ],
)
def test_normalise_model_id(raw: str, expected: str) -> None:
    assert normalise_model_id(raw) == expected


def test_registry_is_well_formed() -> None:
    families = list_logo_families()
    assert families, "registry must not be empty"
    names = [f.name for f in families]
    assert len(names) == len(set(names)), "family names must be unique"
    for family in families:
        assert family.patterns, f"{family.name} declares no patterns"
        assert family.owner, f"{family.name} declares no owner"
        assert family.url.startswith("https://"), f"{family.name} url must be https"


def test_urls_are_version_pinned() -> None:
    """An unpinned asset URL can change under us without any commit here.

    The whole point of centralising these is that the catalog's logos are
    reproducible from a released version of this package.
    """
    for family in list_logo_families():
        assert re.search(r"@\d+\.\d+\.\d+/", family.url), (
            f"{family.name}: {family.url} is not pinned to an exact version"
        )


def test_no_family_shadows_another() -> None:
    """No family's patterns may claim another family's own name.

    Order decides ties, which makes shadowing easy to introduce and
    invisible once introduced — it was exactly how every Aya model ended
    up wearing the Cohere command logo.
    """
    families = list_logo_families()
    for owner in families:
        for other in families:
            if owner is other:
                continue
            claimed = any(p.search(other.name) for p in owner.patterns)
            assert not claimed, (
                f"{owner.name!r} patterns claim {other.name!r}; whichever is declared first would silently win"
            )


def test_preset_rejects_unknown_options() -> None:
    with pytest.raises(ValueError, match="unknown option"):
        logo_preset("qwen", description="nope")


def test_preset_rejects_misspelled_default() -> None:
    """A typo must not silently mean "no fallback"."""
    with pytest.raises(ValueError, match="unknown option"):
        logo_preset("aion-3.0", defualt="https://example.test/x.svg")


class TestOverrideAndDefault:
    """One precedence chain: override → family match → default → None."""

    FALLBACK = "https://example.test/generic-llm.svg"

    def test_used_when_no_family_matches(self) -> None:
        assert logo_preset("aion-3.0", default=self.FALLBACK) == self.FALLBACK

    def test_a_match_wins_over_the_default(self) -> None:
        by_name = {f.name: f for f in list_logo_families()}
        assert logo_preset("qwen3-235b-a22b", default=self.FALLBACK) == by_name["qwen"].url

    def test_absent_default_still_returns_none(self) -> None:
        assert logo_preset("aion-3.0") is None

    def test_null_default_means_no_fallback(self) -> None:
        # What ``{{ fallback | default(none) }}`` renders to.
        assert logo_preset("aion-3.0", default=None) is None

    def test_empty_default_means_no_fallback(self) -> None:
        # ``{{ fallback | default("") }}`` — an empty logo URL would be worse
        # than none, since it creates a document pointing nowhere.
        assert logo_preset("aion-3.0", default="") is None

    def test_non_string_default_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be a URL string"):
            logo_preset("aion-3.0", default=["https://example.test/x.svg"])

    MINE = "https://example.test/mine.svg"

    def test_override_wins_over_a_matching_family(self) -> None:
        # The whole point: a seller pinning one model must not lose to the
        # registry, or the pin silently does nothing.
        assert logo_preset("qwen3-235b-a22b", override=self.MINE) == self.MINE

    def test_override_wins_over_the_default_too(self) -> None:
        assert (
            logo_preset("aion-3.0", override=self.MINE, default=self.FALLBACK) == self.MINE
        )

    def test_absent_override_falls_through_to_the_match(self) -> None:
        by_name = {f.name: f for f in list_logo_families()}
        # ``{{ logo | default(none) }}`` for a model the seller did not pin.
        assert logo_preset("qwen3-235b-a22b", override=None) == by_name["qwen"].url

    def test_empty_override_falls_through_too(self) -> None:
        by_name = {f.name: f for f in list_logo_families()}
        assert logo_preset("qwen3-235b-a22b", override="") == by_name["qwen"].url

    def test_override_applies_even_when_unmatched(self) -> None:
        assert logo_preset("aion-3.0", override=self.MINE) == self.MINE

    def test_non_string_override_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="'override' must be a URL string"):
            logo_preset("qwen", override={"url": self.MINE})

    def test_expands_through_core_sentinel(self) -> None:
        """The nested option forms a template emits, end to end."""
        core_utils = pytest.importorskip("unitysvc_core.utils")
        by_name = {f.name: f for f in list_logo_families()}

        unmatched = core_utils.expand_presets(
            {"logo": {"$logo_preset": {"name": "aion-3.0", "default": self.FALLBACK}}}
        )
        assert unmatched == {"logo": self.FALLBACK}

        matched = core_utils.expand_presets(
            {"logo": {"$logo_preset": {"name": "kimi-k2-instruct", "default": self.FALLBACK}}}
        )
        assert matched == {"logo": by_name["kimi"].url}

        # The one-line template idiom, both ways round: pinned and not.
        pinned = core_utils.expand_presets(
            {"logo": {"$logo_preset": {"name": "kimi-k2-instruct", "override": self.MINE}}}
        )
        assert pinned == {"logo": self.MINE}

        unpinned = core_utils.expand_presets(
            {"logo": {"$logo_preset": {"name": "kimi-k2-instruct", "override": None}}}
        )
        assert unpinned == {"logo": by_name["kimi"].url}


def test_preset_rejects_non_string() -> None:
    with pytest.raises(ValueError, match="expects a model id string"):
        logo_preset({"model": "qwen"})


def test_registered_in_preset_fns() -> None:
    """Sentinel expansion in unitysvc-core discovers presets through
    PRESET_FNS, so registration is what makes $logo_preset work at all."""
    from unitysvc_data import PRESET_FNS

    assert "logo_preset" in PRESET_FNS
    assert PRESET_FNS["logo_preset"]("deepseek-v4-pro") is not None


def test_expands_through_core_sentinel() -> None:
    """End-to-end: the shape a template actually emits."""
    core_utils = pytest.importorskip("unitysvc_core.utils")

    expanded = core_utils.expand_presets({"logo": {"$logo_preset": "kimi-k2-instruct"}})
    by_name = {f.name: f for f in list_logo_families()}
    assert expanded == {"logo": by_name["kimi"].url}

    unmatched = core_utils.expand_presets({"logo": {"$logo_preset": "aion-3.0"}})
    assert unmatched == {"logo": None}
