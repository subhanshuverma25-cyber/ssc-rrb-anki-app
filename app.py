import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Refresh protection
if 'cards' not in st.session_state:
    st.session_state.cards = []

st.set_page_config(page_title="SSC/RRB JE AI", layout="centered")
st.title("🏗️ SSC/RRB JE Anki AI")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key dalein", type="password")
    if api_key:
        genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["📤 PDF Upload", "📖 Revision Mode"])

with tab1:
    f = st.file_uploader("Apna Study PDF dalein", type="pdf")
    if f and api_key:
        if st.button("AI Flashcards Banayein"):
            try:
                reader = PdfReader(f)
                text = "".join([p.extract_text() for p in reader.pages[:1]])
                
                # Sabse stable connection method
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                response = model.generate_content(f"Create 2 short Q&A cards from: {text[:800]}")
                
                st.session_state.cards.append(response.text)
                st.success("Success! 'Revision Mode' check karein.")
            except Exception as e:
                # Agar abhi bhi error aaye toh ye line batayegi kyun
                st.error(f"Technical Detail: {str(e)}")

with tab2:
    if st.session_state.cards:
        for card in st.session_state.cards:
            st.info(card)
    else:
        st.write("No cards yet.")
        
