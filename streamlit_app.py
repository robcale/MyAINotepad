import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from PyPDF2 import PdfReader
import io

# 1. Setup - Pulling from your Streamlit Secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interface Styling
st.set_page_config(page_title="Rob's AI Case Files", page_icon="⚖️")
st.title("⚖️ Rob's AI Case Files")
st.subheader("Your Personal AI Notepad & Legal Assistant")

# 3. Sidebar for Navigation
menu = ["Add New Note", "Search My Files", "Chat with My Brain", "The Audit Lab"]
choice = st.sidebar.selectbox("Choose a Task", menu)

# --- TASK 1: ADD NEW NOTE ---
if choice == "Add New Note":
    st.write("### Upload a Document or Type a Note")
    
    title = st.text_input("Document Title")
    content_type = st.radio("Input Type", ["Text", "Upload PDF", "Upload Word"])
    
    content = ""
    if content_type == "Text":
        content = st.text_area("Type your notes here...")
    
    elif content_type == "Upload PDF":
        uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
        if uploaded_file:
            pdf_reader = PdfReader(uploaded_file)
            content = "\n".join([page.extract_text() for page in pdf_reader.pages])

    elif content_type == "Upload Word":
        uploaded_file = st.file_uploader("Choose a Word Doc", type="docx")
        if uploaded_file:
            doc = Document(uploaded_file)
            content = "\n".join([para.text for para in doc.paragraphs])

    if st.button("Save to Cloud"):
        if title and content:
            data = {"title": title, "content": content}
            supabase.table("documents").insert(data).execute()
            st.success(f"Successfully saved: {title}")
        else:
            st.error("Please provide both a title and content.")

# --- TASK 2: SEARCH FILES ---
elif choice == "Search My Files":
    st.write("### Search Your Saved Notes")
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

# --- TASK 3: CHAT WITH MY BRAIN ---
elif choice == "Chat with My Brain":
    st.write("### Ask Questions About Your Saved Files")
    
    docs = supabase.table("documents").select("content").execute()
    
    if not docs.data:
        st.warning("No documents found in the cloud yet. Upload something first!")
        all_text = ""
    else:
        all_text = "\n".join([str(d['content']) for d in docs.data])
    
    user_question = st.text_input("What do you want to know?")
    
    if user_question and all_text:
        with st.spinner("Thinking..."):
            prompt = f"Using the following personal notes, answer the question: {user_question}\n\nNotes:\n{all_text}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            answer_text = response.text
            st.write(answer_text)
            
            st.download_button(
                label="Download Answer as .txt",
                data=answer_text,
                file_name="ai_answer.txt",
                mime="text/plain"
            )

# --- TASK 4: THE AUDIT LAB ---
elif choice == "The Audit Lab":
    st.write("### 🔍 The Audit Lab: New File vs. The Brain")
    st.info("Upload a file to see what's new compared to your existing notes.")

    uploaded_audit = st.file_uploader("Upload file for auditing", type=["pdf", "docx"])
    
    if uploaded_audit:
        new_content = ""
        if uploaded_audit.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_audit)
            new_content = "\n".join([p.extract_text() for p in pdf_reader.pages])
        else:
            doc = Document(uploaded_audit)
            new_content = "\n".join([p.text for p in doc.paragraphs])
        
        if new_content:
            st.success("New file loaded! Ready to audit.")
            
            if st.button("Run Audit"):
                with st.spinner("Comparing against the Brain..."):
                    # Pull existing brain data
                    docs = supabase.table("documents").select("content").execute()
                    brain_text = "\n".join([str(d['content']) for d in docs.data])
                    
                    audit_prompt = f"Compare the following NEW DOCUMENT to my EXISTING BRAIN. Extract only the NEW information, changes, or updates. Ignore everything already in the Brain. Format as a clean list.\n\nNEW DOCUMENT:\n{new_content}\n\nEXISTING BRAIN:\n{brain_text}"
                    
                    response = model.generate_content(audit_prompt)
                    st.markdown("### 📋 Audit Report (Unique Info):")
                    report_text = response.text
                    st.write(report_text)
                    
                    st.download_button(
                        label="Download Audit Report (.txt)",
                        data=report_text,
                        file_name="audit_report.txt",
                        mime="text/plain"
                    )
