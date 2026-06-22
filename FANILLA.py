import streamlit as st
import requests
import random
import time

st.set_page_config(page_title="Fanilla AI", page_icon="⚡")

# ROTASI 4 MODEL GRATIS R. LIMIT 1 PINDAH KE YANG LAIN
MODEL_LIST = [
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-flash-1.5-8b:free"
]
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

# KODE LU YANG LAIN TETEP SAMA...

# PAS MAU KIRIM CHAT, GANTI BAGIAN INI:
if prompt := st.chat_input("Ketik pesan untuk Fanilla AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Fanilla lagi mikir....."):
            headers = {
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            }

            # GACHA MODEL RANDOM R, BIAR GA LIMIT
            model_pake = VISION_MODEL if uploaded_file else random.choice(MODEL_LIST)

            data = {
                "model": model_pake,
                "messages": [{"role": "user", "content": prompt}]
                #...sisa payload lu...
            }

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
                if r.status_code == 429:
                    st.error("Buset R, 4 model limit semua 😭 Tunggu 1 menit atau bikin API key baru")
                    st.stop()
                r.raise_for_status()
                reply = r.json()['choices'][0]['message']['content']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply, "type": "text"})
            except Exception as e:
                st.error(f"Fanilla eror: {e}")
