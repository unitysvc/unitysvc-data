"""The request templates the Test Request playground starts a request from.

The playground picks a document by the capability its ``applies_to`` names, then
the first entry in it that names the format the customer chose
(unitysvc/unitysvc#2514, #2515). So a template is one document per capability,
holding one ``{"format", "body"}`` entry per request format.

This module is about the DATA: what the shipped documents contain and what they
were derived from. The checks that keep a document reachable are in
``tools/build.py`` (``check_request_templates``) and are tested in
``test_build.py``; how titles stay distinct is in ``test_classifiers.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from unitysvc_data import ALIASES, MANIFEST, doc_preset


def _read(preset: str):
    """The parsed JSON of a preset's file, alias or pinned version alike."""
    return json.loads(Path(doc_preset(preset)["file_path"]).read_text(encoding="utf-8"))


def _bodies(entries: list[dict]) -> dict[str, dict]:
    return {entry["format"]: entry["body"] for entry in entries}


# --------------------------------------------------------------------------- #
# The chat template: migrated in shape, not rewritten
# --------------------------------------------------------------------------- #
def test_the_alias_resolves_to_the_entry_list():
    """What `llm_example_collection` and every `$doc_preset: llm_request_template`
    get is the newest version, and that is the one in the new shape."""
    assert ALIASES["llm_request_template"] == "llm_request_template_v3"
    assert isinstance(_read("llm_request_template"), list)


def test_v3_is_v2_repackaged_not_rewritten():
    """The issue's acceptance criterion for chat is that it behaves identically.
    A migration that quietly improved a prompt on the way through would not, so
    this pins the bodies, the formats and their order against the version they
    replace."""
    v2 = _read("llm_request_template_v2")
    v3 = _read("llm_request_template_v3")

    assert _bodies(v3) == v2
    assert [entry["format"] for entry in v3] == list(v2)


def test_every_chat_entry_is_a_format_the_gateway_names():
    """The gateway's own vocabulary for the formats chat bodies are written in
    (apisix-gateways `request_meta`), not the finer dialect tokens the code
    examples use: `dashscope`, not `dashscope_text` / `dashscope_multimodal`."""
    formats = [entry["format"] for entry in _read("llm_request_template")]

    assert formats == ["openai", "anthropic", "cohere", "dashscope", "bedrock_converse"]


def test_chat_is_served_by_one_family_and_it_names_chat():
    chat = [
        entry
        for key, entry in MANIFEST["presets"].items()
        if key.startswith("llm_request_template") and entry["applies_to"].get("capability") == "chat"
    ]

    assert {entry["preset_name"] for entry in chat} == {"llm_request_template"}
    assert [entry["version"] for entry in chat] == [1, 2, 3]
