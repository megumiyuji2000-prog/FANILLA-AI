import streamlit as st
import requests
from io import BytesIO
import base64
import time
from PIL import Image

# 1. PAGE CONFIG + CSS GEMINI STYLE
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
        padding-top: 1.5rem;
        padding-bottom: 0rem;
    }
    [data-testid="stCaptionContainer"] {
        text-align: center;
        color: #9AA0A6;
        margin-bottom: 1.5rem;
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
.stDownloadButton > button {
        background-color: #283142;
        color: #8AB4F8;
        border: 1px solid #8AB4F8;
        border-radius: 12px;
        width: 100%;
   }
.stDownloadButton > button:hover {
        background-color: #8AB4F8;
        color: #131314;
   }
</style>
""", unsafe_allow_html=True)

# 2. HEADER
st.title("⚡ Fanilla AI")
st.caption("Ditenagai Gemma 4 via OpenRouter")

# 3. INISIALISASI
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = 0

app_mode = st.radio("Pilih Mode:", ("💬 Ngobrol", "🎨 Bikin Gambar"), horizontal=True, label_visibility="collapsed")

# 4. TAMPILIN HISTORY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        if msg["type"] == "image":
            st.image(msg["content"])
        elif msg["type"] == "image_upload":
            st.image(msg["content"], width=200)
            if msg.get("caption"):
                st.markdown(msg["caption"])
        else:
            st.markdown(msg["content"])

# 5. INPUT USER + UPLOAD GAMBAR
uploaded_file = None
if app_mode == "💬 Ngobrol":
    uploaded_file = st.file_uploader(
        "Upload gambar max 5MB",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

prompt = st.chat_input("Ketik pesan untuk Fanilla AI...")

if prompt or uploaded_file:
    # CEK COOLDOWN KALO UPLOAD GAMBAR R
    if uploaded_file:
        waktu_sekarang = time.time()
        sisa_cooldown = 15 - (waktu_sekarang - st.session_state.last_upload_time)
        if sisa_cooldown > 0:
            st.warning(f"Sabar R, kasih napas Fanilla {int(sisa_cooldown)} detik lagi kalo upload gambar 😅")
            st.stop()
        st.session_state.last_upload_time = waktu_sekarang

    # SIMPAN PESAN USER
    if uploaded_file is not None:
        st.session_state.messages.append({"role": "user", "content": uploaded_file, "type": "image_upload", "caption": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.image(uploaded_file, width=200)
            if prompt:
                st.markdown(prompt)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

    # PROSES JAWABAN FANILLA
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

                    # PILIH MODEL OTOMATIS - NAMA UDAH BENER R
                    if uploaded_file is not None:
                        # Kompres gambar biar ga kena limit
                        img = Image.open(uploaded_file)
                        img.thumbnail((768, 768))
                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=75)
                        img_bytes = buffer.getvalue()
                        img_base64 = base64.b64encode(img_bytes).decode()

                        messages_api = [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt if prompt else "Jelaskan gambar ini secara detail"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                            ]
                        }]
                        model_pake = "google/gemma-4-31b-it:free" # VISION PAKE 31B
                    else:
                        messages_api = [{"role": "user", "content": prompt}]
                        model_pake = "google/gemma-4-26b-a4b-it:free" # CHAT PAKE 26B A4B

                    data = {
                        "model": model_pake,
                        "messages": messages_api
                    }

                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=90)
                    r.raise_for_status()
                    reply = r.json()['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        eror = "Fanilla lagi istirahat dulu R 😴 Limit API abis. Tunggu 1-2 menit ya."
                    elif e.response.status_code == 404:
                        eror = "Fanilla error 404 R. Modelnya ga ketemu. Cek lagi nama model di OpenRouter."
                    else:
                        eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
                except Exception as e:
                    eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
