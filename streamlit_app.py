import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader
from PIL import Image
from streamlit_mic_recorder import mic_recorder
import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", page_icon="⚖️", layout="wide")

# --- DATABASE & AI SETUP ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # The updated, high-speed engine
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError as e:
    st.error(f"🚨 Missing Secret/API Key: {e}. Please check your Streamlit Secrets.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚖️ The War Room")
menu = ["1. Mass Intake (Upload)", "2. The Processing Desk", "3. Search & Edit Files", "4. The Courtroom (Chat)"]
choice = st.sidebar.selectbox("Navigate", menu)

# --- TASK 1: MASS INTAKE (Sends to HOLD) ---
if choice == "1. Mass Intake (Upload)":
    st.write("### 📥 Intake & Mass Upload")
    st.info("All files uploaded here are sent to the 'Holding Tank' for review before entering the Brain.")
    
    uploaded_files = st.file_uploader("Drag and drop files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    if uploaded_files:
        if st.button(f"Scan & Send {len(uploaded_files)} Files to Hold"):
            with st.spinner("Processing intake..."):
                for uploaded_file in uploaded_files:
                    content = ""
                    if uploaded_file.type == "application/pdf":
                        pdf_reader = PdfReader(uploaded_file)
                        content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        doc = Document(uploaded_file)
                        content = "\n".join([para.text for para in doc.paragraphs])
                    elif uploaded_file.type == "text/plain":
                        content = uploaded_file.read().decode("utf-8", errors="ignore")
                    
                    if content:
                        try:
                            name_prompt = f"Create a short, professional title (max 6 words) for this document: {content[:1000]}"
                            ai_title = model.generate_content(name_prompt).text.strip().replace('"', '')
                            # Automatically tags it as HOLD
                            final_title = f"[HOLD] {ai_title}"
                            supabase.table("documents").insert({"title": final_title, "content": content}).execute()
                            st.write(f"✅ Sent to Hold: **{final_title}**")
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {e}")
                            
            st.success("Intake complete! Go to The Processing Desk to review.")

# --- TASK 2: THE PROCESSING DESK (Audit & Clean) ---
elif choice == "2. The Processing Desk":
    st.write("### ⏳ The Holding Tank & Processing Desk")
    
    # Fetch HOLD docs (FIXED: Added .select("*"))
    hold_docs = supabase.table("documents").select("*").ilike("title", "%[HOLD]%").execute()
    
    # Fetch MASTER STORY (FIXED: Added .select("*"))
    master_doc = supabase.table("documents").select("*").ilike("title", "%[MASTER STORY]%").execute()
    master_text = master_doc.data[0]['content'] if master_doc.data else "No Master Story found. Please upload a document titled '[MASTER STORY]'."
