import streamlit as st
import requests
from io import BytesIO
import base64
import time
from PIL import Image
# from gtts import gTTS # MATIIN DULU R
# import os

# 1. PAGE CONFIG + CSS GEMINI STYLE PRO MAX
st.set_page_config(page_title="Fanilla AI", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
 .stApp {
        background-color: #131314;
        font-family: 'Google Sans', sans-serif;
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #8AB4F8, #C58AF9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 500;
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    [data-testid="stCaptionContainer"] {
        text-align: center;
        color: #9AA0A6;
        margin-bottom: 1rem;
    }
 .stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 8px;
        margin-bottom: 1rem;
    }
 .stRadio > div > label {
        background-color: #1E1F20;
        padding: 8px 16px;
        border-radius: 8px;
        border: 1px solid #444746;
    }
 .stRadio > div > label:has(input:checked) {
        background-color: #283142;
        border: 1px solid #8AB4F8;
    }
 .stChatMessage {
        background-color: #1E1F20;
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 1rem;
        border: none;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #283142;
    }
 .stChatInputContainer {
        background-color: #1E1F20;
        border: 1px solid #444746;
        border-radius: 28px;
        padding: 6px 6px 6px 20px;
    }
 .stChatInputContainer:focus-within {
        border: 1px solid #8AB4F8;
    }
 .stFileUploader {
        padding-bottom: 10px;
    }
 .stFileUploader > div > button {
        background-color: #1E1F20;
        border: 1px solid #444746;
        color: #E3E3E3;
    }
 .stDownloadButton > button,.stButton > button {
        background-color: #283142;
        color: #8AB4F8;
        border: 1px solid #8AB4F8;
        border-radius: 12px;
        width: 100%;
    }
 .stDownloadButton > button:hover,.stButton > button:hover {
        background-color: #8AB4F8;
        color: #131314;
    }
  .small-btn button {
        padding: 2px 8px!important;
        font-size: 12px!important;
        width: auto!important;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 2. HEADER + SYSTEM PROMPT
st.title("⚡ Fanilla AI V3 Lite")
st.caption("Full Features: Chat, Vision, Image Gen, Memory")

SYSTEM_PROMPT = """Kamu adalah Fanilla AI, asisten AI buatan R.
Kepribadian: Asik, to the point, pake bahasa gaul indo, suka pake 'R' buat manggil user.
Aturan: Jawab singkat padat, pake tabel kalo diminta, jangan cringe, jangan sok bijak."""

# 3. INISIALISASI SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = 0

# 4. SIDEBAR: FITUR TAMBAHAN
with st.sidebar:
    st.markdown("### ⚙️ Kontrol Fanilla")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Info")
    st.caption("Model Chat: gemma-4-26b-a4b-it:free")
    st.caption("Model Vision: gemma-4-31b-it:free")

app_mode = st.radio("Pilih Mode:", ("💬 Ngobrol", "🎨 Bikin Gambar"), horizontal=True, label_visibility="collapsed")

# 5. TAMPILIN HISTORY CHAT
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "system": continue

    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        if msg["type"] == "image":
            st.image(msg["content"])
        elif msg["type"] == "image_upload":
            st.image(msg["content"], width=200)
            if msg.get("caption"):
                st.markdown(msg["caption"])
        else:
            st.markdown(msg["content"])

        # FITUR: TOMBOL COPY
        if msg["role"] == "assistant" and msg["type"] == "text":
            st.markdown(f'<div class="small-btn">', unsafe_allow_html=True)
            if st.button("📋 Copy", key=f"copy_{i}"):
                st.code(msg["content"], language=None)
            st.markdown('</div>', unsafe_allow_html=True)

# 6. INPUT USER + UPLOAD GAMBAR
uploaded_file = None
if app_mode == "💬 Ngobrol":
    uploaded_file = st.file_uploader(
        "Upload gambar max 5MB buat dianalisis",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

prompt = st.chat_input("Ketik pesan untuk Fanilla AI...")

if prompt or uploaded_file:
    if uploaded_file:
        waktu_sekarang = time.time()
        sisa_cooldown = 15 - (waktu_sekarang - st.session_state.last_upload_time)
        if sisa_cooldown > 0:
            st.warning(f"Sabar R, kasih napas Fanilla {int(sisa_cooldown)} detik lagi kalo upload gambar 😅")
            st.stop()
        st.session_state.last_upload_time = waktu_sekarang

    if uploaded_file is not None:
        st.session_state.messages.append({"role": "user", "content": uploaded_file, "type": "image_upload", "caption": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.image(uploaded_file, width=200)
            if prompt: st.markdown(prompt)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        if app_mode == "🎨 Bikin Gambar":
            with st.spinner("Fanilla lagi gambar..."):
                try:
                    prompt_bersih = requests.utils.quote(prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{prompt_bersih}?width=1024&height=1024&nologo=true"
                    st.image(image_url, caption=f"Fanilla AI: {prompt}")
                    img_response = requests.get(image_url)
                    img_bytes = BytesIO(img_response.content)
                    st.download_button(
                        label="⬇️ Download Gambar",
                        data=img_bytes,
                        file_name=f"fanilla_{prompt[:30]}.png",
                        mime="image/png"
                    )
                    st.session_state.messages.append({"role": "assistant", "content": image_url, "type": "image"})
                except Exception as e:
                    eror = f"Gagal bikin gambar: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
        else:
            with st.spinner("Fanilla lagi mikir..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {st.secrets['API_KEY']}",
                        "Content-Type": "application/json"
                    }
                    messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                    for msg in st.session_state.messages[-6:]:
                        if msg["role"] == "system": continue
                        if msg["type"] == "text":
                            messages_api.append({"role": msg["role"], "content": msg["content"]})
                        elif msg["type"] == "image_upload" and msg["role"] == "user":
                            img = Image.open(msg["content"])
                            img.thumbnail((768, 768))
                            buffer = BytesIO()
                            img.save(buffer, format="JPEG", quality=75)
                            img_bytes = buffer.getvalue()
                            img_base64 = base64.b64encode(img_bytes).decode()
                            content_list = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}]
                            if msg.get("caption"):
                                content_list.insert(0, {"type": "text", "text": msg["caption"]})
                            messages_api.append({"role": "user", "content": content_list})

                    model_pake = "google/gemma-4-31b-it:free" if uploaded_file else "google/gemma-4-26b-a4b-it:free"
                    data = {"model": model_pake, "messages": messages_api}
                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=90)
                    r.raise_for_status()
                    response_json = r.json()
                    if 'choices' not in response_json:
                        if 'error' in response_json:
                            eror = f"Fanilla eror: {response_json['error'].get('message', 'Unknown error')}"
                        else:
                            eror = f"Fanilla dapet response aneh: {response_json}"
                        st.error(eror)
                        st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
                        st.stop()
                    reply = response_json['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        eror = "Fanilla lagi istirahat dulu R 😴 Limit API abis. Tunggu 1-2 menit ya."
                    elif e.response.status_code == 404:
                        eror = "Model ga ketemu R. Cek nama model di OpenRouter."
                    elif e.response.status_code == 400:
                        eror = f"Request error R: {e.response.json().get('error', {}).get('message', e.response.text)}"
                    else:
                        eror = f"Fanilla eror HTTP: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
                except Exception as e:
                    eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
