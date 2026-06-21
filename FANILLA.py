import streamlit as st
import requests
import time

# 1. CONFIG DASAR + TEMA FANILLA
st.set_page_config(
    page_title="Fanilla AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS CUSTOM BIAR NYAMAN + CAKEP
st.markdown("""
<style>
    /* Background Vanilla Cream */
   .stApp {
        background-color: #FFF8E7;
        font-family: 'Inter', sans-serif;
    }

    /* Judul */
    h1 {
        color: #1F2937;
        text-align: center;
        font-weight: 800;
        padding-top: 1rem;
    }

    /* Bubble Chat */
   .stChatMessage {
        background-color: white;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #F3F4F6;
    }

    /* Input Box */
   .stChatInput {
        background-color: white;
        border-radius: 12px;
    }

    /* Tombol Mode */
   .stRadio > div {
        justify-content: center;
        gap: 1rem;
    }

    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. HEADER
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("Fanilla AI")
    st.caption("Simple Input, Fantastic Output")

# 4. MODE VANILLA VS FANTASTIC
mode = st.radio(
    "**Pilih gaya jawab:**",
    ["**Vanilla** - Singkat & to-the-point", "**Fantastic** - Detail + contoh"],
    horizontal=True,
    label_visibility="collapsed"
)

# 5. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []
    # SAPAAN PERTAMA BIAR GA KOSONG
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Halo R! Gue Fanilla AI. Tanya apa aja, pilih mode Vanilla buat jawaban cepet atau Fantastic buat detail."
    })

for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 6. FUNGSI PANGGIL API ANTI EROR
def get_ai_response(prompt, system_prompt):
    try:
        headers = {
            "Authorization": f"Bearer {st.secrets['API_KEY']}",
            "HTTP-Referer": "https://fanilla-ai.streamlit.app",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7 if "Fantastic" in mode else 0.3
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30 # TIMEOUT 30 DETIK BIAR GA NGGANTUNG
        )

        # CEK KALO EROR DARI API
        if response.status_code!= 200:
            return f"Waduh R, server lagi batuk. Kode eror: {response.status_code}. Coba lagi 10 detik ya."

        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return "Sori R, Fanilla lagi mikir kelamaan. Coba pertanyaannya dipersingkat ya."
    except requests.exceptions.RequestException:
        return "Koneksi ke otak Fanilla putus R. Cek internet lu atau coba lagi."
    except Exception as e:
        return f"Ada eror tak terduga R: {str(e)}. Screenshot ini kirim ke developer."

# 7. INPUT USER + PROSES
if prompt := st.chat_input("Ketik pertanyaan lu disini..."):
    # TAMPILIN PESAN USER
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # PROSES & TAMPILIN JAWABAN AI
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Fanilla lagi mikir..."):
            if "Vanilla" in mode:
                system_prompt = "Kamu adalah Fanilla AI. Jawab super singkat, padat, to-the-point. Maksimal 3 kalimat. Gaya bahasa santai kayak temen."
            else:
                system_prompt = "Kamu adalah Fanilla AI. Jawab detail, kasih langkah-langkah konkret, dan contoh nyata. Gaya bahasa santai, bantuin, dan pake format poin biar gampang dibaca."

            reply = get_ai_response(prompt, system_prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
