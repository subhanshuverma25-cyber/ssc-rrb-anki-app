import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from datetime import datetime, timedelta

st.set_page_config(page_title="SSC/RRB JE Anki AI", layout="centered")

# --- SESSION STATE INITIALIZATION (Memory setup) ---
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.title("🏗️ SSC/RRB JE Anki AI Flashcards")

# Sidebar: API Key
with st.sidebar:
    st.header("Settings")
    user_key = st.text_input("Gemini API Key dalein", value=st.session_state.api_key, type="password")
    if user_key:
        st.session_state.api_key = user_key
        genai.configure(api_key=user_key)
    st.info("Data memory mein save hoga (Jab tak tab open hai).")

tab1, tab2 = st.tabs(["📤 Upload PDF", "📖 Revision Mode"])

with tab1:
    uploaded_file = st.file_uploader("Study PDF upload karein", type="pdf")
    if uploaded_file and st.session_state.api_key:
        if st.button("AI Flashcards Banayein"):
            with st.spinner("AI cards bana raha hai..."):
                reader = PdfReader(uploaded_file)
                text = "".join([page.extract_text() for page in reader.pages[:3]])
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                # Prompt ko strict banaya hai taaki data parse ho sake
                prompt = f"Create 5 SSC JE level flashcards. Format: 'Q: [Question] | A: [Answer]'. Separate cards with '---'. Text: {text[:2000]}"
                response = model.generate_content(prompt)
                
                # Parsing Logic: Text se cards nikal kar list mein dalna
                new_cards_raw = response.text.split('---')
                for item in new_cards_raw:
                    if '|' in item:
                        parts = item.split('|')
                        q = parts[0].replace('Q:', '').strip()
                        a = parts[1].replace('A:', '').strip()
                        st.session_state.flashcards.append({"q": q, "a": a, "next": datetime.now().date()})
                
                st.success(f"Naye {len(new_cards_raw)} cards add ho gaye!")

with tab2:
    today = datetime.now().date()
    # Filter cards jinhe aaj padhna hai
    due_cards = [c for c in st.session_state.flashcards if c['next'] <= today]

    if due_cards:
        card = due_cards[0]
        st.subheader("Question:")
        st.info(card['q'])
        
        if st.button("Show Answer"):
            st.success(f"Answer: {card['a']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Hard (Kal dikhao)"):
                card['next'] = today + timedelta(days=1)
                st.rerun()
            if col2.button("Easy (4 Din baad)"):
                card['next'] = today + timedelta(days=4)
                st.rerun()
    else:
        st.write(f"🎉 Aaj ke liye saare cards khatam! (Total cards: {len(st.session_state.flashcards)})")

if st.button("Clear All Data"):
    st.session_state.flashcards = []
    st.rerun()
    
