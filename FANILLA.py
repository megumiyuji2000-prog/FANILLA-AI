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

# INISIALISASI + SAMBUTAN CUMA 1X
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("**Selamat datang, Anda bebas melakukan apapun di sini**")
        st.markdown("**Note: mohon maaf bila gambar yang Fanilla buat kurang memuaskan** 🙏")

# TAMPILIN CHAT LAMA
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# INPUT USER
if prompt := st.chat_input("Ketik pesan atau deskripsi gambar..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # PROSES JAWABAN FANILLA - SEMUA DISINI, GA PISAH2
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla lagi mikir..."):
            headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}

            # KALO MODE GAMBAR
            if app_mode == "🎨 Bikin Gambar":
                try:
                    data = {"model": "google/gemini-2.5-flash-image", "prompt": prompt}
                    r = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=data, timeout=60)
                    if r.status_code == 200:
                        image_url = r.json()['data'][0]['url']
                        st.image(image_url)
                        st.session_state.messages.append({"role": "assistant", "content": image_url, "type": "image"})
                    else:
                        eror_msg = f"Server gambar lagi eror {r.status_code}. Coba 1 menit lagi R."
                        st.error(eror_msg)
                        st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})
                except Exception as e:
                    eror_msg = f"Koneksi gagal: {str(e)}"
                    st.error(eror_msg)
                    st.session_state.messages.append({"role": "assistant", "content": eror_msg, "type": "text"})

            # KALO MODE CHAT
            else:
                try:
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
