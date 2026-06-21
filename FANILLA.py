
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
st.caption("Simple Input, Fantastic Output")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Halo R! Gue Fanilla. Udah fix nih, tanya apa aja."})

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

def get_ai_response(prompt, system_prompt):
    try:
        headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}", "Content-Type": "application/json"}
        data = {
            "model": "google/gemma-4-31b-it:free",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code!= 200: return f"Eror Kode {response.status_code}: {response.text}"
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Eror Total R: {str(e)}"

if prompt := st.chat_input("Ketik pesan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Fanilla mikir..."):
            system_prompt = "Kamu Fanilla AI. Jawab singkat & santai."
            reply = get_ai_response(prompt, system_prompt)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
