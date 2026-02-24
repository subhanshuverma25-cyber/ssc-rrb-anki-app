import streamlit as st
import sqlite3
import google.generativeai as genai
from PyPDF2 import PdfReader
from datetime import datetime, timedelta

# Database setup - Data store karne ke liye
conn = sqlite3.connect('anki.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY, q TEXT, a TEXT, next DATE, interval INTEGER)')
conn.commit()

st.set_page_config(page_title="SSC/RRB JE AI Quiz", layout="centered")
st.title("🏗️ SSC/RRB JE Anki AI Flashcards")

# Sidebar: API Key Configuration
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key dalein", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    st.info("Tip: Get Key from Google AI Studio (Free)")

tab1, tab2 = st.tabs(["📤 Upload PDF", "📖 Revision Mode"])

with tab1:
    uploaded_file = st.file_uploader("Study PDF upload karein", type="pdf")
    if uploaded_file and api_key:
        if st.button("AI Flashcards Banayein"):
            reader = PdfReader(uploaded_file)
            # Pehle 2 pages se text nikalna
            text = "".join([page.extract_text() for page in reader.pages[:2]])
            
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Create 3 flashcards from this SSC/RRB JE text. Format: Q: [Question] | A: [Answer]. Text: {text[:1500]}"
            response = model.generate_content(prompt)
            
            # Cards ko store karne ka logic
            raw_text = response.text
            st.success("AI ne cards generate kar diye!")
            st.write(raw_text)
            st.warning("Storage logic setup karne ke liye pehle app deploy karein.")

with tab2:
    today = datetime.now().date()
    c.execute("SELECT * FROM cards WHERE next <= ?", (today,))
    cards = c.fetchall()

    if cards:
        card = cards[0]
        st.subheader("Question:")
        st.info(card[1])
        
        if st.button("Show Answer"):
            st.success(f"Answer: {card[2]}")
            
            # Anki-style Intervals
            col1, col2 = st.columns(2)
            if col1.button("Hard (Next: Kal)"):
                new_date = today + timedelta(days=1)
                c.execute("UPDATE cards SET next=? WHERE id=?", (new_date, card[0]))
                conn.commit()
                st.rerun()
            if col2.button("Easy (Next: 4 Din)"):
                new_date = today + timedelta(days=4)
                c.execute("UPDATE cards SET next=? WHERE id=?", (new_date, card[0]))
                conn.commit()
                st.rerun()
    else:
        st.write("🎉 Aaj ke liye saare cards khatam!")
  
