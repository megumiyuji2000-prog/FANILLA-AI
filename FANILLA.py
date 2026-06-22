import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Fanilla AI", page_icon="⚡", layout="centered")

st.markdown("""
<style>
.stApp {background-color: #0A0A0A;}
h1, p,.stMarkdown {color: #FFFFFF!important;}
.stChatMessage {background-color: #000000!important; border: 1px solid #2DD4BF; border-radius: 18px;}
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("Fanilla AI")
st.caption("Simple Input, Fantastic Output + Gambar by Gemini 🍌")

app_mode = st.radio("**Pilih Mode:**", ["💬 Chat", "🎨 Bikin Gambar"], horizontal=True)

# SAMBUTAN 1X DOANG
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("**Selamat datang, Anda bebas melakukan apapun di sini**")
        st.markdown("**Note: mohon maaf bila gambar yang Fanilla buat kurang memuaskan** 🙏")

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ketik pesan atau deskripsi gambar..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla lagi proses..."):

                        # MODE GAMBAR PAKE IMAGEN 3 - YANG BENERAN STABIL
            if app_mode == "🎨 Bikin Gambar":
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={st.secrets['GEMINI_KEY']}"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "instances": [{"prompt": prompt}],
                        "parameters": {"sampleCount": 1}
                    }
                    r = requests.post(url, headers=headers, json=data, timeout=60)

                    if r.status_code == 200:
                        img_b64 = r.json()['predictions'][0]['bytesBase64Encoded']
                        image = Image.open(BytesIO(base64.b64decode(img_b64)))
                        st.image(image)
                        st.session_state.messages.append({"role": "assistant", "content": image, "type": "image"})
                    else:
                        eror_msg = f"Imagen eror {r.status_code}: {r.json().get('error', {}).get('message', 'Coba lagi R')}"
                        st.error(eror_msg)
                        st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})

                except Exception as e:
                    eror_msg = f"Gagal total R: {str(e)}"
                    st.error(eror_msg)
                    st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"}).messages.append({"role": "assistant", "content": eror_msg, "type": "text"})

            # MODE CHAT TETEP PAKE OPENROUTER
            else:
                try:
                    headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}
                    data = {
                        "model": "google/gemma-4-31b-it:free",
                        "messages": [{"role": "system", "content": "Kamu Fanilla AI. Jawab singkat & santai."}, {"role": "user", "content": prompt}]
                    }
                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
                    reply = r.json()['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
                except Exception as e:
                    eror_msg = f"Fanilla lagi eror: {str(e)}"
                    st.error(eror_msg)
                    st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})
