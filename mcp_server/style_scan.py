"""Scan Olivia's past projects (.html / .css only) for real style values.

Pure standard library, no MCP import, so test_scan.py can run it directly.
Read-only: this module never writes, moves or deletes files.
It never prints; it returns text (and logs problems to stderr via `logging`).
"""
from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from pathlib import Path

log = logging.getLogger("ui-style-reference.scan")

PROJECTS_FILE = Path(__file__).with_name("projects.json")
SKIP_DIRS = {"node_modules", ".git", ".venv"}
EXTENSIONS = {".html", ".htm", ".css"}
MAX_FILE_BYTES = 2_000_000
VALID_KINDS = ("tool", "game", "all")

GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
                 "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded", "emoji", "math",
                 "inherit", "initial", "unset", "-apple-system", "blinkmacsystemfont"}
COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b|\b(?:rgba?|hsla?)\([^)]*\)")
GOOGLE_RE = re.compile(r"fonts\.googleapis\.com/css2?\?[^\"'\s)>]+")
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.I | re.S)
INLINE_STYLE_RE = re.compile(r"\sstyle\s*=\s*(\"([^\"]*)\"|'([^']*)')", re.I)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
NOT_RE = re.compile(r":not\([^)]*\)")
LAYOUT_ORDER = ("max-width", "gap", "padding", "line-height")


# ---------------------------------------------------------------- CSS walking
def walk_css(css: str, start_line: int = 1):
    """Yield ('decl', prop, value, line, stack) and ('block', prelude, line, stack)."""
    css = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), css)
    stack: list[str] = []
    buf: list[str] = []
    buf_line = None
    line = start_line
    quote = None
    paren = 0

    def flush():
        text = "".join(buf).strip()
        if stack and ":" in text:
            prop, value = text.split(":", 1)
            return ("decl", prop.strip().lower(), value.strip(), buf_line or line, list(stack))
        return None

    for ch in css:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == "(":
            paren += 1
            buf.append(ch)
        elif ch == ")":
            paren = max(0, paren - 1)
            buf.append(ch)
        elif ch == "{" and paren == 0:
            prelude = "".join(buf).strip()
            yield ("block", prelude, buf_line or line, list(stack))
            stack.append(prelude)
            buf, buf_line = [], None
        elif ch in ";}" and paren == 0:
            item = flush()
            if item:
                yield item
            if ch == "}" and stack:
                stack.pop()
            buf, buf_line = [], None
        else:
            if buf_line is None and not ch.isspace():
                buf_line = line
            buf.append(ch)
        if ch == "\n":
            line += 1


def css_chunks(path: Path, text: str):
    """(css_text, start_line) pieces: whole .css file, or <style> blocks + inline styles in HTML."""
    if path.suffix.lower() == ".css":
        yield text, 1
        return
    for m in STYLE_BLOCK_RE.finditer(text):
        yield m.group(1), text.count("\n", 0, m.start(1)) + 1
    for m in INLINE_STYLE_RE.finditer(text):
        body = m.group(2) if m.group(2) is not None else m.group(3)
        yield "[inline style]{" + body + "}", text.count("\n", 0, m.start()) + 1


# ---------------------------------------------------------------- collecting
class Values:
    """value -> list of 'file:line' (keeps first-seen order)."""

    def __init__(self):
        self.where: dict[str, list[str]] = defaultdict(list)

    def add(self, value: str, loc: str):
        self.where[" ".join(value.split())].append(loc)

    def render(self, limit: int = 8, indent: str = "    ") -> list[str]:
        items = sorted(self.where.items(), key=lambda kv: -len(kv[1]))
        out = []
        for value, locs in items[:limit]:
            more = f", +{len(locs) - 2} more" if len(locs) > 2 else ""
            count = f" ({len(locs)}x)" if len(locs) > 1 else ""
            out.append(f"{indent}{value}{count}  [{', '.join(locs[:2])}{more}]")
        if len(items) > limit:
            out.append(f"{indent}(+{len(items) - limit} more distinct values)")
        return out


def _norm_color(c: str) -> str:
    c = re.sub(r"\s+", "", c.lower())
    if c.startswith("#") and len(c) in (4, 5):
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c


def _font_names(value: str) -> list[str]:
    names = []
    for part in value.split(","):
        part = part.strip().strip("'\"").strip()
        if part and not part.lower().startswith("var(") and part.lower() not in GENERIC_FONTS:
            names.append(part)
    return names


def _mode(stack: list[str]) -> str:
    at_rules = " ".join(p.lower() for p in stack if p.startswith("@"))
    if "prefers-color-scheme" in at_rules:
        return "dark" if re.search(r"prefers-color-scheme\s*:\s*dark", at_rules) else "light"
    selector = NOT_RE.sub("", stack[-1].lower()) if stack else ""
    return "dark" if "dark" in selector else "light"


def scan_project(name: str, info: dict) -> dict:
    root = Path(str(info.get("path", "")))
    p = {"name": name, "kind": info.get("kind", "?"), "path": str(root), "problems": [],
         "files": 0, "vars": {"light": Values(), "dark": Values()}, "other_scope_vars": 0,
         "font_family": Values(), "google": Values(), "media": Values(),
         "layout": {k: Values() for k in LAYOUT_ORDER}, "colors": defaultdict(list),
         "font_names": set()}
    if not root.is_dir():
        p["problems"].append(f"path not found: {root}")
        return p

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            path = Path(dirpath) / fname
            if path.suffix.lower() not in EXTENSIONS:
                continue
            rel = path.relative_to(root).as_posix()
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    p["problems"].append(f"skipped (over 2 MB): {rel}")
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                p["problems"].append(f"could not read {rel}: {e}")
                log.warning("could not read %s: %s", path, e)
                continue
            p["files"] += 1
            _scan_text(p, path, rel, text)
    return p


def _scan_text(p: dict, path: Path, rel: str, text: str):
    for m in GOOGLE_RE.finditer(text):
        loc = f"{rel}:{text.count(chr(10), 0, m.start()) + 1}"
        query = m.group(0).split("?", 1)[1].replace("&amp;", "&")
        for part in query.split("&"):
            if part.startswith("family="):
                for fam in part[7:].split("|"):  # css v1 uses '|'
                    fam = fam.split(":")[0].replace("+", " ").replace("%20", " ").strip()
                    if fam:
                        p["google"].add(fam, loc)
                        p["font_names"].add(fam)

    for css, start in css_chunks(path, text):
        for item in walk_css(css, start):
            if item[0] == "block":
                prelude = item[1].lower()
                if prelude.startswith("@media") and ("width" in prelude or "height" in prelude):
                    p["media"].add(item[1][6:].strip(), f"{rel}:{item[2]}")
                continue
            loc = f"{rel}:{item[3]}"
            _, prop, value, _, stack = item
            for c in COLOR_RE.findall(value):
                p["colors"][_norm_color(c)].append(loc)
            selector = next((s for s in reversed(stack) if not s.startswith("@")), "")
            if prop.startswith("--"):
                if ":root" in selector.lower():
                    p["vars"][_mode(stack)].add(f"{prop}: {value}", loc)
                else:
                    p["other_scope_vars"] += 1
                if ("font" in prop or "family" in prop) and ("," in value or "'" in value or '"' in value):
                    p["font_names"].update(_font_names(value))
            elif prop == "font-family":
                p["font_family"].add(value, loc)
                p["font_names"].update(_font_names(value))
            elif prop.startswith(("padding", "gap", "row-gap", "column-gap")) or prop in ("max-width", "line-height"):
                bucket = "padding" if prop.startswith("padding") else ("gap" if "gap" in prop else prop)
                p["layout"][bucket].add(value if prop == bucket else f"{prop}: {value}", loc)


# ---------------------------------------------------------------- report text
def _render_project(p: dict) -> list[str]:
    out = [f"=== {p['name']} ({p['kind']}) ===", f"path: {p['path']}"]
    if p["problems"] and p["files"] == 0 and not Path(p["path"]).is_dir():
        out.append(f"PROBLEM: {p['problems'][0]}")
        return out
    out.append(f"html/css files scanned: {p['files']}")
    for mode in ("light", "dark"):
        lines = p["vars"][mode].render(limit=40)
        out.append(f"  :root custom properties ({mode}):" + ("" if lines else " none"))
        out += lines
    if p["other_scope_vars"]:
        out.append(f"  custom properties defined outside :root: {p['other_scope_vars']}")
    out.append("  font-family values:" + ("" if p["font_family"].where else " none"))
    out += p["font_family"].render()
    out.append("  Google Fonts families:" + ("" if p["google"].where else " none"))
    out += p["google"].render()
    for key in LAYOUT_ORDER:
        lines = p["layout"][key].render(limit=6)
        out.append(f"  {key}:" + ("" if lines else " none"))
        out += lines
    out.append("  @media breakpoints:" + ("" if p["media"].where else " none"))
    out += p["media"].render()
    for problem in p["problems"]:
        out.append(f"  PROBLEM: {problem}")
    return out


def _render_common(projects: list[dict]) -> list[str]:
    out = ["=== common patterns (in more than one project) ==="]
    scanned = [p for p in projects if p["files"]]
    if len(scanned) < 2:
        return out + ["  need at least two scanned projects to compare"]
    fonts: dict[str, set] = defaultdict(set)
    display: dict[str, str] = {}
    colors: dict[str, set] = defaultdict(set)
    for p in scanned:
        for f in p["font_names"]:
            fonts[f.lower()].add(p["name"])
            display.setdefault(f.lower(), f)
        for c in p["colors"]:
            colors[c].add(p["name"])
    shared_fonts = sorted((k for k, v in fonts.items() if len(v) > 1), key=lambda k: -len(fonts[k]))
    shared_colors = sorted((k for k, v in colors.items() if len(v) > 1), key=lambda k: -len(colors[k]))
    out.append("  fonts:" + ("" if shared_fonts else " none shared"))
    out += [f"    {display[k]} - {', '.join(sorted(fonts[k]))}" for k in shared_fonts]
    out.append("  colors:" + ("" if shared_colors else " none shared"))
    out += [f"    {c} - {', '.join(sorted(colors[c]))}" for c in shared_colors[:15]]
    if len(shared_colors) > 15:
        out.append(f"    (+{len(shared_colors) - 15} more shared colors)")
    return out


def build_reference(kind: str = "all", projects_file: Path = PROJECTS_FILE) -> str:
    """Return the readable text summary for every project of this kind."""
    kind = (kind or "all").strip().lower()
    if kind not in VALID_KINDS:
        return f"ERROR: kind must be one of {', '.join(VALID_KINDS)} (got {kind!r})."
    try:
        projects = json.loads(Path(projects_file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        log.error("cannot load %s: %s", projects_file, e)
        return f"ERROR: could not load {projects_file}: {e}"

    chosen = {n: i for n, i in projects.items() if kind == "all" or str(i.get("kind", "")).lower() == kind}
    if not chosen:
        kinds = sorted({str(i.get("kind")) for i in projects.values()})
        return f"No projects with kind={kind!r} in projects.json (kinds present: {', '.join(kinds)})."

    scanned = [scan_project(n, i) for n, i in chosen.items()]
    out = [f"Style reference, kind={kind}: {len(scanned)} project(s): {', '.join(chosen)}",
           "Values come from .html/.css files only. [file:line] after each value; 2 locations shown max.", ""]
    for p in scanned:
        out += _render_project(p) + [""]
    out += _render_common(scanned)
    return "\n".join(out)
