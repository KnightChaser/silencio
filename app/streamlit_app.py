# app/streamlit_app.py
import streamlit as st
from silencio.core.chat import simple_roundtrip
from silencio.core.redact import enumerate_confidential_items
from silencio.settings import get_model_name

st.set_page_config(page_title="silencio — redactor", layout="wide")
st.title("silencio")

mode = st.radio("Mode", ["Chat", "Enumerate"], horizontal=True)

user_input = st.text_area(
    "Input text",
    height=300,
    placeholder="Paste text or message...",
)

if st.button("Run", type="primary"):
    if not user_input.strip():
        st.warning("Type or paste something first.")
        st.stop()

    with st.spinner(f"Running {mode.lower()} mode on {get_model_name()}…"):
        try:
            if mode == "Chat":
                output = simple_roundtrip(user_input)
                st.subheader("Output")
                st.text_area("Result", output, height=400)

            if mode == "Enumerate":
                inventory = enumerate_confidential_items(user_input)
                st.subheader("Inventory")
                rows = [
                    {
                        "#": i + 1,
                        "item": it.item,
                        "code": it.code,
                        "desc": it.desc,
                        "aliases": ", ".join(it.aliases) if it.aliases else "",
                        "notes": it.notes,
                    }
                    for i, it in enumerate(inventory.items)
                ]
                st.dataframe(rows, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
