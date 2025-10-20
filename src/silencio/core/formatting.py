# src/silencio/core/formatting.py
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
