import streamlit as st
import requests
import os

# CONFIG FANILLA AI
st.set_page_config(
    page_title="Fanilla AI",
    page_icon="⚡",
    layout="centered"
)

# CSS CUSTOM WARNA FANILLA
st.markdown("""
<style>
   .stApp { background-color: #FFF8E7; }
    h1 { color: #1F2937; text-align: center; }
   .stChatMessage { background-color: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# HEADER + LOGO
st.title("Fanilla AI")
st.caption("Simple Input, Fantastic Output")

# MODE VANILLA VS FANTASTIC
mode = st.radio("Pilih Mode:", ["Vanilla", "Fantastic"], horizontal=True)

# CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT USER
if prompt := st.chat_input("Tanya apa aja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # PANGGIL API AI
    with st.chat_message("assistant"):
        with st.spinner("Fanilla mikir..."):
            system_prompt = "Jawab singkat & to-the-point" if mode == "Vanilla" else "Jawab detail pake contoh & langkah konkret"

            headers = {
                "Authorization": f"Bearer {st.secrets['API_KEY']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            reply = response.json()['choices'][0]['message']['content']
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
