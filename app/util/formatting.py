# app/util/formatting.py
import re

# Matches numbered tag blocks like: [REDACTED(#12): (3)(B)(c), internal domain]
TAG = re.compile(
    r"\[REDACTED(?:\(#([0-9]+)\))?: \(([0-9]+)\)\(([A-Z])\)(?:\(([a-z])\))?, (.*?)\]"
)


def colorize_redaction_tags(md_text: str) -> str:
    """
    Colorizes redaction tags for Streamlit markdown rendering.
    """
    return TAG.sub(
        lambda m: f"<span style='color:red; font-weight:bold'>{m.group(0)}</span>",
        md_text,
    )


def segments_from_matches(text: str, matches, code_bg="#FDECEA", code_fg="#7A0010"):
    """
    Given text and a list of matches, returns a list of segments where each segment is either
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
