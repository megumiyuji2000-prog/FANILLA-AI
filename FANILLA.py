import streamlit as st
import requests
import random
import time
import base64

st.set_page_config(page_title="Fanilla AI", page_icon="⚡")

# MODEL YANG MASIH IDUP DI OPENROUTER PER HARI INI R
MODEL_LIST = [
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "google/gemini-flash-1.5-8b:free",
    "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free"
]
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

st.title("⚡ Fanilla AI V5.1")
st.caption("Full Features: Chat & Vision Only - Anti 404")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Upload Gambar")
    uploaded_file = st.file_uploader("Buat Vision AI", type=["png", "jpg", "jpeg"])
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
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            else:
                model_pake = random.choice(MODEL_LIST)
                content = prompt

            data = {"model": model_pake, "messages": [{"role": "user", "content": content}]}

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                if r.status_code == 404:
                    st.error("Model ga ada R 😭 OpenRouter hapus modelnya. Coba lagi, nanti ganti model otomatis.")
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
