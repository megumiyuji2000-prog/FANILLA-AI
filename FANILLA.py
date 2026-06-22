import streamlit as st
import requests
import base64
import time
from datetime import datetime

st.set_page_config(page_title="Fanilla AI", page_icon="💎")

# CUMA 1 MODEL: GEMMA 4 31B R
MODEL = "google/gemma-4-31b-it:free"
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free" # Gemma ga ada vision gratis

st.title("💎 Fanilla AI V7")
st.caption(f"Single Model: Gemma 4 31B | {datetime.now().strftime('%d %b %Y')}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.info("🔥 Model: Gemma 4 31B Only")
    st.warning("⚠️ Limit: ~10 chat/menit\nJangan spam R, cooldown 6 detik")
    uploaded_file = st.file_uploader("Upload Gambar Buat Vision", type=["png", "jpg", "jpeg"])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.rerun()

# Counter biar tau udah chat berapa kali
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya ke Gemma 31B..."):
    st.session_state.chat_count += 1

    # Warning kalo udah kebanyakan chat
    if st.session_state.chat_count > 8:
        st.sidebar.error(f"⚠️ Udah {st.session_state.chat_count} chat R. Rawan limit!")

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gemma 31B lagi mikir..."):
            time.sleep(6) # COOLDOWN 6 DETIK WAJIB BUAT 31B R
            headers = {"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}"}

            # Kalo ada gambar = pake Vision Llama, kalo ga ada = Chat Gemma
            if uploaded_file:
                img_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                model_pake = VISION_MODEL
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
                st.caption("🖼️ Vision: Llama 3.2 11B - Gemma ga support gambar")
            else:
                model_pake = MODEL
                content = prompt
                st.caption("💎 Chat: Gemma 4 31B")

            data = {"model": model_pake, "messages": [{"role": "user", "content": content}]}

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)

                if r.status_code == 404:
                    st.error("Gemma 31B mokad R 😭 OpenRouter hapus lagi.")
                    st.stop()
                if r.status_code == 429:
                    st.error(f"LIMIT R 😴 Gemma 31B limit 10/menit. Udah {st.session_state.chat_count}x chat. Tunggu 1 menit.")
                    st.stop()

                r.raise_for_status()
                reply = r.json()['choices'][0]['message']['content']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"Gemma eror: {e}")
