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

# 3. Sidebar for Navigation
menu = ["Add New Note / Mass Upload", "Search & Edit Files", "Chat & Stress Test", "The Audit Lab"]
choice = st.sidebar.selectbox("Choose a Task", menu)

# --- TASK 1: ADD NEW NOTE / MASS UPLOAD (With AI Auto-Naming) ---
if choice == "Add New Note / Mass Upload":
    st.write("### 📝 Smart Add to the Brain")
    st.info("AI will automatically scan and name your documents based on their content.")
    
    input_method = st.radio("Choose Method", ["Upload Multiple Files (PDF, Word, TXT)", "Voice Memo", "Manual Text Entry", "Upload Image (OCR)"])
    
    if input_method == "Upload Multiple Files (PDF, Word, TXT)":
        uploaded_files = st.file_uploader("Drag and drop files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        
        if uploaded_files:
            if st.button(f"AI Scan & Save {len(uploaded_files)} Files"):
                for uploaded_file in uploaded_files:
                    content = ""
                    if uploaded_file.type == "application/pdf":
                        pdf_reader = PdfReader(uploaded_file)
                        content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        doc = Document(uploaded_file)
                        content = "\n".join([para.text for para in doc.paragraphs])
                    elif uploaded_file.type == "text/plain":
                        content = uploaded_file.read().decode("utf-8")
                    
                    if content:
                        # --- AI AUTO-NAMING LOGIC ---
                        name_prompt = f"Scan this document and create a short, professional title (max 6 words). Categorize it logically (e.g. Legal, Tech, Personal, Admin). Text: {content[:1000]}"
                        ai_title = model.generate_content(name_prompt).text.strip().replace('"', '')
                        
                        supabase.table("documents").insert({"title": ai_title, "content": content}).execute()
                        st.write(f"✅ Auto-Named: **{ai_title}**")
                st.success("All files processed and saved!")

    elif input_method == "Manual Text Entry":
        content = st.text_area("Type your notes here...")
        if st.button("AI Auto-Name & Save"):
            if content:
                ai_title = model.generate_content(f"Create a short title for this note: {content[:500]}").text.strip().replace('"', '')
                supabase.table("documents").insert({"title": ai_title, "content": content}).execute()
                st.success(f"Saved as: {ai_title}")

    elif input_method == "Voice Memo":
        audio = mic_recorder(start_prompt="🎤 Start Recording", stop_prompt="🛑 Stop", key='recorder')
        if audio:
            with st.spinner("Transcribing..."):
                audio_data = {'mime_type': 'audio/wav', 'data': audio['bytes']}
                transcript = model.generate_content(["Transcribe and summarize this accurately:", audio_data]).text
                st.text_area("Transcribed Text", transcript, height=200)
                if st.button("Save Transcription"):
                    ai_title = model.generate_content(f"Short title for this voice note: {transcript[:500]}").text.strip().replace('"', '')
                    supabase.table("documents").insert({"title": ai_title, "content": transcript}).execute()
                    st.success(f"Saved as: {ai_title}")

    elif input_method == "Upload Image (OCR)":
        uploaded_img = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            if st.button("Extract & Auto-Name"):
                text_content = model.generate_content(["Extract all text from this image:", img]).text
                ai_title = model.generate_content(f"Short title for this image text: {text_content[:500]}").text.strip().replace('"', '')
                supabase.table("documents").insert({"title": ai_title, "content": text_content}).execute()
                st.success(f"Saved as: {ai_title}")

# --- TASK 2: SEARCH & EDIT FILES ---
elif choice == "Search & Edit Files":
    st.write("### 📂 Your Brain Database")
    if st.button("🔄 Sync & Refresh Database"):
        st.cache_data.clear()
        st.rerun()

    search_query = st.text_input("Search files...")
    docs = supabase.table("documents").select("*").ilike("title", f"%{search_query}%").execute() if search_query else supabase.table("documents").select("*").execute()
    
    for d in docs.data:
        with st.expander(f"📄 {d['title']}"):
            new_title = st.text_input("Edit Title:", d['title'], key=f"title_{d['id']}")
            new_edit = st.text_area("Edit Content:", d['content'], key=f"edit_{d['id']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", key=f"save_{d['id']}"):
                    supabase.table("documents").update({"title": new_title, "content": new_edit}).eq("id", d['id']).execute()
                    st.success("Updated!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete File", key=f"del_{d['id']}"):
                    supabase.table("documents").delete().eq("id", d['id']).execute()
                    st.rerun()

# --- TASK 3: CHAT & STRESS TEST ---
elif choice == "Chat & Stress Test":
    st.write("### 💬 Smart Search & Analysis")
    docs = supabase.table("documents").select("title, content").execute()
    all_text = "\n".join([f"[{d['title']}]: {d['content']}" for d in docs.data]) if docs.data else ""

    v_audio = mic_recorder(start_prompt="🎙️ Ask by Voice", stop_prompt="🛑 Stop", key='chat_recorder')
    user_question = st.text_input("Search the brain...")

    if v_audio:
        with st.spinner("Processing voice..."):
            audio_data = {'mime_type': 'audio/wav', 'data': v_audio['bytes']}
            user_question = model.generate_content(["Transcribe question:", audio_data]).text
            st.info(f"Question: {user_question}")

    if user_question and all_text:
        if st.button("Run Smart Analysis"):
            with st.spinner("Deep searching files..."):
                prompt = f"Answer question based on these files. Cite [Title] in your response.\nDATA:\n{all_text}\nQUESTION:\n{user_question}"
                res = model.generate_content(prompt)
                st.markdown("### 🔍 AI Findings:")
                st.write(res.text)

# --- TASK 4: THE AUDIT LAB ---
elif choice == "The Audit Lab":
    st.write("### 🔍 The Audit Lab")
    uploaded_audit = st.file_uploader("Upload file to Compare or Translate", type=["pdf", "docx", "txt"])
    if uploaded_audit:
        if uploaded_audit.type == "application/pdf":
            new_content = "\n".join([p.extract_text() for p in PdfReader(uploaded_audit).pages if p.extract_text()])
        elif uploaded_audit.type == "text/plain":
            new_content = uploaded_audit.read().decode("utf-8")
        else:
            new_content = "\n".join([p.text for p in Document(uploaded_audit).paragraphs])
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Run Difference Audit"):
                docs = supabase.table("documents").select("content").execute()
                brain_text = "\n".join([str(d['content']) for d in docs.data])
                res = model.generate_content(f"Compare NEW to BRAIN. Extract UNIQUE info:\nNEW:\n{new_content}\nBRAIN:\n{brain_text}")
                st.write(res.text)
        with col_b:
            if st.button("⚖️ Translate Legalese"):
                res = model.generate_content(f"Simplify this to plain English for a non-lawyer:\n\n{new_content}")
                st.write(res.text)
