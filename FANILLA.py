import streamlit as st
import requests
import time

# 1. CONFIG DARK MODE FANILLA
st.set_page_config(
    page_title="Fanilla AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS DARK MODE + BUBBLE HITAM
st.markdown("""
<style>
    /* Background Hitam Total */
  .stApp {
        background-color: #0A0A0A;
        font-family: 'Inter', sans-serif;
    }

    /* Semua Teks Jadi Putih */
    h1, h2, h3, p,.stMarkdown,.stRadio > label,.stCaption {
        color: #FFFFFF!important;
    }

    /* Judul */
    h1 {
        text-align: center;
        font-weight: 800;
        padding-top: 1rem;
        color: #FFFFFF!important;
    }

    /* Caption */
  .stCaption {
        text-align: center!important;
        color: #A3A3A3!important;
    }

    /* Bubble Chat User = Abu Gelap */
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"]:has(div[data-testid="stMarkdownContainer"] > p) {
        background-color: #262626;
        border-radius: 18px;
        padding: 1rem 1.2rem;
    }

    /* Bubble Chat AI = Hitam + Border Teal */
    [data-testid="stChatMessage"][data-testid="chat-message-assistant"] [data-testid="stChatMessageContent"] {
        background-color: #000000!important;
        border: 1px solid #2DD4BF;
        border-radius: 18px;
        padding: 1rem 1.2rem;
    }

    /* Teks di dalam bubble putih semua */
    [data-testid="stChatMessageContent"] p {
        color: #FFFFFF!important;
    }

    /* Input Box */
  .stChatInput > div {
        background-color: #1F1F1F;
        border: 1px solid #333333;
        border-radius: 12px;
    }
   .stChatInput input {
        color: #FFFFFF!important;
    }

    /* Tombol Mode */
  .stRadio > div {
        justify-content: center;
        gap: 1rem;
    }
   .stRadio label span {
        color: #FFFFFF!important;
    }

    /* Hide Menu Bawaan */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. HEADER
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
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Halo ! Gue Fanilla AI Dark Mode. Tanya apa aja, udah enak diliat kan?"
    })

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 6. FUNGSI API ANTI EROR
def get_ai_response(prompt, system_prompt):
    try:
        headers = {
            "Authorization": f"Bearer {st.secrets['API_KEY']}",
            "HTTP-Referer": "https://fanilla-ai.streamlit.app",
            "Content-Type": "application/json"
        }

        data = {
            ""model": "google/gemma-2-9b-it:free",
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
            timeout=30
        )

        if response.status_code!= 200:
            return f"Server lagi error R. Kode: {response.status_code}. Coba lagi bentar ya."

        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return "Sori , kelamaan mikir. Coba pertanyaan lebih pendek."
    except Exception as e:
        return f"Eror R: {str(e)}. Cek API Key di Secrets udah bener belum."

# 7. INPUT USER
if prompt := st.chat_input("Ketik pertanyaan lu disini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla lagi mikir..."):
            if "Vanilla" in mode:
                system_prompt = "Kamu Fanilla AI. Jawab super singkat, padat, to-the-point. Maksimal 3 kalimat. Gaya bahasa santai."
            else:
                system_prompt = "Kamu Fanilla AI. Jawab detail, pake langkah konkret + contoh. Gaya santai, pake format poin."

            reply = get_ai_response(prompt, system_prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
