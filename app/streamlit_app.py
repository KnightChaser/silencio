# app/streamlit_app.py
from __future__ import annotations
import streamlit as st

from silencio.core.chat import simple_roundtrip
from silencio.settings import get_model_name

st.set_page_config(page_title="silencio — basic chat", layout="centered")
st.title("silencio — Chat sanity check")

st.caption("Model and temperature are read from environment variables.")
st.code(
    "export OPENAI_API_KEY=sk-... ; export OPENAI_MODEL=gpt-5 ;",
    language="bash",
)

user_msg = st.text_area("Your message", height=200, placeholder="Say hello…")

col1, col2 = st.columns([1, 1])
with col1:
    send = st.button("Send", type="primary")
with col2:
    st.write(f"Model: `{get_model_name()}`")

if send:
    if not user_msg.strip():
        st.warning("Type something first.")
    else:
        with st.spinner("Talking to the model…"):
            try:
                reply = simple_roundtrip(user_msg)
                st.subheader("Reply")
                st.write(reply)
            except Exception as e:
                st.error(f"Error: {e}")
