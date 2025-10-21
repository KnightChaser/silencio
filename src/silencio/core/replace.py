# src/silencio/core/replace.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import ahocorasick


@dataclass
class InventoryRow:
    """
    A single row in the inventory.
    Represents an item to be redacted, along with its metadata.
    """

    number: int
    item: str
    code: str
    desc: str
    aliases: List[str]


@dataclass
class Match:
    """
    A single match found in the text.
    """

    start: int
    end: int  # exclusive
    number: int
    code: str
    desc: str
    surface: str  # exact matched text


def _build_automation(rows: List[InventoryRow]) -> ahocorasick.Automaton:
    """
    Build an Aho-Corasick automaton from the inventory rows.

    Creates a trie-based automaton optimized for multi-pattern matching. Each row's item
    and aliases are added as patterns, storing metadata for replacement.
    """
    A = ahocorasick.Automaton()
    for row in rows:
        patterns = {row.item, *row.aliases}
        for pattern in patterns:
            if not pattern:
                continue
            # Store row index + canonical pattern for replacement bookkeeping
            A.add_word(pattern, (row.number, row.code, row.desc, pattern))
    A.make_automaton()
    return A


def _collect_matches(A: ahocorasick.Automation, text: str) -> List[Match]:
    """
    Collect all matches in the given text using the provided Aho-Corasick automaton.

    Iterates through the text with the automaton, creating Match objects for each found pattern.
    Matches include position, number, code, description, and surface text.
    """
    found: List[Match] = []
    for end_index, payload in A.iter(text):
        number, code, desc, pattern = payload
        start_index = end_index - len(pattern) + 1
        found.append(
            Match(
                start=start_index,
                end=end_index + 1,
                number=number,
                code=code,
                desc=desc,
                surface=pattern,
            )
        )
    return found


def _select_leftmost_longest(matches: List[Match]) -> List[Match]:
    """
    Select non-overlapping matches using the leftmost-longest strategy.

    Sorts matches by start position and length (longest first), then greedily selects
    matches that don't overlap with previously chosen ones. This ensures no conflicts
    in replacement.
    """
    matches.sort(
        key=lambda m: (m.start, -(m.end - m.start))
    )  # Sort by start, then by length (longest first)
    selected: List[Match] = []
    last_end = -1
    for match in matches:
        if match.start >= last_end:
            # No overlap with previous match
            selected.append(match)
            last_end = match.end
        # else overlap: skip (shorter or later-starting)
    return selected


def _collect_matches(A: ahocorasick.Automation, text: str) -> List[Match]:
    """
    Collect all matches in the given text using the provided Aho-Corasick automaton.
    """
    found: List[Match] = []
    for end_index, payload in A.iter(text):
        number, code, desc, pattern = payload
        start_index = end_index - len(pattern) + 1
        found.append(
            Match(
                start=start_index,
                end=end_index + 1,
                number=number,
                code=code,
                desc=desc,
                surface=pattern,
            )
        )
    return found


def _select_leftmost_longest(matches: List[Match]) -> List[Match]:
    """
    Select non-overlapping matches using the leftmost-longest strategy.
    Pick the matches greedily (earliest start, longest length).
    """
    matches.sort(
        key=lambda m: (m.start, -(m.end - m.start))
    )  # Sort by start, then by length (longest first)
    selected: List[Match] = []
    last_end = -1
    for match in matches:
        if match.start >= last_end:
            # No overlap with previous match
            selected.append(match)
            last_end = match.end
        # else overlap: skip (shorter or later-starting)
    return selected


def apply_numbered_redactions(
    text: str, rows: List[InventoryRow]
) -> Tuple[str, List[Match]]:
    """
    Apply numbered redactions to the input text based on the provided inventory rows.

    For each item in the inventory, replaces all occurrences in the text with a formatted
    redaction tag like [REDACTED(#N): code, description], where N is the item's number.
    Uses Aho-Corasick automaton for efficient multi-pattern string matching and employs
    a leftmost-longest strategy to select non-overlapping matches.

    Args:
        text: The original text to redact.
        rows: List of InventoryRow objects representing items to redact.

    Returns:
        A tuple containing the redacted text and a list of Match objects for the applied redactions.
    """
    if not rows:
        return text, []

    A = _build_automation(rows)
    matches = _collect_matches(A, text)
    if not matches:
        return text, []

    selected = _select_leftmost_longest(matches)

    # Replace right-to-left so indices remain stable.
    out = []
    cursor = len(text)
    for match in reversed(selected):
        out.append(text[match.end : cursor])
        out.append(f"[REDACTED(#{match.number}): {match.code}, {match.desc}]")
        out.append(text[match.start : match.start])  # Append text before match
        cursor = match.start

    out.append(text[0:cursor])
    redacted_text = "".join(reversed(out))
    return redacted_text, selected
