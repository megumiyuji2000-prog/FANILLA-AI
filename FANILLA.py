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

                                    # MODE GAMBAR PAKE HUGGINGFACE - 100% GRATIS & STABIL
            if app_mode == "🎨 Bikin Gambar":
                try:
                    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                        # MODE GAMBAR PAKE POLLINATIONS - GA PAKE TOKEN, LANGSUNG JADI
            if app_mode == "🎨 Bikin Gambar":
                try:
                    # Pollinations ga butuh API Key. Tinggal tembak URL
                    prompt_encoded = requests.utils.quote(prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}"
                    
                    # Tembak langsung, ambil gambarnya
                    r = requests.get(image_url, timeout=60)
                    
                    if r.status_code == 200:
                        image = Image.open(BytesIO(r.content))
                        st.image(image)
                        st.session_state.messages.append({"role": "assistant", "content": image, "type": "image"})
                    else:
                        eror_msg = f"Server gambar lagi penuh {r.status_code}. Coba 10 detik lagi R."
                        st.error(eror_msg)
                        st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})

                except Exception as e:
                    eror_msg = f"Internet lu/Fanilla lemot: {str(e)}"
                    st.error(eror_msg)
                    st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})
            
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
