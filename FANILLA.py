import streamlit as st
import requests
import base64
import time
import random
from datetime import datetime

st.set_page_config(page_title="Fanilla AI", page_icon="💎")

MODEL = "google/gemma-4-31b-it:free"
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

# MULTI API KEY BIAR GA LIMIT
API_KEYS = [
    st.secrets["OPENROUTER_API_KEY_1"],
    st.secrets["OPENROUTER_API_KEY_2"],
    st.secrets["OPENROUTER_API_KEY_3"]
]

st.title("💎 Fanilla AI V7.1 - Anti Limit")
st.caption("3 API Key Rotation | Gemma 4 31B")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.success("✅ 3 API Key Aktif = ~30 chat/menit")
    uploaded_file = st.file_uploader("Upload Gambar", type=["png", "jpg", "jpeg"])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya ke Gemma 31B..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gemma 31B lagi mikir..."):
            time.sleep(3) # Cooldown turun jadi 3 detik karena ada 3 key
            # PAKE API KEY RANDOM TIAP CHAT
            headers = {"Authorization": f"Bearer {random.choice(API_KEYS)}"}

            if uploaded_file:
                img_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                model_pake = VISION_MODEL
                content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}]
            else:
                model_pake = MODEL
                content = prompt

            data = {"model": model_pake, "messages": [{"role": "user", "content": content}]}

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                if r.status_code == 429:
                    st.error("3 API KEY LIMIT SEMUA R 😭 Tunggu 1 menit. Lu spam parah.")
                    st.stop()
                r.raise_for_status()
                reply = r.json()['choices'][0]['message']['content']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Gemma eror: {e}")
