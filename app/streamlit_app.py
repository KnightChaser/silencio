# app/streamlit_app.py
import streamlit as st
from annotated_text import annotated_text

from util.formatting import colorize_redaction_tags, segments_from_matches
from silencio.core.redact import enumerate_confidential_items
from silencio.core.replace import apply_numbered_redactions, InventoryRow
from silencio.settings import get_model_name


st.set_page_config(page_title="silencio — a document redactor", layout="wide")
st.title("silencio - a document redactor")

user_input = st.text_area(
    "Input text",
    height=320,
    placeholder="Paste text or message...",
)

if st.button("Run", type="primary"):
    if not user_input.strip():
        st.warning("Type or paste something first.")
        st.stop()

    with st.spinner(f"Running {get_model_name()} to enumerate sensitive items..."):
        inventory = enumerate_confidential_items(user_input)

    # Number rows deterministically, sort by (code, item)
    items_sorted = sorted(inventory.items, key=lambda r: (r.code, r.item))
    rows = [
        InventoryRow(
            number=index + 1,
            item=row.item,
            code=row.code,
            desc=row.desc,
            aliases=row.aliases or [],
        )
        for index, row in enumerate(items_sorted)
    ]

    with st.spinner("Applying redactions using Aho-Corasick algorithm..."):
        redacted, matches = apply_numbered_redactions(user_input, rows)

    st.subheader("Highlighted items")
    segments = segments_from_matches(user_input, matches)
    annotated_text(*segments)

    st.subheader("Redacted Output")
    st.markdown(
        colorize_redaction_tags(redacted),
        unsafe_allow_html=True,
        help="Tags are rendered in bold red for quick identification.",
    )

    st.subheader("Inventory (numbered)")
    table = [
        {
            "#": row.number,
            "item": row.item,
            "code": row.code,
            "desc": row.desc,
            "aliases": ", ".join(row.aliases),
            "count": sum(1 for match in matches if match.number == row.number),
        }
        for row in rows
    ]
    st.dataframe(table, width="stretch")
