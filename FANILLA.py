import streamlit as st
import requests
import random
import base64
from datetime import datetime

st.set_page_config(page_title="Fanilla AI", page_icon="⚡")

# UPDATE 22 JUNI 2026 - 3 MODEL GRATIS YANG MASIH IDUP R
MODEL_LIST = [
    "google/gemma-4-31b-it:free", # Gemma 2 masih aman
    "meta-llama/llama-3.3-70b-instruct:free", # Llama 3 biasa masih ada
    "google/gemma-4-31b-it:free" # Phi 3 Microsoft
]
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

st.title("⚡ Fanilla AI V5.3")
st.caption(f"Model Update: {datetime.now().strftime('%d %b %Y')}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Debug Info")
    st.write("Model Aktif:")
    for m in MODEL_LIST:
        st.code(m.split('/')[1])
    st.divider()
    uploaded_file = st.file_uploader("Upload Gambar", type=["png", "jpg", "jpeg"])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ketik pesan untuk Fanilla AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Fanilla lagi mikir..."):
            headers = {"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}"}

            if uploaded_file:
                img_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                model_pake = VISION_MODEL
                content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}]
            else:
                model_pake = random.choice(MODEL_LIST)
                content = prompt

            st.caption(f"🔧 Pake model: `{model_pake}`") # BIAR KETAUAN PAKE APA

            data = {"model": model_pake, "messages": [{"role": "user", "content": content}]}

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                if r.status_code == 404:
                    st.error(f"Buset R, `{model_pake}` baru aja mokad 😭 Chat lagi biar ganti model.")
                    st.stop()
                if r.status_code == 429:
                    st.error("Limit R 😴 Tunggu 1 menit.")
                    st.stop()
                r.raise_for_status()
                reply = r.json()['choices'][0]['message']['content']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Fanilla eror: {e}")
