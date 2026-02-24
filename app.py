import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from datetime import datetime, timedelta

# --- MEMORY SETUP (Taaki refresh par data na jaye) ---
if 'cards' not in st.session_state:
    st.session_state.cards = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.set_page_config(page_title="SSC/RRB JE Anki AI", layout="centered")
st.title("🏗️ SSC/RRB JE Anki AI Flashcards")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Settings")
    user_key = st.text_input("Gemini API Key dalein", value=st.session_state.api_key, type="password")
    if user_key:
        st.session_state.api_key = user_key
        genai.configure(api_key=user_key)
    st.info("Memory is active. Cards will stay until you close this tab.")

# --- MAIN TABS ---
tab1, tab2 = st.tabs(["📤 Upload PDF", "📖 Revision Mode"])

with tab1:
    uploaded_file = st.file_uploader("Study PDF upload karein", type="pdf")
    if uploaded_file and st.session_state.api_key:
        if st.button("AI Flashcards Banayein"):
            with st.spinner("AI is thinking..."):
                try:
                    # PDF Reading
                    reader = PdfReader(uploaded_file)
                    text = "".join([page.extract_text() for page in reader.pages[:2]])
                    
                    # Model Calling (Fixing the NotFound Error)
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    prompt = f"Create 3 flashcards from this text. Format each card exactly like this: 'Q: [Question] | A: [Answer]'. Separate cards with '---'. Text: {text[:1500]}"
                    response = model.generate_content(prompt)
                    
                    # Saving to Memory
                    raw_cards = response.text.split('---')
                    for item in raw_cards:
                        if '|' in item:
                            q_a = item.split('|')
                            st.session_state.cards.append({
                                "q": q_a[0].replace('Q:', '').strip(),
                                "a": q_a[1].replace('A:', '').strip(),
                                "next": datetime.now().date()
                            })
                    st.success(f"Successfully added {len(raw_cards)} cards!")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab2:
    today = datetime.now().date()
    due_cards = [c for c in st.session_state.cards if c['next'] <= today]

    if due_cards:
        card = due_cards[0]
        st.subheader("Question:")
        st.info(card['q'])
        
        if st.button("Show Answer"):
            st.success(f"Answer: {card['a']}")
            
            col1, col2 = st.columns(2)
            if col1.button("Hard (Review Tomorrow)"):
                card['next'] = today + timedelta(days=1)
                st.rerun()
            if col2.button("Easy (Review in 4 Days)"):
                card['next'] = today + timedelta(days=4)
                st.rerun()
    else:
        st.write(f"🎉 No cards due for today! Total cards in memory: {len(st.session_state.cards)}")

# Clear data button
if st.sidebar.button("Reset App Data"):
    st.session_state.cards = []
    st.rerun()
    
