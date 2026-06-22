import streamlit as st
import requests
from io import BytesIO
import base64

# 1. PAGE CONFIG + CSS GEMINI STYLE
st.set_page_config(page_title="Fanilla AI", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    /* Hilangin branding Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background & Font */
  .stApp {
        background-color: #131314;
        font-family: 'Google Sans', sans-serif;
    }

    /* Judul Gradient Gemini */
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #8AB4F8, #C58AF9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 500;
        padding-top: 1.5rem;
        padding-bottom: 0rem;
    }

    /* Caption tengah */
    [data-testid="stCaptionContainer"] {
        text-align: center;
        color: #9AA0A6;
        margin-bottom: 1.5rem;
    }

    /* Radio jadi pills di tengah */
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

    /* Chat Bubble Style */
  .stChatMessage {
        background-color: #1E1F20;
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 1rem;
        border: none;
    }
    /* Bubble User beda warna */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #283142;
    }

    /* Input Chat + File Uploader */
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

   /* Tombol download */
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
st.caption("Ditenagai Gemma 4 31B via OpenRouter")

# 3. INISIALISASI
if "messages" not in st.session_state:
    st.session_state.messages = []

app_mode = st.radio("Pilih Mode:", ("💬 Ngobrol", "🎨 Bikin Gambar"), horizontal=True, label_visibility="collapsed")

# 4. TAMPILIN HISTORY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        if msg["type"] == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# 5. INPUT USER + UPLOAD GAMBAR KHUSUS MODE NGOBROL
uploaded_file = None
if app_mode == "💬 Ngobrol":
    uploaded_file = st.file_uploader(
        "Upload gambar buat ditanyain ke Fanilla",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

prompt = st.chat_input("Ketik pesan untuk Fanilla AI...")

if prompt or uploaded_file:
    # SIMPAN PESAN USER
    if uploaded_file is not None:
        st.session_state.messages.append({"role": "user", "content": uploaded_file, "type": "image_upload"})
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

                    # FITUR 3: DOWNLOAD GAMBAR R
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

                    # FITUR 5: VISION KALO ADA GAMBAR R
                    if uploaded_file is not None:
                        img_bytes = uploaded_file.getvalue()
                        img_base64 = base64.b64encode(img_bytes).decode()

                        messages_api = [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt if prompt else "Jelaskan gambar ini secara detail"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                            ]
                        }]
                    else:
                        messages_api = [{"role": "user", "content": prompt}]

                    data = {
                        "model": "google/gemma-4-31b-it:free", # WAJIB MODEL VISION
                        "messages": messages_api
                    }

                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=90)
                    r.raise_for_status()
                    reply = r.json()['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        eror = "Fanilla lagi istirahat dulu R 😴 Limit API abis. Coba lagi semenit ya"
                    else:
                        eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
                except Exception as e:
                    eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
