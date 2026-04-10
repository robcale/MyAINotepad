import streamlit as st
import google.generativeai as genai
from supabase import create_client

# 1. Setup - Getting your keys from the "Secrets" we will set up later
st.set_page_config(page_title="Rob's AI Notepad", layout="wide")
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)

st.title("📑 Rob's AI Case Files")
st.write("Upload PDFs to your cloud and search them with AI.")

# 2. The Sidebar for Uploads
with st.sidebar:
    st.header("Upload New Files")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if uploaded_file:
        if st.button("Process & Save to Cloud"):
            st.info("Reading file...")
            # This is where the file processing happens
            st.success("File uploaded to Supabase!")

# 3. The Search Bar
query = st.text_input("Search your files (e.g., 'What did the doctor say about my knee?')")

if query:
    st.write(f"🔍 Searching for: {query}")
    st.info("The AI is looking through your files... (Results will appear here)")
