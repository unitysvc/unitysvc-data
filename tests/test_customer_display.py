"""Rules for ``{% if not customer_display %}`` blocks in shipped examples.

``customer_display`` (unitysvc/unitysvc#2488) lets one template serve two
audiences: the renderer executes the full source, and the customer-facing
projection renders it again with the flag set so execution-only scaffolding
disappears. That only stays honest if the hidden part is *strictly* removable
— everything a customer reads must be something the runner executed.

These tests enforce that. The synthetic cases below come first deliberately:
no shipped preset uses the flag yet, so a corpus-only suite would pass while
catching nothing. Each rule is proven against a template that breaks it.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from tools.customer_display import (
    EXECUTION_ONLY_MARKERS,
    audience_violations,
    is_ordered_subsequence,
    unwrapped_scaffolding,
)


class TestElseIsRejected:
    """An ``{% else %}`` arm ships to customers but is never executed."""

    def test_else_arm_is_a_violation(self) -> None:
        source = (
            "print('shared')\n"
            "{% if not customer_display %}\n"
            "assert response\n"
            "{% else %}\n"
            "print('customers see this and nothing ever runs it')\n"
            "{% endif %}\n"
        )

        assert any("else" in v for v in audience_violations(source))

    def test_elif_arm_is_a_violation(self) -> None:
        source = (
            "{% if not customer_display %}\n"
            "assert response\n"
            "{% elif something %}\n"
            "print('never executed')\n"
            "{% endif %}\n"
        )

        assert any("elif" in v for v in audience_violations(source))

    def test_a_block_without_an_else_is_accepted(self) -> None:
        source = (
            "print('shared')\n"
            "{%- if not customer_display %}\n"
            "assert response\n"
            "{%- endif %}\n"
        )

        assert audience_violations(source) == []

    def test_an_unrelated_else_is_not_a_violation(self) -> None:
        # ``local_testing`` legitimately has two arms: both are executed, one
        # against the upstream and one through the gateway.
        source = (
            "{% if local_testing %}\n"
            "url = 'upstream'\n"
            "{% else %}\n"
            "url = 'gateway'\n"
            "{% endif %}\n"
        )

        assert audience_violations(source) == []

    def test_an_else_nested_inside_the_block_is_still_rejected(self) -> None:
        # The nested ``{% if %}`` must not absorb the ``{% else %}`` that
        # belongs to the customer_display conditional.
        source = (
            "{% if not customer_display %}\n"
            "{% if local_testing %}\n"
            "assert a\n"
            "{% else %}\n"
            "assert b\n"
            "{% endif %}\n"
            "{% else %}\n"
            "print('never executed')\n"
            "{% endif %}\n"
        )

        assert any("else" in v for v in audience_violations(source))


class TestPolarityAndPlacement:
    def test_bare_customer_display_condition_is_a_violation(self) -> None:
        # ``{% if customer_display %}`` is display-only content: never
        # executed, and on a renderer that does not supply the flag it
        # silently vanishes instead of failing safe.
        source = "{% if customer_display %}\nprint('never executed')\n{% endif %}\n"

        assert any("not customer_display" in v for v in audience_violations(source))

    def test_negated_comparison_is_a_violation(self) -> None:
        source = (
            "{% if customer_display == False %}\nassert x\n{% endif %}\n"
        )

        assert audience_violations(source) != []

    def test_tag_sharing_a_line_with_code_is_a_violation(self) -> None:
        source = "print('x'){% if not customer_display %}assert x{% endif %}\n"

        assert any("own line" in v for v in audience_violations(source))

    def test_the_trim_form_is_required(self) -> None:
        # A plain ``{% if %}`` on its own line leaves that line's newline in
        # the output, so wrapping an example CHANGES what the runner executes
        # (a blank line appears where the tag was). ``{%-`` absorbs it, and
        # only that form leaves the executed render byte-identical.
        source = "{% if not customer_display %}\nassert x\n{%- endif %}\n"

        assert any("{%-" in v for v in audience_violations(source))

    def test_the_trim_form_is_accepted(self) -> None:
        source = "line1\n{%- if not customer_display %}\nassert x\n{%- endif %}\nline2\n"

        assert audience_violations(source) == []

    def test_wrapping_in_the_trim_form_leaves_the_executed_render_untouched(
        self,
    ) -> None:
        """The property the trim form exists to preserve."""
        env = jinja2.Environment()
        unwrapped = "line1\nassert x\nline2\n"
        wrapped = (
            "line1\n{%- if not customer_display %}\nassert x\n{%- endif %}\nline2\n"
        )

        executed = env.from_string(wrapped).render(customer_display=False)

        assert executed == env.from_string(unwrapped).render(customer_display=False)


class TestOrderedSubsequence:
    """Removal-only: displayed must be executed, minus whole lines."""

    def test_removed_lines_are_a_subsequence(self) -> None:
        executed = ["a", "assert x", "b"]
        displayed = ["a", "b"]

        assert is_ordered_subsequence(displayed, executed)

    def test_added_line_is_not_a_subsequence(self) -> None:
        executed = ["a", "b"]
        displayed = ["a", "customers only", "b"]

        assert not is_ordered_subsequence(displayed, executed)

    def test_reordering_is_not_a_subsequence(self) -> None:
        executed = ["a", "b"]
        displayed = ["b", "a"]

        assert not is_ordered_subsequence(displayed, executed)

    def test_duplicates_are_counted_not_collapsed(self) -> None:
        executed = ["a", "b"]
        displayed = ["a", "a", "b"]

        assert not is_ordered_subsequence(displayed, executed)

    def test_altered_text_is_not_a_subsequence(self) -> None:
        executed = ["print('hello')"]
        displayed = ["print('goodbye')"]

        assert not is_ordered_subsequence(displayed, executed)


class TestUnwrappedScaffolding:
    def test_bare_assertion_is_reported(self) -> None:
        source = "resp = call()\nassert resp.ok\n"

        assert unwrapped_scaffolding(source, ".py.j2")

    def test_assertion_inside_the_block_is_not_reported(self) -> None:
        source = (
            "resp = call()\n"
            "{% if not customer_display %}\n"
            "assert resp.ok\n"
            "{% endif %}\n"
        )

        assert unwrapped_scaffolding(source, ".py.j2") == []

    def test_shell_ok_marker_is_reported(self) -> None:
        source = 'curl -sS "$URL"\necho "example ok"\n'

        assert unwrapped_scaffolding(source, ".sh.j2")

    def test_ordinary_code_is_not_reported(self) -> None:
        source = "resp = call()\nprint(resp.text)\n"

        assert unwrapped_scaffolding(source, ".py.j2") == []

    def test_markers_are_language_scoped(self) -> None:
        # ``echo "example ok"`` is a shell marker; the same text inside a
        # Python string is not a Python assertion.
        source = 'print(\'echo "example ok"\')\n'

        assert unwrapped_scaffolding(source, ".py.j2") == []

    def test_every_marker_language_is_covered(self) -> None:
        """The marker table must not quietly lose a language."""
        assert set(EXECUTION_ONLY_MARKERS) == {".py.j2", ".sh.j2", ".js.j2"}


# ---------------------------------------------------------------------------
# The shipped corpus
# ---------------------------------------------------------------------------

EXAMPLES_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "unitysvc_data" / "examples"
)
BASELINE_PATH = Path(__file__).resolve().parent / "customer_display_baseline.txt"
ALL_EXAMPLES = sorted(EXAMPLES_DIR.rglob("*.j2"))


def _suffix(path: Path) -> str:
    return "." + ".".join(path.name.split(".")[-2:])


def _baseline() -> set[str]:
    return {
        line.strip()
        for line in BASELINE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def _render(path: Path, *, local_testing: bool, customer_display: bool) -> list[str]:
    """Render with only the two audience flags bound.

    ChainableUndefined lets ``{{ routing_key.model }}`` resolve to empty
    rather than raise, so a template renders without a service context.
    """
    env = jinja2.Environment(
        undefined=jinja2.ChainableUndefined, keep_trailing_newline=True
    )
    return (
        env.from_string(path.read_text(encoding="utf-8"))
        .render(local_testing=local_testing, customer_display=customer_display)
        .splitlines()
    )


def test_there_are_examples_to_check() -> None:
    """Guard against the glob silently matching nothing."""
    assert len(ALL_EXAMPLES) > 500


@pytest.mark.parametrize(
    "path", ALL_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR))
)
def test_example_obeys_the_customer_display_contract(path: Path) -> None:
    violations = audience_violations(path.read_text(encoding="utf-8"))

    assert violations == [], "\n".join(violations)


@pytest.mark.parametrize(
    "path", ALL_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR))
)
@pytest.mark.parametrize("local_testing", [True, False], ids=["local", "gateway"])
def test_customer_render_only_removes_lines(path: Path, local_testing: bool) -> None:
    """The customer form must be the executed form minus whole lines.

    Compares two renders of the SAME context differing only in
    ``customer_display`` — never a worker render against a public one, since
    other flags legitimately change the output.
    """
    executed = _render(path, local_testing=local_testing, customer_display=False)
    displayed = _render(path, local_testing=local_testing, customer_display=True)

    assert is_ordered_subsequence(displayed, executed), (
        f"{path.name}: the customer_display render is not an ordered "
        f"subsequence of the executed render — it adds or reorders lines"
    )


@pytest.mark.parametrize(
    "path", ALL_EXAMPLES, ids=lambda p: str(p.relative_to(EXAMPLES_DIR))
)
def test_scaffolding_is_wrapped_or_baselined(path: Path) -> None:
    """Ratchet: no NEW unwrapped scaffolding, and no stale baseline entry."""
    relative = str(path.relative_to(EXAMPLES_DIR))
    hits = unwrapped_scaffolding(path.read_text(encoding="utf-8"), _suffix(path))
    baselined = relative in _baseline()

    if hits and not baselined:
        pytest.fail(
            f"{relative} has execution-only code outside a "
            f"{{% if not customer_display %}} block:\n  "
            + "\n  ".join(hits)
            + "\n\nWrap it, or add the path to tests/customer_display_baseline.txt "
            "if this example is not being migrated yet."
        )
    if baselined and not hits:
        pytest.fail(
            f"{relative} is listed in tests/customer_display_baseline.txt but "
            f"has no unwrapped scaffolding left. Delete the line — the "
            f"baseline may only shrink."
        )


def test_baseline_lists_only_existing_files() -> None:
    missing = sorted(
        entry for entry in _baseline() if not (EXAMPLES_DIR / entry).is_file()
    )

    assert missing == [], (
        "tests/customer_display_baseline.txt references files that no longer "
        f"exist: {missing}"
    )
