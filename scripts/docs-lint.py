#!/usr/bin/env python3
"""Documentation gates for the Gyrel site.

The checks are intentionally small and stdlib-only so the same script runs in
CI and in ``./dev.sh check``:

  * R-16 / X-4  every ``[control: ID]`` reference resolves to a recorded entry
                in ``docs/controls/ledger.jsonl``;
  * R-3 / R-8   banned prose tokens in English and Russian, with inline code
                spans, fenced code blocks and link targets exempt;
  * R-21..R-24  EN/RU heading tree, code-block bytes and table shapes match,
                and a RU ``parity: <en-path>@<sha>`` front-matter value is
                enforced when present;
  * R-19        a reference page carries an exit-code/status table;
  * R-25        private capture paths and internal executor report names are
                banned from pages, including inline code.

Run ``python3 scripts/docs-lint.py --self-test`` to exercise the checks against
good and deliberately bad fixtures.  Run without arguments to lint the repo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Banned prose tokens
# ---------------------------------------------------------------------------

# (rule, pattern, label).  Patterns are compiled with re.IGNORECASE.
EN_BANNED = [
    # R-2: no authorial first-person plural.
    ("R-2", r"\bwe\b", "we"),
    ("R-2", r"\bour\b", "our"),
    ("R-2", r"\bus\b", "us"),
    # R-3: hype and filler.
    ("R-3", r"\bseamless\b", "seamless"),
    ("R-3", r"\brobust\b", "robust"),
    ("R-3", r"\bcutting-edge\b", "cutting-edge"),
    ("R-3", r"\bstate-of-the-art\b", "state-of-the-art"),
    ("R-3", r"\bleverage\b", "leverage"),
    ("R-3", r"\bempower\b", "empower"),
    ("R-3", r"\bunlock\b", "unlock"),
    ("R-3", r"\brevolutionary\b", "revolutionary"),
    ("R-3", r"\bbest-in-class\b", "best-in-class"),
    ("R-3", r"\bhassle-free\b", "hassle-free"),
    ("R-3", r"\blightning-fast\b", "lightning-fast"),
    ("R-3", r"\bgame-changer\b", "game-changer"),
    ("R-3", r"\bdelve\b", "delve"),
    ("R-3", r"\beffortless\b", "effortless"),
    ("R-3", r"\bpowerful\b", "powerful"),
    ("R-3", r"\bflexible\b", "flexible"),
    ("R-3", r"\bsimply\b", "simply"),
    ("R-3", r"\bjust\b", "just"),
    ("R-3", r"\beasily\b", "easily"),
    ("R-3", r"in today['\u2019]s fast-paced world", "in today's fast-paced world"),
    ("R-3", r"it is important to note", "it is important to note"),
    ("R-3", r"\bnote that\b", "note that"),
    ("R-3", r"as we all know", "as we all know"),
    # R-5: marketing metaphors.
    ("R-5", r"\bsupercharge\b", "supercharge"),
    ("R-5", r"under the hood magic", "under the hood magic"),
    # R-15: absolute bans.
    ("R-15", r"drop-in replacement", "drop-in replacement"),
    ("R-15", r"fully compatible", "fully compatible"),
    ("R-15", r"100% parity", "100% parity"),
    ("R-15", r"production-ready", "production-ready"),
    ("R-15", r"just works", "just works"),
]

RU_BANNED = [
    # R-8: канцелярит.  The demonstrative forms are banned; "данные"
    # (data) and its oblique plural forms are not.
    ("R-8", r"(?<![\u0410-\u044f\u0401\u0451])данн(ый|ого|ому|ом|ая|ой|ую|ою)(?![\u0410-\u044f\u0401\u0451])", "данный"),
    ("R-8", r"(?<![\u0410-\u044f\u0401\u0451])осуществля", "осуществлять"),
    ("R-8", r"(?<![\u0410-\u044f\u0401\u0451])производ(ить|ит|ят|ил|ила|или|ящий|ящая|ящее|ящие)(?![\u0410-\u044f\u0401\u0451])", "производить"),
    ("R-8", r"(?<![\u0410-\u044f\u0401\u0451])явля(ется|ются|лся|лась|лись|ющийся|ющаяся|ющееся|ющиеся)(?![\u0410-\u044f\u0401\u0451])", "является"),
    ("R-8", r"в целях", "в целях"),
    # R-8: calques.
    ("R-8", r"бесшовн", "бесшовный"),
    ("R-8", r"передов", "передовой"),
    ("R-8", r"использовать преимущества", "использовать преимущества"),
    ("R-8", r"раскрыть потенциал", "раскрыть потенциал"),
    ("R-8", r"важно отметить", "Важно отметить"),
    ("R-8", r"как известно", "Как известно"),
]

EN_BANNED = [(rule, re.compile(pattern, re.IGNORECASE), label) for rule, pattern, label in EN_BANNED]
RU_BANNED = [(rule, re.compile(pattern, re.IGNORECASE), label) for rule, pattern, label in RU_BANNED]

# (token, label).  Matched literally against raw page lines, so inline code
# spans do not exempt a hit.
PRIVATE_PATTERNS = [("/tmp/rheic-", "private capture path"), ("EXECUTOR-REPORT", "internal report reference")]

CONTROL_REF = re.compile(r"\[control:\s*([A-Za-z0-9._:-]+)\s*\]")
HEADING = re.compile(r"^(#{1,6})\s+\S", re.MULTILINE)
FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,})([^\n]*)$")
PARITY = re.compile(r"^([0-9a-f]{7,40})$", re.IGNORECASE)
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Return simple top-level front-matter keys and the body."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            front = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            data: dict[str, str] = {}
            for line in front.splitlines():
                if not line or line[0] in " \t-#":
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip().strip("'\"")
            return data, body
    return {}, text


def blank_fenced(text: str) -> str:
    """Replace fenced code blocks with newlines, preserving line numbers."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    fence: str | None = None
    for line in lines:
        match = FENCE.match(line.rstrip("\n"))
        if fence is not None:
            out.append("\n" if line.endswith("\n") else "")
            if match and match.group(2)[0] == fence[0] and len(match.group(2)) >= len(fence):
                fence = None
            continue
        if match:
            fence = match.group(2)
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(line)
    return "".join(out)


def strip_non_prose(text: str) -> str:
    """Blank front matter, fenced code, inline code, link targets and HTML."""
    _, body = split_front_matter(text)
    body = blank_fenced(body)
    # HTML comments can span lines.
    body = re.sub(r"(?s)<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), body)
    # <code>...</code> is code font too.
    body = re.sub(r"(?is)<code>.*?</code>", "", body)
    # Keep link text, drop the destination.
    body = re.sub(r"\]\([^)]*\)", "]", body)
    # Autolinks and bare URLs are not prose.
    body = re.sub(r"<https?://[^>]*>", "", body)
    body = re.sub(r"https?://\S+", "", body)
    # Inline code spans.
    body = re.sub(r"`+[^`\n]*`+", "", body)
    # Remaining HTML tags.
    body = re.sub(r"</?[A-Za-z][^>]*>", "", body)
    return body


def code_blocks(text: str) -> list[str]:
    """Return each fenced code block exactly as written, delimiters included."""
    lines = text.splitlines(keepends=True)
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        match = FENCE.match(lines[i].rstrip("\n"))
        if not match:
            i += 1
            continue
        fence = match.group(2)
        start = i
        i += 1
        while i < len(lines):
            closing = re.match(
                r"^[ \t]*" + re.escape(fence[0]) + r"{" + str(len(fence)) + r",}[ \t]*$",
                lines[i].rstrip("\n"),
            )
            if closing:
                i += 1
                break
            i += 1
        blocks.append("".join(lines[start:i]))
    return blocks


def heading_levels(text: str) -> list[int]:
    _, body = split_front_matter(text)
    body = blank_fenced(body)
    return [len(m.group(1)) for m in HEADING.finditer(body)]


def _split_row(line: str) -> list[str]:
    """Split a Markdown table row on unescaped pipes outside code spans."""
    raw = line.strip()
    cells: list[str] = []
    current: list[str] = []
    i = 0
    in_code = False
    code_ticks = 0
    while i < len(raw):
        char = raw[i]
        if char == "\\" and i + 1 < len(raw) and raw[i + 1] == "|":
            current.append("|")
            i += 2
            continue
        if char == "`":
            j = i
            while j < len(raw) and raw[j] == "`":
                j += 1
            run = j - i
            if not in_code:
                in_code = True
                code_ticks = run
            elif code_ticks == run:
                in_code = False
                code_ticks = 0
            current.append(raw[i:j])
            i = j
            continue
        if char == "|" and not in_code:
            cells.append("".join(current))
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    cells.append("".join(current))
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and set(stripped) <= set("|:- ") and "-" in stripped


def table_blocks(text: str) -> list[list[str]]:
    """Return contiguous Markdown table blocks outside fenced code."""
    body = blank_fenced(split_front_matter(text)[1])
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in body.splitlines():
        if line.lstrip().startswith("|"):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def table_shapes(text: str) -> list[tuple[int, int]]:
    shapes: list[tuple[int, int]] = []
    for block in table_blocks(text):
        rows = [line for line in block if not _is_separator(line)]
        if not rows:
            continue
        widths = [len(_split_row(line)) for line in rows]
        shapes.append((len(rows), max(widths)))
    return shapes


def table_header(text: str) -> list[str] | None:
    for block in table_blocks(text):
        if block:
            return _split_row(block[0])
    return None


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


def load_ledger(path: Path, root: Path) -> tuple[dict[str, dict], list[str]]:
    entries: dict[str, dict] = {}
    errors: list[str] = []
    if not path.is_file():
        return {}, [f"{path.relative_to(root)}: ledger file is missing"]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        where = f"{path.relative_to(root)}:{lineno}"
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: invalid JSON: {exc}")
            continue
        if not isinstance(entry, dict):
            errors.append(f"{where}: ledger row must be a JSON object")
            continue
        ident = entry.get("id")
        if not isinstance(ident, str) or not ID_RE.match(ident):
            errors.append(f"{where}: missing or invalid id")
            continue
        if ident in entries:
            errors.append(f"{where}: duplicate control id {ident!r}")
            continue
        status = entry.get("status")
        if status not in {"recorded", "pending"}:
            errors.append(f"{where}: control {ident!r} has invalid status {status!r}")
        control_class = entry.get("control_class")
        if control_class not in {"E1", "E2", "E3"}:
            errors.append(f"{where}: control {ident!r} has invalid control_class {control_class!r}")
        for required in ("title", "scope", "source"):
            if not entry.get(required):
                errors.append(f"{where}: control {ident!r} is missing {required}")
        if status == "recorded":
            for required in ("date", "runner", "components"):
                if not entry.get(required):
                    errors.append(f"{where}: recorded control {ident!r} is missing {required}")
            artifacts = entry.get("artifacts")
            if not isinstance(artifacts, list) or not artifacts:
                errors.append(f"{where}: recorded control {ident!r} has no artifacts")
            else:
                errors.extend(_check_artifacts(ident, where, artifacts, root))
        elif status == "pending":
            if not entry.get("pending_for"):
                errors.append(f"{where}: pending control {ident!r} is missing pending_for")
        entries[ident] = entry
    return entries, errors


def _check_artifacts(ident: str, where: str, artifacts: list, root: Path) -> list[str]:
    errors: list[str] = []
    for item in artifacts:
        if not isinstance(item, dict) or not item.get("path"):
            errors.append(f"{where}: control {ident!r} has an artifact without a path")
            continue
        scope = item.get("scope", "external")
        path = Path(item["path"])
        expected = item.get("sha256")
        if scope == "repo":
            candidate = root / path
            if not candidate.is_file():
                errors.append(f"{where}: control {ident!r} artifact is missing: {item['path']}")
                continue
            if expected and _sha256(candidate) != expected.lower():
                errors.append(f"{where}: control {ident!r} artifact digest mismatch: {item['path']}")
        elif scope == "external":
            # External evidence is retrievable from the recorded host path.  CI
            # does not have /tmp state, so absence is not an error; if the file
            # is present locally, its digest is still checked.
            if path.is_file() and expected and _sha256(path) != expected.lower():
                errors.append(f"{where}: control {ident!r} artifact digest mismatch: {item['path']}")
        else:
            errors.append(f"{where}: control {ident!r} artifact has unknown scope {scope!r}")
    return errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_banned_words(root: Path) -> list[str]:
    errors: list[str] = []
    for lang, rules in (("en", EN_BANNED), ("ru", RU_BANNED)):
        for path in sorted((root / "docs" / lang).rglob("*.md")):
            prose = strip_non_prose(path.read_text(encoding="utf-8"))
            for lineno, line in enumerate(prose.splitlines(), 1):
                for rule, pattern, label in rules:
                    if pattern.search(line):
                        rel = path.relative_to(root)
                        errors.append(f"{rel}:{lineno}: banned token {label!r} ({rule})")
    return errors


def check_private_paths(root: Path) -> list[str]:
    errors: list[str] = []
    for lang in ("en", "ru"):
        for path in sorted((root / "docs" / lang).rglob("*.md")):
            rel = path.relative_to(root)
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for token, label in PRIVATE_PATTERNS:
                    if token in line:
                        errors.append(f"{rel}:{lineno}: {label} {token!r}")
    return errors


def check_control_refs(root: Path, entries: dict[str, dict]) -> tuple[list[str], int]:
    errors: list[str] = []
    count = 0
    for path in sorted((root / "docs").rglob("*.md")):
        if "controls" in path.relative_to(root / "docs").parts:
            continue
        prose = strip_non_prose(path.read_text(encoding="utf-8"))
        for lineno, line in enumerate(prose.splitlines(), 1):
            for match in CONTROL_REF.finditer(line):
                count += 1
                ident = match.group(1)
                rel = path.relative_to(root)
                entry = entries.get(ident)
                if entry is None:
                    errors.append(f"{rel}:{lineno}: unresolved control reference {ident!r}")
                elif entry.get("status") != "recorded":
                    errors.append(f"{rel}:{lineno}: control reference {ident!r} is still pending")
    return errors, count


def check_parity(root: Path, check_git: bool = True) -> list[str]:
    errors: list[str] = []
    en_dir = root / "docs" / "en"
    ru_dir = root / "docs" / "ru"
    en_pages = {p.name for p in en_dir.glob("*.md")}
    ru_pages = {p.name for p in ru_dir.glob("*.md")}
    for name in sorted(en_pages - ru_pages):
        errors.append(f"docs/ru/{name}: missing Russian counterpart")
    for name in sorted(ru_pages - en_pages):
        errors.append(f"docs/ru/{name}: no English counterpart")
    for name in sorted(en_pages & ru_pages):
        en_path = en_dir / name
        ru_path = ru_dir / name
        en_text = en_path.read_text(encoding="utf-8")
        ru_text = ru_path.read_text(encoding="utf-8")
        rel_en = en_path.relative_to(root)
        rel_ru = ru_path.relative_to(root)

        en_heads = heading_levels(en_text)
        ru_heads = heading_levels(ru_text)
        if en_heads != ru_heads:
            errors.append(
                f"{rel_ru}: heading tree differs from {rel_en} "
                f"(EN {en_heads}, RU {ru_heads})"
            )

        en_blocks = code_blocks(en_text)
        ru_blocks = code_blocks(ru_text)
        if en_blocks != ru_blocks:
            where = "block count"
            for index, (left, right) in enumerate(zip(en_blocks, ru_blocks)):
                if left != right:
                    where = f"block {index + 1}"
                    break
            errors.append(f"{rel_ru}: code blocks differ from {rel_en} ({where})")

        en_tables = table_shapes(en_text)
        ru_tables = table_shapes(ru_text)
        if en_tables != ru_tables:
            errors.append(
                f"{rel_ru}: table shapes differ from {rel_en} "
                f"(EN {en_tables}, RU {ru_tables})"
            )

        front, _ = split_front_matter(ru_text)
        parity = front.get("parity")
        if parity:
            errors.extend(_check_parity_value(root, rel_ru, rel_en, parity, check_git))
    return errors


def _check_parity_value(
    root: Path, rel_ru: Path, rel_en: Path, value: str, check_git: bool
) -> list[str]:
    errors: list[str] = []
    if "@" not in value:
        return [f"{rel_ru}: parity must be <en-path>@<sha>, got {value!r}"]
    en_ref, sha = value.rsplit("@", 1)
    sha = sha.strip()
    if not PARITY.match(sha):
        errors.append(f"{rel_ru}: parity sha is not 7-40 hex characters: {sha!r}")

    if en_ref.startswith("docs/"):
        candidate = root / en_ref
    elif en_ref.startswith("en/"):
        candidate = root / "docs" / en_ref
    else:
        candidate = root / "docs" / "en" / en_ref
    if not candidate.is_file():
        errors.append(f"{rel_ru}: parity English path does not exist: {en_ref}")
        return errors
    rel_candidate = candidate.relative_to(root)

    if not check_git or not PARITY.match(sha):
        return errors
    try:
        inside = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return errors
        kind = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-t", sha],
            capture_output=True,
            text=True,
            check=False,
        )
        if kind.returncode != 0:
            errors.append(f"{rel_ru}: parity sha does not resolve in this repository: {sha}")
            return errors
        obj_type = kind.stdout.strip()
        if obj_type == "blob":
            expected = sha
        elif obj_type in {"commit", "tree"}:
            resolved = subprocess.run(
                ["git", "-C", str(root), "rev-parse", f"{sha}:{rel_candidate.as_posix()}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if resolved.returncode != 0:
                errors.append(
                    f"{rel_ru}: parity sha {sha} does not contain {rel_candidate.as_posix()}"
                )
                return errors
            expected = resolved.stdout.strip()
        else:
            errors.append(f"{rel_ru}: parity sha {sha} is a {obj_type}, not a commit or blob")
            return errors
        current = subprocess.run(
            ["git", "-C", str(root), "hash-object", "--", rel_candidate.as_posix()],
            capture_output=True,
            text=True,
            check=False,
        )
        if current.returncode != 0 or current.stdout.strip() != expected:
            errors.append(f"{rel_ru}: parity sha {sha} does not match the current {rel_candidate}")
    except OSError:
        # No git executable: the format and path checks above still ran.
        return errors
    return errors


def _nav_reference_entries(root: Path) -> list[str]:
    mkdocs = root / "mkdocs.yml"
    if not mkdocs.is_file():
        return []
    entries: list[str] = []
    in_reference = False
    base_indent = 0
    for line in mkdocs.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if re.match(r"^\s*(?:-\s*)?Reference:\s*$", line):
            in_reference = True
            base_indent = indent
            continue
        if in_reference:
            if indent <= base_indent:
                in_reference = False
                continue
            match = re.search(r"([A-Za-z0-9_./-]+\.md)\b", line)
            if match:
                entries.append(match.group(1))
    return entries


def _is_reference_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    _, body = split_front_matter(text)
    body = blank_fenced(body)
    match = re.search(r"(?m)^#\s+(.+)$", body)
    return bool(match and re.search(r"\breference\b", match.group(1), re.IGNORECASE))


def _has_exit_status_table(text: str) -> bool:
    for block in table_blocks(text):
        if not block:
            continue
        header = _split_row(block[0])
        code = any(re.search(r"(?i)\b(code|error|код|ошибк)", cell) for cell in header)
        status = any(re.search(r"(?i)\b(status|exit|статус|выход)", cell) for cell in header)
        if code and status:
            return True
    return False


def check_reference_tables(root: Path) -> list[str]:
    errors: list[str] = []
    for ref in _nav_reference_entries(root):
        en_path = root / "docs" / ref
        if not en_path.is_file() or not _is_reference_page(en_path):
            continue
        rel_en = en_path.relative_to(root)
        ru_path = root / "docs" / ref.replace("en/", "ru/", 1)
        for path in (en_path, ru_path):
            if not path.is_file():
                errors.append(f"{path.relative_to(root)}: reference page is missing")
                continue
            if not _has_exit_status_table(path.read_text(encoding="utf-8")):
                errors.append(
                    f"{path.relative_to(root)}: reference page has no exit-code/status table (R-19; see {rel_en})"
                )
    return errors


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def lint(root: Path, check_git: bool = True) -> tuple[list[str], dict[str, int]]:
    entries, errors = load_ledger(root / "docs" / "controls" / "ledger.jsonl", root)
    ref_errors, ref_count = check_control_refs(root, entries)
    errors.extend(ref_errors)
    errors.extend(check_banned_words(root))
    errors.extend(check_private_paths(root))
    errors.extend(check_parity(root, check_git=check_git))
    errors.extend(check_reference_tables(root))
    stats = {
        "pages": len(list((root / "docs" / "en").glob("*.md"))),
        "controls": len(entries),
        "references": ref_count,
    }
    return errors, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint the Gyrel documentation contract.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (default: the parent of scripts/)",
    )
    parser.add_argument("--self-test", action="store_true", help="run fixture self-tests and exit")
    parser.add_argument("--no-git", action="store_true", help="skip git-backed parity sha checks")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_tests()

    root = args.root.resolve()
    errors, stats = lint(root, check_git=not args.no_git)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"docs-lint: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "docs-lint: OK "
        f"({stats['pages']} English pages, {stats['controls']} controls, "
        f"{stats['references']} control references)"
    )
    return 0


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture(tmp: Path) -> None:
    artifact = b"fixture artifact\n"
    digest = hashlib.sha256(artifact).hexdigest()
    _write(tmp / "docs" / "controls" / "artifact.txt", artifact.decode())
    ledger = {
        "id": "E1-TEST",
        "control_class": "E1",
        "status": "recorded",
        "title": "fixture control",
        "date": "2026-11-27",
        "runner": "self-test",
        "components": {"fixture": {"version": "1"}},
        "scope": "self-test fixture",
        "source": "self-test",
        "artifacts": [
            {"path": "docs/controls/artifact.txt", "scope": "repo", "sha256": digest}
        ],
    }
    _write(
        tmp / "docs" / "controls" / "ledger.jsonl",
        json.dumps(ledger, ensure_ascii=False) + "\n",
    )
    _write(
        tmp / "docs" / "en" / "page.md",
        "# Page\n\n"
        "A sentence with [control: E1-TEST].\n\n"
        "```sh\n"
        "echo ok\n"
        "```\n\n"
        "| A | B |\n"
        "| --- | --- |\n"
        "| 1 | 2 |\n",
    )
    _write(
        tmp / "docs" / "ru" / "page.md",
        "# Страница\n\n"
        "Предложение с [control: E1-TEST].\n\n"
        "```sh\n"
        "echo ok\n"
        "```\n\n"
        "| А | Б |\n"
        "| --- | --- |\n"
        "| 1 | 2 |\n",
    )


def _case(name: str, mutate, expected: str | None) -> tuple[str, bool, str]:
    with tempfile.TemporaryDirectory(prefix="docs-lint-") as tmp_name:
        tmp = Path(tmp_name)
        _fixture(tmp)
        mutate(tmp)
        errors, _ = lint(tmp, check_git=False)
        blob = "\n".join(errors)
        if expected is None:
            return name, not errors, blob
        return name, expected in blob, blob


def run_self_tests() -> int:
    def add_banned(tmp: Path) -> None:
        _write(
            tmp / "docs" / "en" / "page.md",
            (tmp / "docs" / "en" / "page.md").read_text(encoding="utf-8")
            + "\nA seamless path.\n",
        )

    def add_code_font(tmp: Path) -> None:
        _write(
            tmp / "docs" / "en" / "page.md",
            (tmp / "docs" / "en" / "page.md").read_text(encoding="utf-8")
            + "\nA `seamless` path.\n",
        )

    def add_private_path(tmp: Path) -> None:
        _write(
            tmp / "docs" / "en" / "page.md",
            (tmp / "docs" / "en" / "page.md").read_text(encoding="utf-8")
            + "\nRaw captures are in `/tmp/rheic-example/probe-logs/`.\n",
        )

    def add_bad_ref(tmp: Path) -> None:
        path = tmp / "docs" / "en" / "page.md"
        _write(path, path.read_text(encoding="utf-8").replace("E1-TEST", "E9-MISSING"))

    def make_pending(tmp: Path) -> None:
        path = tmp / "docs" / "controls" / "ledger.jsonl"
        entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        entries[0]["status"] = "pending"
        entries[0]["pending_for"] = "self-test"
        _write(path, "\n".join(json.dumps(item) for item in entries) + "\n")

    def add_heading(tmp: Path) -> None:
        path = tmp / "docs" / "en" / "page.md"
        _write(path, path.read_text(encoding="utf-8") + "\n## Extra\n")

    def change_code(tmp: Path) -> None:
        path = tmp / "docs" / "ru" / "page.md"
        _write(path, path.read_text(encoding="utf-8").replace("echo ok", "echo no"))

    def change_table(tmp: Path) -> None:
        path = tmp / "docs" / "ru" / "page.md"
        _write(
            path,
            path.read_text(encoding="utf-8").replace("| А | Б |", "| А | Б | В |")
            .replace("| --- | --- |", "| --- | --- | --- |")
            .replace("| 1 | 2 |", "| 1 | 2 | 3 |"),
        )

    def bad_parity_path(tmp: Path) -> None:
        path = tmp / "docs" / "ru" / "page.md"
        text = "---\nparity: en/missing.md@deadbeef\n---\n" + path.read_text(encoding="utf-8")
        _write(path, text)

    def bad_parity_sha(tmp: Path) -> None:
        path = tmp / "docs" / "ru" / "page.md"
        text = "---\nparity: en/page.md@not-a-sha\n---\n" + path.read_text(encoding="utf-8")
        _write(path, text)

    def missing_artifact(tmp: Path) -> None:
        (tmp / "docs" / "controls" / "artifact.txt").unlink()

    def add_reference_page(tmp: Path, table: bool) -> None:
        _write(
            tmp / "mkdocs.yml",
            "nav:\n  - Reference:\n      - CLI: en/cli.md\n",
        )
        body_en = "# CLI reference\n\nRefusals carry a code and an exit status.\n"
        body_ru = "# Справочник CLI\n\nОтказы несут код и статус выхода.\n"
        if table:
            body_en += (
                "\n| Code | Exit status | Meaning |\n"
                "| --- | --- | --- |\n"
                "| `FILTER_REQUIRED` | 2 | Pre-flight refusal. |\n"
            )
            body_ru += (
                "\n| Код | Статус выхода | Значение |\n"
                "| --- | --- | --- |\n"
                "| `FILTER_REQUIRED` | 2 | Отказ до выполнения. |\n"
            )
        _write(tmp / "docs" / "en" / "cli.md", body_en)
        _write(tmp / "docs" / "ru" / "cli.md", body_ru)

    def create_reference_without_table(tmp: Path) -> None:
        add_reference_page(tmp, table=False)

    def create_reference_with_table(tmp: Path) -> None:
        add_reference_page(tmp, table=True)

    def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def _commit_fixture(root: Path) -> str:
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "self-test@example.invalid")
        _git(root, "config", "user.name", "docs-lint self-test")
        _git(root, "add", ".")
        _git(root, "commit", "-q", "-m", "fixture")
        rev = _git(root, "rev-parse", "HEAD")
        return rev.stdout.strip()

    def _git_parity_case(mutate_en: bool) -> tuple[bool, str]:
        with tempfile.TemporaryDirectory(prefix="docs-lint-git-") as tmp_name:
            tmp = Path(tmp_name)
            _fixture(tmp)
            sha = _commit_fixture(tmp)
            ru_path = tmp / "docs" / "ru" / "page.md"
            _write(
                ru_path,
                f"---\nparity: en/page.md@{sha}\n---\n"
                + ru_path.read_text(encoding="utf-8"),
            )
            if mutate_en:
                en_path = tmp / "docs" / "en" / "page.md"
                _write(en_path, en_path.read_text(encoding="utf-8") + "\nChanged after the parity sha.\n")
            errors, _ = lint(tmp, check_git=True)
            return not errors, "\n".join(errors)

    git_parity_ok, git_parity_detail = _git_parity_case(mutate_en=False)
    git_parity_bad, git_parity_bad_detail = _git_parity_case(mutate_en=True)

    cases = [
        _case("good fixture", lambda tmp: None, None),
        _case("unresolved control reference", add_bad_ref, "unresolved control reference"),
        _case("pending control reference", make_pending, "still pending"),
        _case("banned prose token", add_banned, "banned token 'seamless'"),
        _case("code-font exemption", add_code_font, None),
        _case("private capture path", add_private_path, "private capture path"),
        _case("heading tree mismatch", add_heading, "heading tree differs"),
        _case("code-block mismatch", change_code, "code blocks differ"),
        _case("table shape mismatch", change_table, "table shapes differ"),
        _case("parity path", bad_parity_path, "parity English path does not exist"),
        _case("parity sha format", bad_parity_sha, "parity sha is not 7-40 hex"),
        _case("missing artifact", missing_artifact, "artifact is missing"),
        _case("reference table missing", create_reference_without_table, "exit-code/status table"),
        _case("reference table present", create_reference_with_table, None),
    ]

    failures = 0
    for name, ok, detail in cases:
        if ok:
            print(f"ok  {name}")
        else:
            failures += 1
            print(f"FAIL {name}", file=sys.stderr)
            if detail:
                print(detail, file=sys.stderr)

    extra = [
        ("git-backed parity sha", git_parity_ok, git_parity_detail),
        (
            "git-backed parity mismatch",
            not git_parity_bad and "does not match the current" in git_parity_bad_detail,
            git_parity_bad_detail,
        ),
    ]
    for name, ok, detail in extra:
        if ok:
            print(f"ok  {name}")
        else:
            failures += 1
            print(f"FAIL {name}", file=sys.stderr)
            if detail:
                print(detail, file=sys.stderr)

    # Exercise the process exit code as well as the in-process checks.
    with tempfile.TemporaryDirectory(prefix="docs-lint-cli-") as tmp_name:
        tmp = Path(tmp_name)
        _fixture(tmp)
        add_bad_ref(tmp)
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--root", str(tmp), "--no-git"],
            capture_output=True,
            text=True,
            check=False,
        )
        ok = result.returncode == 1 and "unresolved control reference" in result.stderr
        if ok:
            print("ok  bad fixture exits nonzero through the CLI")
        else:
            failures += 1
            print("FAIL bad fixture exits nonzero through the CLI", file=sys.stderr)
            print(result.stdout + result.stderr, file=sys.stderr)

    if failures:
        print(f"docs-lint self-test: {failures} failure(s)", file=sys.stderr)
        return 1
    print(f"docs-lint self-test: {len(cases) + len(extra) + 1} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
