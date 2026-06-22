import streamlit as st
import requests
import random
import base64
import time
from datetime import datetime

st.set_page_config(page_title="Fanilla AI", page_icon="💎")

# CUMA 2 MODEL GEMMA GRATIS YANG ADA DI OPENROUTER HARI INI
GEMMA_MODELS = [
    "google/gemma-4-26b-a4b-it:free", # Gemma 4 26B
    "google/gemma-4-31b-it:free" # Gemma 4 31B
]
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free" # Vision tetep Llama, Gemma ga ada vision gratis

st.title("💎 Fanilla AI V6 - Gemma Edition")
st.caption(f"100% Google Gemma | {datetime.now().strftime('%d %b %Y')}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.info("🔥 Pake Gemma 4 26B & 31B Only")
    st.warning("Limit Gemma 31B: ~10/menit\nLimit Gemma 26B: ~15/menit")
    uploaded_file = st.file_uploader("Upload Gambar", type=["png", "jpg", "jpeg"])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya ke Gemma..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gemma lagi mikir..."):
            time.sleep(2) # Cooldown 2 detik wajib, Gemma 31B limit ketat
            headers = {"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}"}

            if uploaded_file:
                img_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                model_pake = VISION_MODEL # Vision pake Llama, Gemma ga support
                content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}]
                st.caption("⚠️ Vision pake Llama 3.2 - Gemma belum ada vision gratis")
            else:
                model_pake = random.choice(GEMMA_MODELS)
                content = prompt
                st.caption(f"💎 {model_pake.split('/')[1].replace('-it:free','')}")

            data = {"model": model_pake, "messages": [{"role": "user", "content": content}]}

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                if r.status_code == 404:
                    st.error(f"Buset R, `{model_pake.split('/')[1]}` mokad juga 😭")
                    st.stop()
                if r.status_code == 429:
                    st.error("Limit Gemma R 😴 Model 26B/31B emang ketat. Tunggu 1 menit.")
                    st.stop()
                r.raise_for_status()
                reply = r.json()['choices'][0]['message']['content']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Gemma eror: {e}")
