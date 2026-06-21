import streamlit as st
import requests

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
st.caption("Simple Input, Fantastic Output + Gambar")

app_mode = st.radio("**Pilih Mode:**", ["💬 Chat", "🎨 Bikin Gambar"], horizontal=True)

# INISIALISASI CHAT + CEK APAKAH USER BARU
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.first_load = True # TANDA USER BARU BUKA
else:
    st.session_state.first_load = False

# KALO USER BARU, KASIH SAMBUTAN DULU
if st.session_state.first_load and len(st.session_state.messages) == 0:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("**Selamat datang, Anda bebas melakukan apapun di sini**")
        st.markdown("**Note: mohon maaf bila gambar yang Fanilla buat kurang memuaskan** 🙏")

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["type"] == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

def get_text_response(prompt):
    headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}
    data = {
        "model": "google/gemma-4-31b-it:free",
        "messages": [{"role": "system", "content": "Kamu Fanilla AI. Jawab singkat & santai."}, {"role": "user", "content": prompt}]
    }
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
    return r.json()['choices'][0]['message']['content']

def get_image_response(prompt):
    headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}
    data = {
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "prompt": prompt,
    }
    r = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=data, timeout=60)
    if r.status_code!= 200: return None, f"Eror Gambar: {r.text}. Coba lagi 1 menit ya R."
    image_url = r.json()['data'][0]['url']
    return image_url, None

if prompt := st.chat_input("Ketik pesan atau deskripsi gambar..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla lagi proses..."):
            if app_mode == "🎨 Bikin Gambar":
                image_url, error = get_image_response(prompt)
                if error:
                    st.error(error)
                    st.session_state.messages.append({"role": "assistant", "content": error, "type": "text"})
                else:
                    st.image(image_url)
                    st.session_state.messages.append({"role": "assistant", "content": image_url, "type": "image"})
            else:
                reply = get_text_response(prompt)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
