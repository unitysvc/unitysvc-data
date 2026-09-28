"""Validate ``{% if not customer_display %}`` blocks in example templates.

``customer_display`` (unitysvc/unitysvc#2488) is how one template serves two
audiences. The renderer executes the full source; the customer-facing
projection renders it again with the flag set, and execution-only scaffolding
disappears. The guarantee that makes this honest is narrow:

    Everything a customer reads is something the runner executed.

Which holds only if the flag exclusively *removes* whole lines. Three ways it
stops holding, all enforced here:

* an ``{% else %}`` arm is shown to customers and never executed;
* ``{% if customer_display %}`` (without ``not``) is display-only content, and
  inverts the safe default — every document renderer uses a lenient Jinja
  environment, so an absent flag is falsy, and only the ``not`` form degrades
  to "execute the checks" on a renderer that does not supply it yet;
* a tag sharing a line with code splices lines and makes the two renders
  incomparable — so each tag sits alone on its line, and opens with ``{%-`` so
  it absorbs that line's own newline. Without the trim, wrapping an example
  inserts a blank line where the tag was, which changes what the runner
  executes; with it, the executed render is byte-identical to the unwrapped
  original and a migration is invisible to anything that renders it.

Importable so preset authors can run it directly; the gate is
``tests/test_customer_display.py``.
"""

from __future__ import annotations

import re

#: A Jinja statement tag and its inner expression.
_TAG_RE = re.compile(r"\{%-?\s*(.*?)\s*-?%\}", re.DOTALL)
#: Same, but keeping the delimiters so whitespace control is visible.
_RAW_TAG_RE = re.compile(r"\{%-?.*?-?%\}", re.DOTALL)

#: The only accepted condition. Anything else is rejected rather than guessed
#: at: ``customer_display == False`` and ``not not customer_display`` may be
#: equivalent to a reader, but each new spelling is one more thing every
#: downstream renderer has to agree about.
_ACCEPTED_CONDITION = "not customer_display"

#: Lines that only make sense when something is executing them. Deliberately
#: conservative — each pattern is anchored to a statement, so prose mentioning
#: "assert" or a string containing ``example ok`` does not trip it.
EXECUTION_ONLY_MARKERS: dict[str, tuple[re.Pattern[str], ...]] = {
    ".py.j2": (
        re.compile(r"^\s*assert\s"),
        re.compile(r"^\s*raise\s+SystemExit\b"),
        re.compile(r"^\s*sys\.exit\("),
    ),
    ".sh.j2": (
        re.compile(r"^\s*exit\s+[1-9]"),
        re.compile(r"""^\s*echo\s+['"]example ok['"]"""),
        re.compile(r"^\s*echo\s+.*\|\s*grep\s+-q\b"),
        re.compile(r"\|\s*grep\s+-q\b"),
    ),
    ".js.j2": (
        re.compile(r"^\s*process\.exit\(\s*[1-9]"),
        re.compile(r"^\s*throw\s+new\s+Error\b"),
    ),
}


def _condition(tag_body: str) -> str | None:
    """The condition of an ``if``/``elif`` tag, or None for any other tag."""
    for keyword in ("if ", "elif "):
        if tag_body.startswith(keyword):
            return tag_body[len(keyword) :].strip()
    return None


def _mentions_flag(text: str) -> bool:
    return "customer_display" in text


def audience_violations(source: str) -> list[str]:
    """Every way ``source`` breaks the customer_display contract.

    Returns human-readable messages; empty means the template is conformant
    (including the common case of not using the flag at all).
    """
    violations: list[str] = []

    # --- placement: each flag tag alone on its line, no whitespace control ---
    for lineno, line in enumerate(source.splitlines(), start=1):
        for raw in _RAW_TAG_RE.findall(line):
            if not _mentions_flag(raw):
                continue
            if not raw.startswith("{%-"):
                violations.append(
                    f"line {lineno}: customer_display tag must open with "
                    f"'{{%-' ({raw.strip()}). A plain tag leaves its own "
                    f"newline in the output, so wrapping an example changes "
                    f"what the runner executes; the trim form leaves the "
                    f"executed render byte-identical."
                )
            if line.strip() != raw.strip():
                violations.append(
                    f"line {lineno}: a customer_display tag must be on its "
                    f"own line, got {line.strip()!r}"
                )

    # --- structure: walk the tag stream, tracking customer_display blocks ---
    # ``depth`` counts open ``if`` blocks; ``guarded`` holds the depth at which
    # each customer_display block opened, so a nested ``{% else %}`` belongs to
    # the inner conditional and only the matching one is reported.
    depth = 0
    guarded: list[int] = []
    for match in _TAG_RE.finditer(source):
        body = match.group(1).strip()
        lineno = source.count("\n", 0, match.start()) + 1
        condition = _condition(body)

        if body.startswith("if "):
            depth += 1
            if _mentions_flag(condition or ""):
                if (condition or "").strip() != _ACCEPTED_CONDITION:
                    violations.append(
                        f"line {lineno}: condition must be exactly "
                        f"'{_ACCEPTED_CONDITION}', got {condition!r}"
                    )
                guarded.append(depth)
        elif body.startswith("elif "):
            if _mentions_flag(condition or ""):
                violations.append(
                    f"line {lineno}: 'elif' on a customer_display condition; "
                    f"the branch is shown to customers but never executed"
                )
            elif guarded and guarded[-1] == depth:
                violations.append(
                    f"line {lineno}: 'elif' inside a customer_display block; "
                    f"the branch is shown to customers but never executed"
                )
        elif body == "else":
            if guarded and guarded[-1] == depth:
                violations.append(
                    f"line {lineno}: 'else' on a customer_display block; the "
                    f"branch is shown to customers but never executed"
                )
        elif body == "endif":
            if guarded and guarded[-1] == depth:
                guarded.pop()
            depth -= 1

    return violations


def is_ordered_subsequence(displayed: list[str], executed: list[str]) -> bool:
    """Is every displayed line present, in order, in the executed render?

    An ordered subsequence rather than a set comparison: a set test accepts
    reordered output and silently collapses repeated lines, so a template that
    shuffled or deduplicated its customer-facing form would pass one and fail
    the other.
    """
    remaining = iter(executed)
    return all(line in remaining for line in displayed)


def unwrapped_scaffolding(source: str, suffix: str) -> list[str]:
    """Execution-only lines that are NOT inside a customer_display block.

    Advisory by nature — the marker table cannot know every shape scaffolding
    takes — so the gate treats this as a ratchet against a recorded baseline
    rather than an absolute rule.
    """
    patterns = EXECUTION_ONLY_MARKERS.get(suffix)
    if not patterns:
        return []

    found: list[str] = []
    depth = 0
    guarded: list[int] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        tags = [t.strip() for t in _TAG_RE.findall(line)]
        for body in tags:
            if body.startswith("if "):
                depth += 1
                if _mentions_flag(body):
                    guarded.append(depth)
            elif body == "endif":
                if guarded and guarded[-1] == depth:
                    guarded.pop()
                depth -= 1
        if guarded or tags:
            continue
        if any(pattern.search(line) for pattern in patterns):
            found.append(f"line {lineno}: {line.strip()}")
    return found


def main(argv: list[str] | None = None) -> int:
    """Report violations for the shipped examples, or for paths given as args."""
    import sys
    from pathlib import Path

    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        paths = [Path(a) for a in args]
    else:
        root = Path(__file__).resolve().parent.parent
        paths = sorted((root / "src" / "unitysvc_data" / "examples").rglob("*.j2"))

    failed = 0
    for path in paths:
        source = path.read_text(encoding="utf-8")
        suffix = "." + ".".join(path.name.split(".")[-2:])
        for message in audience_violations(source):
            print(f"{path}: {message}")
            failed += 1
        for message in unwrapped_scaffolding(source, suffix):
            print(f"{path}: unwrapped execution-only code: {message}")
    print(f"\n{len(paths)} template(s) checked; {failed} contract violation(s).")
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    raise SystemExit(main())
