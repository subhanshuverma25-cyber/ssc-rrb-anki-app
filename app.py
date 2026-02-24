import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Memory Setup (Refresh hone par data bachane ke liye)
if 'cards' not in st.session_state:
    st.session_state.cards = []

st.set_page_config(page_title="SSC/RRB JE AI", layout="centered")
st.title("🏗️ SSC/RRB JE Anki AI")

# 2. Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key dalein", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    st.info("Note: Browser tab band karne par data clear ho jayega.")

tab1, tab2 = st.tabs(["📤 PDF Upload", "📖 Revision Mode"])

with tab1:
    f = st.file_uploader("Apna Study PDF dalein", type="pdf")
    if f and api_key:
        if st.button("AI Flashcards Banayein"):
            try:
                reader = PdfReader(f)
                text = "".join([p.extract_text() for p in reader.pages[:2]])
                
                # Model 'gemini-pro' sabse stable hai
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"Create 3 flashcards from this text. Format: Q: [Question] | A: [Answer]. Text: {text[:1000]}"
                response = model.generate_content(prompt)
                
                # Cards ko memory mein save karna
                st.session_state.cards.append(response.text)
                st.success("Cards ban gaye! 'Revision Mode' mein check karein.")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    if st.session_state.cards:
        for card in st.session_state.cards:
            st.markdown(f"### {card}")
            st.write("---")
    else:
        st.write("Abhi koi cards nahi hain. Pehle PDF upload karke generate karein.")
        
