import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader
from PIL import Image
import io
from streamlit_mic_recorder import mic_recorder

# 1. Setup - Pulling from your Streamlit Secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interface Styling
st.set_page_config(page_title="Rob's AI Case Files", page_icon="⚖️", layout="wide")
st.title("⚖️ Rob's AI Case Files")
st.subheader("Personal AI Research & Strategic Legal Assistant")

# 3. Sidebar for Navigation
menu = ["Add New Note", "Search My Files", "Chat & Stress Test", "The Audit Lab"]
choice = st.sidebar.selectbox("Choose a Task", menu)

# --- TASK 1: ADD NEW NOTE (OCR & Voice Supported) ---
if choice == "Add New Note":
    st.write("### 📝 Add to the Brain")
    title = st.text_input("Document Title (e.g., 'Evidence Photo' or 'Case Summary')")
    content_type = st.radio("Input Type", ["Text", "Voice Memo", "Upload PDF/Word", "Upload Image (OCR)"])
    
    content = ""
    if content_type == "Text":
        content = st.text_area("Type your notes here...")
    
    elif content_type == "Voice Memo":
        st.write("Click to record your thoughts:")
        audio = mic_recorder(start_prompt="🎤 Start Recording", stop_prompt="🛑 Stop", key='recorder')
        if audio:
            with st.spinner("Transcribing your voice..."):
                audio_data = {'mime_type': 'audio/wav', 'data': audio['bytes']}
                res = model.generate_content(["Summarize and transcribe this voice note into clean text:", audio_data])
                content = res.text
                st.text_area("Transcribed Text", content, height=200)

    elif content_type == "Upload PDF/Word":
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            else:
                doc = Document(uploaded_file)
                content = "\n".join([para.text for para in doc.paragraphs])

    elif content_type == "Upload Image (OCR)":
        uploaded_img = st.file_uploader("Upload a photo of evidence/notes", type=["jpg", "jpeg", "png"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Uploaded Image", width=300)
            if st.button("Extract Text from Image"):
                with st.spinner("Reading photo..."):
                    res = model.generate_content(["Extract all text from this image as a clean document:", img])
                    content = res.text
                    st.text_area("Extracted Text", content, height=200)

    if st.button("Save to Cloud"):
        if title and content:
            supabase.table("documents").insert({"title": title, "content": content}).execute()
            st.success(f"Successfully saved: {title}")
        else:
            st.error("Missing title or content.")

# --- TASK 2: SEARCH FILES ---
elif choice == "Search My Files":
    st.write("### 📂 Search Your Brain")
    search_query = st.text_input("Search by title...")
    
    if search_query:
        docs = supabase.table("documents").select("*").ilike("title", f"%{search_query}%").execute()
    else:
        docs = supabase.table("documents").select("*").execute()
    
    for d in docs.data:
        with st.expander(d['title']):
            st.write(d['content'])
            if st.button(f"Delete {d['title']}", key=d['id']):
                supabase.table("documents").delete().eq("id", d['id']).execute()
                st.rerun()

# --- TASK 3: CHAT & STRESS TEST (Citations Enabled) ---
elif choice == "Chat & Stress Test":
    st.write("### 💬 Chat with Your Files")
    docs = supabase.table("documents").select("title, content").execute()
    
    all_text = ""
    for d in docs.data:
        all_text += f"\n\n--- DOCUMENT TITLE: {d['title']} ---\n{d['content']}"

    st.write("Ask a question by typing or using your voice:")
    v_audio = mic_recorder(start_prompt="🎙️ Ask by Voice", stop_prompt="🛑 Stop & Process", key='chat_recorder')
    user_question = st.text_input("Or type your question here...")

    if v_audio:
        with st.spinner("Processing voice..."):
            audio_data = {'mime_type': 'audio/wav', 'data': v_audio['bytes']}
            v_res = model.generate_content(["Transcribe this user question briefly:", audio_data])
            user_question = v_res.text
            st.info(f"Searching for: {user_question}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Search & Analyze") and user_question and all_text:
            with st.spinner("Searching the Brain..."):
                prompt = f"Use these files to answer the question. Cite which 'DOCUMENT TITLE' you found it in.\n\nFILES:\n{all_text}\n\nQUESTION: {user_question}"
                res = model.generate_content(prompt)
                st.write(res.text)
                st.download_button("Download Answer (.txt)", res.text, file_name="ai_answer.txt")
    
    with col2:
        if st.button("🔥 Run Opposing Counsel Test") and all_text:
            with st.spinner("Analyzing vulnerabilities..."):
                res = model.generate_content(f"Act as a hostile lawyer. Find all weaknesses or contradictions in these notes:\n\n{all_text}")
                st.write(res.text)
                st.download_button("Download Stress Test (.txt)", res.text, file_name="stress_test.txt")

# --- TASK 4: THE AUDIT LAB (Audit & Translate) ---
elif choice == "The Audit Lab":
    st.write("### 🔍 The Audit Lab")
    uploaded_audit = st.file_uploader("Upload file for Audit or Translation", type=["pdf", "docx"])
    
    if uploaded_audit:
        if uploaded_audit.type == "application/pdf":
            new_content = "\n".join([p.extract_text() for p in PdfReader(uploaded_audit).pages])
        else:
            new_content = "\n".join([p.text for p in Document(uploaded_audit).paragraphs])
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Run Difference Audit"):
                docs = supabase.table("documents").select("content").execute()
                brain_text = "\n".join([str(d['content']) for d in docs.data])
                res = model.generate_content(f"Extract ONLY new or conflicting info from NEW compared to BRAIN.\nNEW:\n{new_content}\nBRAIN:\n{brain_text}")
                st.write(res.text)
                st.download_button("Download Audit (.txt)", res.text, file_name="audit_report.txt")
        
        with col_b:
            if st.button("⚖️ Translate Legalese"):
                res = model.generate_content(f"Simplify this document into plain English for a non-lawyer:\n\n{new_content}")
                st.write(res.text)
                st.download_button("Download Translation (.txt)", res.text, file_name="translation.txt")
