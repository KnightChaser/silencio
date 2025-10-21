# app/util/formatting.py
import re
from typing import List
from silencio.core.replace import Match

# Matches numbered tag blocks like: [REDACTED(#12): (3)(B)(c), internal domain]
TAG = re.compile(
    r"\[REDACTED(?:\(#([0-9]+)\))?: \(([0-9]+)\)\(([A-Z])\)(?:\(([a-z])\))?, (.*?)\]"
)


def colorize_redaction_tags(md_text: str) -> str:
    """
    Colorizes redaction tags in markdown text for Streamlit rendering.

    Searches for redaction tag patterns in the input text and wraps them in HTML spans
    with red color and bold font weight for visual emphasis in the UI.
    """
    return TAG.sub(
        lambda m: f"<span style='color:red; font-weight:bold'>{m.group(0)}</span>",
        md_text,
    )


def segments_from_matches(text: str, matches: List[Match], code_bg: str = "#FDECEA", code_fg: str = "#7A0010"):
    """
    Given text and a list of matches, returns a list of segments for annotated text display.

    Each segment is either a string (for plain text) or a tuple (for annotated matches).
    The tuple contains (surface_text, code, background_color, foreground_color).
    """
    segments = []
    cursor = 0
    for match in sorted(matches, key=lambda x: x.start):
        if cursor < match.start:
            segments.append(text[cursor : match.start])  # untouched text
        # label is the policy code only (per target)
        segments.append(
            (
                match.surface,
                match.code,
                code_bg,
                code_fg,
            )
        )
        cursor = match.end
    if cursor < len(text):
        segments.append(text[cursor:])  # remaining text
    return segments
