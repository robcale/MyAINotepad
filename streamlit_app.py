import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import io

# 1. Setup
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interface Styling
st.set_page_config(page_title="Rob's AI Case Files", page_icon="⚖️", layout="wide")
st.title("⚖️ Rob's AI Case Files")
st.subheader("Your Personal AI Notepad & Strategic Legal Assistant")

# 3. Sidebar for Navigation
menu = ["Add New Note", "Search My Files", "Chat & Stress Test", "The Audit Lab"]
choice = st.sidebar.selectbox("Choose a Task", menu)

# --- TASK 1: ADD NEW NOTE (Now with OCR Vision) ---
if choice == "Add New Note":
    st.write("### 📝 Add to the Brain")
    title = st.text_input("Document Title (e.g., 'Evidence Photo' or 'Case Summary')")
    content_type = st.radio("Input Type", ["Text", "Upload PDF/Word", "Upload Image (OCR)"])
    
    content = ""
    if content_type == "Text":
        content = st.text_area("Type your notes here...")
    
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
        uploaded_img = st.file_uploader("Upload a photo of a document", type=["jpg", "jpeg", "png"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Uploaded Image", width=300)
            if st.button("Extract Text from Image"):
                with st.spinner("Gemini is reading the photo..."):
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
    docs = supabase.table("documents").select("*").ilike("title", f"%{search_query}%").execute() if search_query else supabase.table("documents").select("*").execute()
    
    for d in docs.data:
        with st.expander(d['title']):
            st.write(d['content'])
            if st.button(f"Delete {d['title']}", key=d['id']):
                supabase.table("documents").delete().eq("id", d['id']).execute()
                st.rerun()

# --- TASK 3: CHAT & STRESS TEST ---
elif choice == "Chat & Stress Test":
    st.write("### 💬 Chat with Your Files")
    docs = supabase.table("documents").select("content").execute()
    all_text = "\n".join([str(d['content']) for d in docs.data]) if docs.data else ""
    
    user_question = st.text_input("Ask a question or request a stress test...")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Ask Gemini") and user_question and all_text:
            res = model.generate_content(f"Context:\n{all_text}\n\nQuestion: {user_question}")
            st.write(res.text)
    
    with col2:
        if st.button("🔥 Run Opposing Counsel Test") and all_text:
            st.warning("Running Stress Test...")
            res = model.generate_content(f"Act as a hostile opposing counsel. Analyze these notes and find contradictions, weaknesses, or missing evidence that could hurt my case:\n\n{all_text}")
            st.write(res.text)

# --- TASK 4: THE AUDIT LAB (With Legalese Translator) ---
elif choice == "The Audit Lab":
    st.write("### 🔍 The Audit Lab")
    uploaded_audit = st.file_uploader("Upload a new file to Audit or Translate", type=["pdf", "docx"])
    
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
                res = model.generate_content(f"Compare NEW to BRAIN. Extract ONLY new info:\nNEW:\n{new_content}\nBRAIN:\n{brain_text}")
                st.write(res.text)
        
        with col_b:
            if st.button("⚖️ Translate Legalese to Plain English"):
                res = model.generate_content(f"Rewrite this complex document in simple, clear English that a high schooler could understand. Keep all the important facts:\n\n{new_content}")
                st.write(res.text)
