import streamlit as st
import requests
import random
import time
import base64

st.set_page_config(page_title="Fanilla AI", page_icon="⚡", layout="wide")

# --- CONFIG ---
MODEL_LIST = [
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-flash-1.5-8b:free"
]
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"
IMAGE_MODEL = "stabilityai/sdxl:free" # Model gratis buat gambar
TTS_MODEL = "microsoft/speecht5_tts" # Model gratis TTS

# --- CSS BIAR CAKEP ---
st.markdown("""
<style>
.stChatMessage {background-color: #1E1E1E; border-radius: 10px;}
[data-testid="stChatInput"] {border: 2px solid #FF4B4B;}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Fanilla AI V5")
st.caption("Full Features: Chat, Vision, Image Gen, TTS")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR FITUR ---
with st.sidebar:
    st.header("Mode Fanilla")
    mode = st.radio("Pilih fitur:", ["💬 Ngobrol", "🎨 Bikin Gambar", "🔊 Text to Speech"])
    st.divider()
    st.header("Upload Gambar")
    uploaded_file = st.file_uploader("Buat Vision AI", type=["png", "jpg", "jpeg"])
    st.caption("200MB per file • PNG, JPG")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- TAMPILIN HISTORY CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.markdown(msg["content"])
        elif msg["type"] == "image":
            st.image(msg["content"])
        elif msg["type"] == "audio":
            st.audio(msg["content"])

# --- FUNGSI API ---
def call_openrouter(payload):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 429:
            return "LIMIT", "Fanilla lagi istirahat R 😴 Limit API abis. Tunggu 1 menit ya."
        r.raise_for_status()
        return "OK", r.json()
    except Exception as e:
        return "ERROR", f"Fanilla eror: {e}"

# --- MODE 1: NGOBROL + VISION ---
if mode == "💬 Ngobrol":
    if prompt := st.chat_input("Ketik pesan untuk Fanilla AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Fanilla lagi mikir..."):
                # Pake vision kalo ada gambar
                if uploaded_file:
                    img_bytes = uploaded_file.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    model_pake = VISION_MODEL
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ]
                else:
                    model_pake = random.choice(MODEL_LIST)
                    content = prompt

                payload = {"model": model_pake, "messages": [{"role": "user", "content": content}]}
                status, hasil = call_openrouter(payload)

                if status == "OK":
                    reply = hasil['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
                else:
                    st.error(hasil)
                    st.session_state.messages.append({"role": "assistant", "content": hasil, "type": "text"})

# --- MODE 2: BIKIN GAMBAR ---
elif mode == "🎨 Bikin Gambar":
    if prompt := st.chat_input("Jelasin gambar yang mau dibikin..."):
        st.session_state.messages.append({"role": "user", "content": f"Gambar: {prompt}", "type": "text"})
        with st.chat_message("user"):
            st.markdown(f"Gambar: {prompt}")

        with st.chat_message("assistant"):
            with st.spinner("Fanilla lagi nggambar... 20-40 detik R"):
                payload = {
                    "model": IMAGE_MODEL,
                    "prompt": prompt,
                }
                headers = {
                    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                    "Content-Type": "application/json"
                }
                try:
                    r = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=payload, timeout=120)
                    if r.status_code == 429:
                        st.error("Limit gambar abis R 😴 Tunggu 1 menit")
                        st.stop()
                    r.raise_for_status()
                    img_url = r.json()['data'][0]['url']
                    st.image(img_url, caption=prompt)
                    st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                except Exception as e:
                    st.error(f"Gagal bikin gambar R: {e}")

# --- MODE 3: TEXT TO SPEECH ---
elif mode == "🔊 Text to Speech":
    if prompt := st.chat_input("Ketik teks yang mau diucapin Fanilla..."):
        st.session_state.messages.append({"role": "user", "content": f"TTS: {prompt}", "type": "text"})
        with st.chat_message("user"):
            st.markdown(f"TTS: {prompt}")

        with st.chat_message("assistant"):
            with st.spinner("Fanilla lagi rekaman..."):
                payload = {
                    "model": TTS_MODEL,
                    "input": prompt
                }
                headers = {
                    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                    "Content-Type": "application/json"
                }
                try:
                    r = requests.post("https://openrouter.ai/api/v1/audio/speech", headers=headers, json=payload, timeout=60)
                    if r.status_code == 429:
                        st.error("Limit TTS abis R 😴 Tunggu 1 menit")
                        st.stop()
                    r.raise_for_status()
                    audio_bytes = r.content
                    st.audio(audio_bytes, format="audio/mp3")
                    st.session_state.messages.append({"role": "assistant", "content": audio_bytes, "type": "audio"})
                except Exception as e:
                    st.error(f"Gagal bikin suara R: {e}")
