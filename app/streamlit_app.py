# app/streamlit_app.py
import streamlit as st
from silencio.core.chat import simple_roundtrip
from silencio.core.redact import redact_text
from silencio.settings import get_model_name

st.set_page_config(page_title="silencio — redactor", layout="wide")
st.title("silencio")

mode = st.radio("Mode", ["Chat", "Redact"], horizontal=True)

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
            else:
                output = redact_text(user_input)
            st.subheader("Output")
            st.text_area("Result", output, height=400)
        except Exception as e:
            st.error(f"Error: {e}")
