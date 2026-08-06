#!/usr/bin/env python3
"""Generate the one-page technical CV PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Malek_Hassan_CV.pdf"
MIRROR = ROOT / "CV.pdf"

INK = colors.HexColor("#111111")
SLATE = colors.HexColor("#3d4450")
MUTED = colors.HexColor("#5c6472")
HAIRLINE = colors.HexColor("#b9bec8")

CONTENT_WIDTH = 184 * mm
DATE_WIDTH = 34 * mm

# Typeface families available on macOS, keyed by the name passed to build().
# Each maps role -> (file, subfont index within the .ttc).
FONT_FAMILIES = {
    "charter": {
        "file": "/System/Library/Fonts/Supplemental/Charter.ttc",
        "roles": {"regular": 0, "italic": 1, "boldItalic": 2, "bold": 3, "black": 5},
    },
    "avenir": {
        "file": "/System/Library/Fonts/Avenir Next.ttc",
        "roles": {"regular": 7, "italic": 4, "boldItalic": 3, "bold": 2, "black": 0},
    },
    "helvetica": {"file": None, "roles": {}},
}

DEFAULT_FAMILY = "charter"
_DEFAULT = object()


def register_family(family):
    """Register a family and return its role -> PostScript-name mapping.

    Falls back to the built-in Helvetica set when the TTF/TTC is unavailable,
    so the script still runs off a machine that lacks the system font.
    """
    fallback = {
        "regular": "Helvetica", "italic": "Helvetica-Oblique",
        "bold": "Helvetica-Bold", "boldItalic": "Helvetica-BoldOblique",
        "black": "Helvetica-Bold",
    }
    spec = FONT_FAMILIES.get(family)
    if not spec or not spec["file"] or not Path(spec["file"]).exists():
        return fallback

    names = {}
    try:
        for role, index in spec["roles"].items():
            name = f"{family}-{role}"
            pdfmetrics.registerFont(TTFont(name, spec["file"], subfontIndex=index))
            names[role] = name
    except Exception:
        return fallback

    names.setdefault("black", names["bold"])
    pdfmetrics.registerFontFamily(
        family, normal=names["regular"], bold=names["bold"],
        italic=names["italic"], boldItalic=names["boldItalic"],
    )
    return names


def make_styles(f):
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name", parent=base["Normal"], fontName=f["black"],
            fontSize=23, leading=23.5, spaceAfter=3.5, textColor=INK,
        ),
        "headline": ParagraphStyle(
            "Headline", parent=base["Normal"], fontName=f["bold"],
            fontSize=9.2, leading=11, spaceAfter=3.5, textColor=SLATE,
        ),
        "contact": ParagraphStyle(
            "Contact", parent=base["Normal"], fontName=f["regular"],
            fontSize=7.2, leading=9.2, textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "Section", parent=base["Normal"], fontName=f["bold"],
            fontSize=8.6, leading=10, spaceBefore=7, spaceAfter=2.5,
            textColor=INK, textTransform="uppercase",
        ),
        "entry": ParagraphStyle(
            "Entry", parent=base["Normal"], fontName=f["bold"],
            fontSize=9.2, leading=10.8, textColor=INK,
        ),
        "date": ParagraphStyle(
            "Date", parent=base["Normal"], fontName=f["bold"],
            fontSize=7.8, leading=10.4, alignment=TA_RIGHT, textColor=SLATE,
        ),
        "sub": ParagraphStyle(
            "Sub", parent=base["Normal"], fontName=f["italic"],
            fontSize=8.0, leading=9.8, textColor=MUTED,
        ),
        "subright": ParagraphStyle(
            "SubRight", parent=base["Normal"], fontName=f["italic"],
            fontSize=8.0, leading=9.8, alignment=TA_RIGHT, textColor=MUTED,
        ),
        "link": ParagraphStyle(
            "Link", parent=base["Normal"], fontName=f["regular"],
            fontSize=7.5, leading=9.4, alignment=TA_RIGHT, textColor=SLATE,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"], fontName=f["regular"],
            fontSize=8.2, leading=10.2, spaceAfter=1.4, textColor=colors.HexColor("#222222"),
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"], fontName=f["regular"],
            fontSize=8.2, leading=10.3, leftIndent=9, bulletIndent=1.5,
            spaceBefore=1.2, spaceAfter=0.6, textColor=colors.HexColor("#222222"),
        ),
        "note": ParagraphStyle(
            "Note", parent=base["Normal"], fontName=f["regular"],
            fontSize=6.6, leading=8, textColor=colors.HexColor("#6b7280"),
            spaceBefore=4,
        ),
    }


def section(story, styles, title):
    """Section heading followed by a hairline rule."""
    story.append(Paragraph(title, styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE, spaceAfter=3))


def split_row(left, right, left_style, right_style, right_width=DATE_WIDTH):
    """One line with content flush left and a date/location flush right."""
    table = Table(
        [[Paragraph(left, left_style), Paragraph(right, right_style)]],
        colWidths=[CONTENT_WIDTH - right_width, right_width],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def bullet(styles, text):
    return Paragraph(text, styles["bullet"], bulletText="•")


def entry(styles, title, date, subtitle, side, bullets, side_style="sub", side_width=DATE_WIDTH):
    block = [split_row(title, date, styles["entry"], styles["date"])]
    if subtitle or side:
        block.append(split_row(subtitle, side, styles["sub"], styles[side_style], side_width))
    block.extend(bullet(styles, item) for item in bullets)
    block.append(Spacer(1, 3.5))
    return KeepTogether(block)


def build(family=DEFAULT_FAMILY, output=None, mirror=_DEFAULT):
    output = Path(output) if output else OUTPUT
    mirror = MIRROR if mirror is _DEFAULT else (Path(mirror) if mirror else None)
    output.parent.mkdir(parents=True, exist_ok=True)
    f = register_family(family)
    styles = make_styles(f)
    doc = SimpleDocTemplate(
        str(output), pagesize=A4,
        leftMargin=13 * mm, rightMargin=13 * mm,
        topMargin=10 * mm, bottomMargin=9 * mm,
        title="Malek Hassan - Technical Resume",
        author="Malek Hassan",
        subject="AI systems engineering and open-source development resume",
    )
    story = []

    # ── Header ──
    story.append(Paragraph("Malek Hassan", styles["name"]))
    story.append(Paragraph(
        "AI Systems Engineer&nbsp; | &nbsp;Open-Source Developer&nbsp; | &nbsp;"
        "Computer Science at CODE University of Applied Sciences, Berlin",
        styles["headline"],
    ))
    story.append(Paragraph(
        "Berlin, Germany&nbsp; | &nbsp;"
        "<link href='mailto:malek.hassan@code.berlin'>malek.hassan@code.berlin</link>&nbsp; | &nbsp;"
        "+49 176 32469907&nbsp; | &nbsp;"
        "<link href='https://linkedin.com/in/malek-hussein'>linkedin.com/in/malek-hussein</link>&nbsp; | &nbsp;"
        "<link href='https://github.com/Malek1414'>github.com/Malek1414</link>&nbsp; | &nbsp;"
        "<link href='https://malek1414.github.io'>malek1414.github.io</link>",
        styles["contact"],
    ))
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width="100%", thickness=1.4, color=INK, spaceAfter=0.9))
    story.append(HRFlowable(width="100%", thickness=0.4, color=HAIRLINE))

    # ── Education ──
    section(story, styles, "Education")
    story.append(entry(
        styles, "CODE University of Applied Sciences", "2026 - Present",
        "B.Sc. Software Engineering - final year", "Berlin, Germany",
        ["Transferred from RWTH Aachen University to complete the final year of the degree in Berlin, moving to a project-based curriculum built around shipping real software."],
        side_style="subright",
    ))
    story.append(entry(
        styles, "RWTH Aachen University", "Oct 2023 - 2026",
        "B.Sc. Computer Science - first two years", "Aachen, Germany",
        [], side_style="subright",
    ))

    # ── Experience ──
    section(story, styles, "Experience")
    story.append(entry(
        styles, "African Arab International Bank", "Jul 2025 - Sep 2025",
        "Software Engineering Intern, Digital Factory", "Cairo, Egypt",
        [
            "Built an end-to-end banking support assistant with HTML, CSS, JavaScript/TypeScript, URL-scraped public knowledge, and locally hosted Ollama inference.",
            "Won adoption of the concept by the development team and documented its retrieval, inference, and data flow for the bank's internal review process.",
        ],
        side_style="subright",
    ))
    story.append(entry(
        styles, "RWTH Aachen University", "Oct 2023 - Jan 2024",
        "Student Technical Support, CS Peer Assistance", "Aachen, Germany",
        ["Supported peers with Java debugging, Git/GitHub workflows, and LaTeX document structure."],
        side_style="subright",
    ))

    # ── Projects ──
    section(story, styles, "Selected Projects")
    story.append(entry(
        styles, "MOZCODE - Symbol-Level Context Engine for Coding Agents", "2026",
        "Creator and maintainer | MIT licensed",
        "<link href='https://github.com/Malek1414/MOZCODE'>github.com/Malek1414/MOZCODE</link>",
        [
            "Built a local MCP server for Claude Code, Codex, and OpenAI models that uses tree-sitter ASTs to return requested symbols and structural outlines instead of entire source files.",
            "Implemented grouped code search, AST-anchored edits with parse validation, graceful fallbacks, and cached read-only SQLite/PostgreSQL schema introspection.",
            "Instrumented an append-only JSONL ledger and self-contained SVG dashboard; measured an estimated 1,749,436 input tokens avoided across 938 optimized calls, with 80% average payload reduction versus disclosed whole-file/plain-grep baselines.",
        ],
        side_style="link", side_width=48 * mm,
    ))
    story.append(entry(
        styles, "Second Brain - End-to-End RAG Knowledge System", "2025",
        "Personal knowledge capture and cited retrieval", "Node.js | ChromaDB | Claude API",
        [
            "Built one retrieval loop from voice/text capture through embedding and ChromaDB indexing to structured Markdown synchronization with an Obsidian vault.",
            "Implemented an Animus chat interface that retrieves passages from the user's corpus and generates Claude answers with citations back to the source notes.",
            "Integrated Node.js, Express, LangChain/LlamaIndex, ChromaDB, the Anthropic Claude API, Obsidian vault sync, and a vanilla JavaScript/Canvas interface.",
        ],
        side_style="subright", side_width=44 * mm,
    ))

    # ── Skills ──
    section(story, styles, "Technical Skills")
    skills = [
        ("Languages", "TypeScript, JavaScript, Python, Java, SQL, C, HTML/CSS"),
        ("AI and systems", "RAG, Model Context Protocol, tree-sitter, vector search, prompt engineering, Claude API, Ollama"),
        ("Backend and data", "Node.js, Express, PostgreSQL, SQLite, Supabase, ChromaDB, REST APIs"),
        ("Frontend and visualization", "React, Next.js, Vite, D3.js, Recharts, Tailwind CSS, Canvas, Framer Motion"),
        ("Developer tooling", "Git/GitHub, Vitest, esbuild, PDF processing, command-line workflows"),
    ]
    for label, values in skills:
        story.append(Paragraph(
            f"<font name='{f['bold']}'>{label}:</font> {values}", styles["body"]))

    # ── Certifications ──
    section(story, styles, "Certifications")
    story.append(Paragraph(
        "Anthropic: Introduction to Model Context Protocol; Model Context Protocol - Advanced Topics; "
        "Introduction to Agent Skills; Introduction to Subagents (May 2026)",
        styles["body"],
    ))

    # ── Leadership ──
    section(story, styles, "Leadership")
    story.append(entry(
        styles, "Organising Committee Head, Model United Nations", "Sep 2022 - Jun 2023",
        "High school leadership role", "Cairo, Egypt",
        [
            "Led the organising committee across sales, marketing, logistics, and administration, and delivered a keynote to an audience of 300+.",
            "Improved the event's operational performance by 20% year over year.",
        ],
        side_style="subright",
    ))

    # ── Awards ──
    section(story, styles, "Awards and Honors")
    story.append(Paragraph(
        f"<font name='{f['bold']}'>State Champion, Basketball</font> - won a national/state "
        "championship title in the youth division.",
        styles["body"],
    ))

    story.append(Paragraph(
        "MOZCODE figures are estimates against local counterfactual baselines, not billing data. Snapshot: 6 Aug 2026.",
        styles["note"],
    ))

    doc.build(story)

    if mirror:
        mirror.write_bytes(output.read_bytes())
        print(mirror)
    print(output)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    build(
        family=args[0] if args else DEFAULT_FAMILY,
        output=args[1] if len(args) > 1 else None,
        mirror=None if len(args) > 1 else MIRROR,
    )
