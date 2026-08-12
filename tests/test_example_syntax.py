"""Every shipped code example must render to syntactically valid source.

These templates are executed verbatim by the seller test runner and shown to
customers on the marketplace, so a typo in one of them surfaces as a failing
service rather than a failing build. Nothing checked them before, which is how a
sweep across 200+ examples could have silently broken a branch nobody renders
locally.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import jinja2
import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "src" / "unitysvc_data" / "examples"

# `${NAME}` placeholders are substituted by the backend, not by Jinja, and appear
# both inside string literals and in expression position (``json=${__native_body__}``).
# Standing in a literal keeps both forms parseable.
PLACEHOLDER_RE = re.compile(r"\$\{[^}]*\}")

PY_EXAMPLES = sorted(EXAMPLES_DIR.rglob("*.py.j2"))


def _render(path: Path, *, local_testing: bool) -> str:
    """Render with everything undefined but ``local_testing``.

    ChainableUndefined lets ``{{ routing_key.model }}`` resolve to empty rather
    than raising, so a template renders without a full service context.
    """
    env = jinja2.Environment(undefined=jinja2.ChainableUndefined, keep_trailing_newline=True)
    source = env.from_string(path.read_text(encoding="utf-8")).render(local_testing=local_testing)
    return PLACEHOLDER_RE.sub("None", source)


def test_there_are_python_examples_to_check():
    """Guard against the glob silently matching nothing."""
    assert len(PY_EXAMPLES) > 100


@pytest.mark.parametrize("path", PY_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR)))
@pytest.mark.parametrize("local_testing", [True, False], ids=["local", "gateway"])
def test_python_example_renders_to_valid_syntax(path: Path, local_testing: bool):
    ast.parse(_render(path, local_testing=local_testing))


@pytest.mark.parametrize("path", PY_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR)))
def test_python_example_surfaces_the_response_body(path: Path):
    """A failing call must report what the server said.

    ``raise_for_status()`` raises "400 Client Error: Bad Request for url: ..." and
    drops the body, so a gateway or upstream error reaches the test artifact with
    its actual message thrown away. Diagnosing unitysvc/unitysvc#1782 took three
    rounds of guesswork for exactly this reason: the real answer
    ("anthropic-version: header is required") was in a body nobody printed.
    """
    source = path.read_text(encoding="utf-8")
    assert "response.raise_for_status()" not in source, (
        f"{path.name} discards the response body on failure; raise with "
        f"response.text instead so the server's message survives"
    )


SH_EXAMPLES = sorted(EXAMPLES_DIR.rglob("*.sh.j2"))


@pytest.mark.parametrize("path", SH_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR)))
def test_shell_example_does_not_discard_the_error_body(path: Path):
    """``--fail-with-body`` writes the error body to the output target.

    Pairing it with ``-o /dev/null`` therefore surfaces nothing but
    ``curl: (22) The requested URL returned error: 400`` — the flag looks like it
    reports the failure while sending the message it recovered straight to the
    bit bucket. Capture the body and print it on the failure path instead.
    """
    source = path.read_text(encoding="utf-8")
    for line in source.splitlines():
        if "--fail-with-body" in line and "-o /dev/null" in line:
            pytest.fail(
                f"{path.name}: --fail-with-body is defeated by -o /dev/null on "
                f"this line, so the server's message is discarded:\n    {line.strip()}"
            )
