#!/usr/bin/env python3
"""Convert HTML problem descriptions to Markdown.

Two HTML formats → one intermediate representation → one Markdown renderer.
"""

import argparse
import html as html_mod
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

# ─── CSS helpers ───────────────────────────────────────────────────────

MONOSPACE_FONTS = {"monospace", "Courier New", "Consolas", "Courier", "Menlo", "Monaco"}
BULLET_FONTS = {"Wingdings", "Wingdings 2", "Wingdings 3"}


def parse_font_family(style: str) -> str | None:
    m = re.search(r"font-family:\s*([^;]+)", style)
    if m:
        return m.group(1).strip().strip("'\"").split(",")[0].strip().strip("'\"")
    return None


def parse_margin_left(style: str) -> str | None:
    m = re.search(r"margin-left:\s*([\d]+px)", style)
    if m:
        return m.group(1)
    m = re.search(r"margin:\s*(?:\S+\s+){3}([\d]+px)", style)
    if m:
        return m.group(1)
    m = re.search(r"margin:\s*\S+\s+([\d]+px)", style)
    if m:
        return m.group(1)
    return None


def parse_font_size(style: str) -> str | None:
    m = re.search(r"font-size:\s*([\d]+px)", style)
    return m.group(1) if m else None


def is_monospace_font(f: str | None) -> bool:
    return bool(f and f.lower() in MONOSPACE_FONTS)


def is_bullet_font(f: str | None) -> bool:
    return bool(f and any(bf.lower() in f.lower() for bf in BULLET_FONTS))


def decode_entities(text: str) -> str:
    return html_mod.unescape(text)


# ─── Unified intermediate representation ────────────────────────────────

@dataclass
class Block:
    pass


@dataclass
class Heading(Block):
    level: int
    text: str


@dataclass
class Paragraph(Block):
    text: str


@dataclass
class CodeBlock(Block):
    lines: list[str] = field(default_factory=list)
    lang: str = ""


@dataclass
class ListBlock(Block):
    items: list[str] = field(default_factory=list)
    ordered: bool = False
    start: int = 1


@dataclass
class TableBlock(Block):
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class HRule(Block):
    pass


# ─── Shared Markdown renderer ──────────────────────────────────────────

def render_blocks(blocks: list[Block]) -> str:
    lines: list[str] = []
    prev_blank = False

    for block in blocks:
        if isinstance(block, Heading):
            if lines and lines[-1] != "":
                lines.append("")
            text = _strip_emphasis_from_heading(block.text)
            lines.append(f"{'#' * block.level} {text}")
            lines.append("")

        elif isinstance(block, Paragraph):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(block.text)
            lines.append("")

        elif isinstance(block, CodeBlock):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"```{block.lang}")
            lines.extend(block.lines)
            lines.append("```")
            lines.append("")

        elif isinstance(block, ListBlock):
            if lines and lines[-1] != "":
                lines.append("")
            for i, item in enumerate(block.items, block.start):
                lines.append(f"{i}. {item}" if block.ordered else f"- {item}")
            lines.append("")

        elif isinstance(block, TableBlock):
            if lines and lines[-1] != "":
                lines.append("")
            rows = block.rows
            if rows:
                max_cols = max(len(r) for r in rows)
                for r in rows:
                    while len(r) < max_cols:
                        r.append("")
                lines.append("| " + " | ".join(rows[0]) + " |")
                lines.append("| " + " | ".join(["---"] * max_cols) + " |")
                for row in rows[1:]:
                    lines.append("| " + " | ".join(row) + " |")
                lines.append("")

        elif isinstance(block, HRule):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append("---")
            lines.append("")

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


# ─── Inline formatting helpers (shared) ─────────────────────────────────

def _merge_adjacent_emphasis(text: str) -> str:
    """Merge adjacent bold/italic spans at the token level."""
    while re.search(r"\*\*[^*]+\*\*\*\*[^*]+\*\*", text):
        text = re.sub(r"\*\*([^*]+)\*\*\*\*([^*]+)\*\*", r"**\1\2**", text)
    return text


def _strip_emphasis_from_heading(text: str) -> str:
    """Remove ** and * markers from heading text."""
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text)


def _escape_md_tags(text: str) -> str:
    """Escape <TAG> patterns."""
    return re.sub(r"<(/?(?:[A-Za-z][A-Za-z0-9_.-]*))>", r"\\<\1\\>", text)


# ─── Inline renderer (shared) ──────────────────────────────────────────
# Used by both Format A and Format B to turn HTML elements into formatted text.

def render_inline(element: Tag, *,
                  force_plain: bool = False,
                  in_heading: bool = False,
                  in_strong: bool = False,
                  skip_bullet: bool = False,
                  format_a: bool = False) -> str:
    """Recursively render inline HTML content to Markdown-formatted text.

    - force_plain: skip monospace backtick wrapping (inside code blocks)
    - in_heading: skip bold/italic wrapping (headings already carry emphasis)
    - in_strong: suppress double-wrapping nested <strong>
    - skip_bullet: skip Wingdings bullet marker span
    - format_a: enable CSS font-family based classification for Format A
    """
    parts: list[str] = []
    _skip = skip_bullet

    for child in element.children:
        if isinstance(child, NavigableString):
            text = str(child)
            text = decode_entities(text)
            if not in_heading and not force_plain:
                text = _escape_md_tags(text)
            parts.append(text)
            continue

        if not isinstance(child, Tag):
            continue

        tag = child.name

        if tag in ("strong", "b"):
            if in_heading:
                parts.append(render_inline(child, in_heading=True, format_a=format_a))
            elif in_strong:
                parts.append(render_inline(child, in_strong=True, format_a=format_a))
            else:
                inner = render_inline(child, in_strong=True, format_a=format_a).strip()
                if inner:
                    parts.append(f"**{inner}**")

        elif tag in ("em", "i"):
            if in_heading:
                parts.append(render_inline(child, in_heading=True, format_a=format_a))
            else:
                inner = render_inline(child, format_a=format_a).strip()
                if inner:
                    parts.append(f"*{inner}*")

        elif tag == "code":
            text = child.get_text()
            parts.append(f"`{decode_entities(text)}`")

        elif tag == "a":
            href = child.get("href", "")
            cls = " ".join(child.get("class", []))
            if "anchor" in cls:
                continue
            inner = render_inline(child, in_heading=in_heading, format_a=format_a).strip()
            if href and inner:
                parts.append(f"[{inner}]({href})")
            else:
                parts.append(inner)

        elif tag == "br":
            parts.append("\n")

        elif tag == "span":
            cls = " ".join(child.get("class", []))
            if "Cherry-InlineMath" in cls:
                # Extract LaTeX source from annotation, not the decomposed spans
                ann = child.select_one('annotation[encoding="application/x-tex"]')
                if ann:
                    parts.append(f"${ann.get_text(strip=True)}$")
                else:
                    parts.append(decode_entities(child.get_text()))
                continue
            if "katex" in cls:
                # Skip inner KaTeX spans (handled by Cherry-InlineMath above)
                continue

            if format_a:
                style = child.get("style", "")
                font = parse_font_family(style)
                if _skip and is_bullet_font(font):
                    _skip = False
                    continue
                if is_bullet_font(font):
                    continue
                inner = render_inline(child, force_plain=force_plain,
                                      in_heading=in_heading, in_strong=in_strong,
                                      format_a=True)
                if not force_plain and is_monospace_font(font):
                    inner = inner.strip()
                    if inner:
                        parts.append(f"`{inner}`")
                        continue
                parts.append(inner)
            else:
                parts.append(render_inline(child, in_heading=in_heading,
                                           in_strong=in_strong))

        elif tag in ("img", "image"):
            alt = child.get("alt", "")
            src = child.get("src", "")
            parts.append(f"![{alt}]({src})")

        else:
            parts.append(render_inline(child, force_plain=force_plain,
                                       in_heading=in_heading, in_strong=in_strong,
                                       format_a=format_a))

    # Merge adjacent bold/italic tokens at parse time
    merged = []
    for part in parts:
        if merged and merged[-1].endswith("**") and part.startswith("**"):
            merged[-1] = merged[-1][:-2] + part[2:]
        elif merged and merged[-1].endswith("*") and not merged[-1].endswith("**") and part.startswith("*") and not part.startswith("**"):
            merged[-1] = merged[-1][:-1] + part[1:]
        else:
            merged.append(part)
    text = "".join(merged)
    if skip_bullet:
        text = re.sub(r"^l[\s ]*", "", text)
    return text


# ─── Format A helpers ──────────────────────────────────────────────────
# Detect the "shape" of a <p> element via CSS styles

def _find_first_span_font(element: Tag) -> str | None:
    for child in element.descendants:
        if isinstance(child, Tag) and child.name == "span":
            font = parse_font_family(child.get("style", ""))
            if font:
                return font
    return None


def _is_all_monospace(element: Tag) -> bool:
    has_mono = False
    for child in element.descendants:
        if isinstance(child, Tag) and child.name == "span":
            font = parse_font_family(child.get("style", ""))
            if font:
                if is_monospace_font(font):
                    has_mono = True
                elif not is_bullet_font(font):
                    return False
    return has_mono


# ─── Code detection (Format A) ─────────────────────────────────────────

_CODE_KW1 = re.compile(
    r"^(create|insert|select|drop|alter|begin|commit|abort|rollback|update|delete)\b",
    re.IGNORECASE)
_CODE_KW2 = re.compile(r"^(show|explain|set|crash|\./bin/)\b", re.IGNORECASE)
_CODE_OTHER = re.compile(r"^\| |::|^std::|^#include|^-- |^// ")

_SECTION_LABEL = re.compile(
    r"^(期待|期望|预期)输出[：:]|"
    r"^测试(点|输出|过程|语句|示例)[：: ]|"
    r"^(测试|提示|说明|注意|参考|关于|本题|本测试|本题目)"
)


def _looks_like_code(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    return bool(_CODE_KW1.search(text) or _CODE_KW2.search(text) or _CODE_OTHER.search(text))


def _is_section_break(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if text.startswith("**") and text.endswith("**"):
        return True
    plain = re.sub(r"\*\*", "", text).strip()
    if _SECTION_LABEL.match(plain) or _SECTION_LABEL.match(text):
        return True
    if re.match(r"^\d+[、．.]\s*\S", text) and len(text) <= 30:
        return True
    if len(text) > 60 and len(re.findall(r"[一-鿿]", text)) > 15:
        return True
    return False


# ─── Format B: Cherry Markdown → Blocks ─────────────────────────────────

def build_blocks_format_b(content_div: Tag, title: str) -> list[Block]:
    blocks: list[Block] = []
    if title:
        blocks.append(Heading(1, title))

    cherry = content_div.select_one(".cherry-previewer")
    if not cherry:
        return blocks
    _walk_format_b(cherry, blocks)
    return blocks


def _walk_format_b(element: Tag, blocks: list[Block]):
    for child in element.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                blocks.append(Paragraph(decode_entities(text)))
            continue
        if not isinstance(child, Tag):
            continue

        tag = child.name

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = render_inline(child, in_heading=True).strip()
            if text:
                blocks.append(Heading(int(tag[1]), text))

        elif tag == "p":
            text = render_inline(child).strip()
            if text:
                blocks.append(Paragraph(text))

        elif tag == "ul":
            items = []
            for li in child.select(":scope > li"):
                text = render_inline(li).strip()
                if text:
                    items.append(text)
            if items:
                blocks.append(ListBlock(items=items, ordered=False))

        elif tag == "ol":
            items = []
            start = int(child.get("start", 1))
            for li in child.select(":scope > li"):
                text = render_inline(li).strip()
                if text:
                    items.append(text)
            if items:
                blocks.append(ListBlock(items=items, ordered=True, start=start))

        elif tag in ("pre", "div") and (tag == "pre" or child.get("data-type") == "codeBlock"):
            lang = ""
            code = child.find("code") if tag == "pre" else child.find("pre")
            if code:
                for cls in code.get("class", []):
                    if cls.startswith("language-"):
                        lang = cls.replace("language-", "")
                text = code.get_text()
            elif tag == "pre":
                text = child.get_text()
            else:
                pre = child.find("pre")
                text = pre.get_text() if pre else child.get_text()
            text = decode_entities(text)
            # Remove leading/trailing blank lines
            text = text.strip()
            if text:
                blocks.append(CodeBlock(lines=text.split("\n"), lang=lang))

        elif tag == "table":
            rows = []
            for tr in child.select("thead tr, tbody tr, tr"):
                row = [_escape_md_tags(decode_entities(td.get_text(" ", strip=True)))
                       for td in tr.find_all(["th", "td"])]
                if row:
                    rows.append(row)
            if rows:
                blocks.append(TableBlock(rows=rows))

        elif tag == "hr":
            blocks.append(HRule())

        elif tag == "div":
            if "cherry-table-container" in child.get("class", []):
                table = child.find("table")
                if table:
                    rows = []
                    for tr in table.select("thead tr, tbody tr, tr"):
                        row = [_escape_md_tags(decode_entities(td.get_text(" ", strip=True)))
                               for td in tr.find_all(["th", "td"])]
                        if row:
                            rows.append(row)
                    if rows:
                        blocks.append(TableBlock(rows=rows))
            else:
                _walk_format_b(child, blocks)

        elif tag == "script":
            continue

        else:
            text = child.get_text(" ", strip=True)
            if text:
                blocks.append(Paragraph(decode_entities(text)))


# ─── Format A: Raw HTML → Blocks ────────────────────────────────────────

def build_blocks_format_a(content_div: Tag, title: str) -> list[Block]:
    blocks: list[Block] = []
    if title:
        blocks.append(Heading(1, title))

    expect_output = False  # flag: next content auto-enters code block

    for child in content_div.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                blocks.append(Paragraph(decode_entities(text)))
            continue

        if not isinstance(child, Tag):
            continue

        tag = child.name

        # ── <p> elements: classify by CSS styles ──
        if tag == "p":
            _classify_a_paragraph(child, blocks, expect_output)
            # Update expect_output after processing
            if _is_output_label(_render_para(child)):
                expect_output = True
            elif _is_section_break(_render_para(child)):
                expect_output = False

        # ── <pre> ──
        elif tag == "pre":
            text = _get_text_with_br(child)
            lines = [l for l in decode_entities(text).strip().split("\n")]
            if lines:
                blocks.append(CodeBlock(lines=lines))

        # ── Headings ──
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            first_font = _find_first_span_font(child)
            style = child.get("style", "")
            ml = parse_margin_left(style)
            if is_bullet_font(first_font) and ml == "28px":
                # Heading used as bullet item (problem 5)
                text = render_inline(child, skip_bullet=True, force_plain=True,
                                     format_a=True).strip()
                blocks.append(ListBlock(items=[text]))
            else:
                text = render_inline(child, in_heading=True,
                                     format_a=True).strip()
                if text:
                    blocks.append(Heading(int(tag[1]), text))

        # ── Tables ──
        elif tag == "table":
            rows = []
            for tr in child.find_all("tr"):
                row = [_escape_md_tags(decode_entities(td.get_text(" ", strip=True)))
                       for td in tr.find_all(["th", "td"])]
                if row:
                    rows.append(row)
            if rows:
                blocks.append(TableBlock(rows=rows))

        # ── Nested divs ──
        elif tag == "div":
            for inner in child.children:
                if isinstance(inner, Tag) and inner.name == "p":
                    _classify_a_paragraph(inner, blocks, expect_output)
                    if _is_output_label(_render_para(inner)):
                        expect_output = True
                    elif _is_section_break(_render_para(inner)):
                        expect_output = False
                elif isinstance(inner, Tag) and inner.name == "pre":
                    text = _get_text_with_br(inner)
                    lines = [l for l in decode_entities(text).strip().split("\n")]
                    if lines:
                        blocks.append(CodeBlock(lines=lines))

        elif tag == "script":
            continue

        else:
            text = child.get_text(" ", strip=True)
            if text:
                blocks.append(Paragraph(decode_entities(text)))

    return blocks


def _render_para(p: Tag) -> str:
    """Render a <p> to plain text (no bold/code wrapping) for classification."""
    all_mono = _is_all_monospace(p)
    return render_inline(p, force_plain=all_mono, format_a=True).strip()


def _is_output_label(text: str) -> bool:
    """Check if text is '期待输出：' / '期望输出：' label."""
    plain = re.sub(r"\*\*", "", text)
    return bool(re.match(r"^(期待|期望|预期)输出[：:]", plain))


def _classify_a_paragraph(p: Tag, blocks: list[Block], expect_output: bool):
    """Classify a single <p> element and append the appropriate Block."""
    style = p.get("style", "")
    ml = parse_margin_left(style)
    fs = parse_font_size(style)

    # ── Heading via font-size ──
    if fs in ("20px", "21px"):
        text = render_inline(p, force_plain=_is_all_monospace(p),
                             in_heading=True, format_a=True).strip()
        if text:
            blocks.append(Heading(2, text))
        return

    # ── Wingdings bullet ──
    first_font = _find_first_span_font(p)
    has_bullet = is_bullet_font(first_font)
    raw_text = p.get_text().strip()
    if not raw_text:
        return
    if has_bullet:
        after = re.sub(r"^l[\s ]*", "", raw_text).strip()
        if not after:
            return
        text = render_inline(p, skip_bullet=True, format_a=True).strip()
        if not text:
            return
        # If bullet content looks like code (SQL), go into code block
        if _looks_like_code(after):
            if blocks and isinstance(blocks[-1], CodeBlock) and not blocks[-1].lang:
                blocks[-1].lines.append(text)
            else:
                blocks.append(CodeBlock(lines=[text]))
            return
        blocks.append(ListBlock(items=[text]))
        return

    # ── Monospace code signature (indented) ──
    if ml in ("28px", "48px") and _is_all_monospace(p):
        text = render_inline(p, force_plain=True, format_a=True)
        blocks.append(CodeBlock(lines=[text]))
        return

    # ── Indented paragraph (list continuation or standalone) ──
    if ml == "28px":
        text = render_inline(p, format_a=True).strip()
        if text:
            # Attach to previous list if it exists, otherwise standalone paragraph
            if blocks and isinstance(blocks[-1], ListBlock):
                blocks[-1].items[-1] += " " + text
            else:
                blocks.append(Paragraph(text))
        return

    if ml == "48px":
        text = render_inline(p, format_a=True).strip()
        if text:
            blocks.append(Paragraph(text))
        return

    # ── Regular paragraph ──
    all_mono = _is_all_monospace(p)
    text = render_inline(p, force_plain=all_mono,
                         format_a=True).strip()
    if not text:
        return

    # Code detection: starts code block, or continues existing one (sticky)
    if _looks_like_code(text) or expect_output:
        # Check if we should close an existing sticky code block first
        if (blocks and isinstance(blocks[-1], CodeBlock) and not blocks[-1].lang
                and _is_section_break(text)):
            # Section break inside sticky block: close it, emit as paragraph
            blocks.append(Paragraph(text))
        elif blocks and isinstance(blocks[-1], CodeBlock) and not blocks[-1].lang:
            blocks[-1].lines.append(text)
        else:
            blocks.append(CodeBlock(lines=[text]))
        return

    # Non-code line: if we're in a sticky code block, section breaks close it
    if blocks and isinstance(blocks[-1], CodeBlock) and not blocks[-1].lang:
        if _is_section_break(text):
            blocks.append(Paragraph(text))
            return

    blocks.append(Paragraph(text))


def _get_text_with_br(element) -> str:
    parts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag) and child.name == "br":
            parts.append("\n")
        elif isinstance(child, Tag):
            parts.append(_get_text_with_br(child))
    return "".join(parts)


# ─── Main ──────────────────────────────────────────────────────────

def detect_format(content_div: Tag) -> str:
    if content_div.select_one(".cherry-previewer"):
        return "B"
    return "A"


def convert_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    title_elem = soup.select_one("h4.cgcode_css-tt3ivf-Title")
    title = title_elem.get_text(strip=True) if title_elem else ""

    content_div = soup.select_one(".cgProblemContentClass")
    if not content_div:
        desc = soup.select_one(".cgcode_description__2b0C")
        if desc:
            content_div = desc.select_one(".cgcode_content__1Y2H")
        if not content_div:
            return ""

    fmt = detect_format(content_div)

    if fmt == "B":
        blocks = build_blocks_format_b(content_div, title)
    else:
        blocks = build_blocks_format_a(content_div, title)

    return render_blocks(blocks)


def main():
    parser = argparse.ArgumentParser(description="Convert HTML problem descriptions to Markdown")
    parser.add_argument("input", nargs="?", type=Path, help="Input HTML file (default: stdin)")
    parser.add_argument("-o", "--output", type=Path, help="Output markdown file (default: stdout)")
    args = parser.parse_args()

    html_content = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    markdown = convert_html(html_content)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()
