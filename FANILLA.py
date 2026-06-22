import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Fanilla AI", page_icon="⚡")
st.title("⚡ Fanilla AI")
st.caption("Chat & Generate Gambar Gratis")

# INISIALISASI
if "messages" not in st.session_state:
    st.session_state.messages = []

app_mode = st.radio("Pilih Mode:", ("💬 Ngobrol", "🎨 Bikin Gambar"), horizontal=True)

# TAMPILIN HISTORY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        if msg["type"] == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# INPUT USER
if prompt := st.chat_input("Ketik pesan atau deskripsi gambar..."):
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
                    data = {
                        "model": "google/gemma-4-31b-it:free",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                    r.raise_for_status()
                    reply = r.json()['choices'][0]['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
                except Exception as e:
                    eror = f"Fanilla eror: {str(e)}"
                    st.error(eror)
                    st.session_state.messages.append({"role": "assistant", "content": eror, "type": "text"})
