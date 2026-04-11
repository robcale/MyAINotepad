import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader
from PIL import Image
from streamlit_mic_recorder import mic_recorder
import datetime

# 1. Setup
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Rob's AI Case Files", page_icon="⚖️", layout="wide")

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
                        content = uploaded_file.read().decode("utf-8")
                    
                    if content:
                        name_prompt = f"Create a short, professional title (max 6 words) for this document: {content[:1000]}"
                        ai_title = model.generate_content(name_prompt).text.strip().replace('"', '')
                        # Automatically tags it as HOLD
                        final_title = f"[HOLD] {ai_title}"
                        supabase.table("documents").insert({"title": final_title, "content": content}).execute()
                        st.write(f"✅ Sent to Hold: **{final_title}**")
            st.success("Intake complete! Go to The Processing Desk to review.")

# --- TASK 2: THE PROCESSING DESK (Audit & Clean) ---
elif choice == "2. The Processing Desk":
    st.write("### ⏳ The Holding Tank & Processing Desk")
    
    # Fetch HOLD docs
    hold_docs = supabase.table("documents").ilike("title", "%[HOLD]%").execute()
    
    # Fetch MASTER STORY
    master_doc = supabase.table("documents").ilike("title", "%[MASTER STORY]%").execute()
    master_text = master_doc.data[0]['content'] if master_doc.data else "No Master Story found. Please upload a document titled '[MASTER STORY]'."

    if not hold_docs.data:
        st.success("The Holding Tank is empty! All files are processed.")
    else:
        doc_titles = [d['title'] for d in hold_docs.data]
        selected_title = st.selectbox("Select a document to review:", doc_titles)
        selected_doc = next(d for d in hold_docs.data if d['title'] == selected_title)
        
        st.write("#### Document Content:")
        current_content = st.text_area("Edit Raw Text:", selected_doc['content'], height=250, key="raw_text")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🧹 Clean Rambling & Reformat"):
                with st.spinner("Cleaning document..."):
                    clean_prompt = f"Remove all off-topic rambling from this text. Keep only the hard facts, dates, and legal relevance. Format it cleanly with bullet points:\n\n{current_content}"
                    cleaned_text = model.generate_content(clean_prompt).text
                    supabase.table("documents").update({"content": cleaned_text}).eq("id", selected_doc['id']).execute()
                    st.success("Document cleaned! Click 'Sync & Refresh' to see changes.")
                    
        with col2:
            if st.button("⚖️ Audit against Master Story"):
                with st.spinner("Cross-referencing..."):
                    audit_prompt = f"""
                    Compare this HOLD DOCUMENT to the MASTER STORY. 
                    List ONLY the new facts found in the Hold Document that are missing from the Master Story. 
                    Suggest exactly where they should be added.
                    
                    MASTER STORY: {master_text}
                    HOLD DOCUMENT: {current_content}
                    """
                    audit_result = model.generate_content(audit_prompt).text
                    st.info(audit_result)
                    
        with col3:
            if st.button("✅ Approve to Brain"):
                clean_title = selected_doc['title'].replace("[HOLD] ", "")
                supabase.table("documents").update({"title": clean_title, "content": current_content}).eq("id", selected_doc['id']).execute()
                st.success(f"Approved! Moved to main Brain as: {clean_title}")
                st.rerun()

        st.divider()
        st.write("#### 💬 Chat with this specific document:")
        doc_question = st.text_input("Ask a question or give an instruction on how to reformat this...")
        if st.button("Ask AI about Document") and doc_question:
            res = model.generate_content(f"Use ONLY this document to answer or follow the instruction: {current_content}\n\nUser: {doc_question}")
            st.write(res.text)

# --- TASK 3: SEARCH & EDIT FILES ---
elif choice == "3. Search & Edit Files":
    st.write("### 📂 The Main Brain Database")
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

# --- TASK 4: THE COURTROOM (Chat & Archive) ---
elif choice == "4. The Courtroom (Chat)":
    st.write("### 💬 The Courtroom")
    # Only search documents that have been approved (No [HOLD] tags)
    docs = supabase.table("documents").select("title, content").not_.ilike("title", "%[HOLD]%").execute()
    all_text = "\n".join([f"[{d['title']}]: {d['content']}" for d in docs.data]) if docs.data else ""

    user_question = st.text_area("Ask your Brain, plan a strategy, or analyze facts...")

    if user_question and all_text:
        if st.button("Run Analysis"):
            with st.spinner("Analyzing..."):
                prompt1 = f"Answer this question using only the provided files. Cite [Title].\nDATA:\n{all_text}\nQUESTION:\n{user_question}"
                res1 = model.generate_content(prompt1).text
                
                # Store the result in Streamlit session state so we can archive it
                st.session_state['last_q'] = user_question
                st.session_state['last_a'] = res1
                
                st.subheader("AI Findings:")
                st.write(res1)
                
        # The Archive System
        if 'last_a' in st.session_state:
            st.divider()
            archive_note = st.text_input("Add any personal thoughts or actions you plan to take based on this:")
            if st.button("💾 Archive this Conversation"):
                date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                archive_title = f"[ARCHIVE] Chat Log - {date_str}"
                archive_content = f"USER ASKED:\n{st.session_state['last_q']}\n\nAI REPLIED:\n{st.session_state['last_a']}\n\nMY THOUGHTS/ACTIONS:\n{archive_note}"
                
                supabase.table("documents").insert({"title": archive_title, "content": archive_content}).execute()
                st.success("Conversation permanently archived to the Brain!")
