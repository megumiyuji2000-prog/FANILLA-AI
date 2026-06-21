import streamlit as st
import requests
import time

st.set_page_config(page_title="Fanilla AI", page_icon="🎨", layout="centered")

# CSS DARK MODE + TOMBOL GAMBAR
st.markdown("""
<style>
 .stApp {background-color: #0A0A0A;}
  h1, p,.stMarkdown {color: #FFFFFF!important;}
 .stChatMessage {background-color: #000000!important; border: 1px solid #2DD4BF; border-radius: 18px;}
  #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("Fanilla AI")
st.caption("Simple Input, Fantastic Output + Gambar")

# MODE CHAT VS GAMBAR
app_mode = st.radio("**Pilih Mode:**", ["💬 Chat", "🎨 Bikin Gambar"], horizontal=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Halo R! Gue Fanilla. Mau ngobrol apa bikin gambar?"})

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["type"] == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# FUNGSI TEKS
def get_text_response(prompt, system_prompt):
    headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}
    data = {
        "model": "google/gemma-4-31b-it:free",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
    if response.status_code!= 200: return f"Eror: {response.text}"
    return response.json()['choices'][0]['message']['content']

# FUNGSI GAMBAR - PAKE HUGGINGFACE GRATIS
def get_image_response(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"} # TOKEN BARU
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code!= 200: return None, f"Eror Gambar: {response.text}"
    return response.content, None

# INPUT USER
if prompt := st.chat_input("Ketik pesan atau deskripsi gambar..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla lagi proses..."):
            if app_mode == "🎨 Bikin Gambar":
                image_bytes, error = get_image_response(prompt)
                if error:
                    st.error(error)
                    st.session_state.messages.append({"role": "assistant", "content": error, "type": "text"})
                else:
                    st.image(image_bytes)
                    st.session_state.messages.append({"role": "assistant", "content": image_bytes, "type": "image"})
            else:
                system_prompt = "Kamu Fanilla AI. Jawab singkat & santai."
                reply = get_text_response(prompt, system_prompt)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
