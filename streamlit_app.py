import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader
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
menu = ["1. Mass Intake (Upload)", "2. The Main Database", "3. The Courtroom (Chat)"]
choice = st.sidebar.selectbox("Navigate", menu)

# --- TASK 1: MASS INTAKE ---
if choice == "1. Mass Intake (Upload)":
    st.write("### 📥 Intake & Mass Upload")
    st.info("Files uploaded here are processed and sent directly into the Main Brain Database.")
    
    uploaded_files = st.file_uploader("Drag and drop files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    if uploaded_files:
        if st.button(f"Scan & Send {len(uploaded_files)} Files to Database"):
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
                            # Generate title
                            name_prompt = f"Create a short, professional title (max 6 words) for this document: {content[:1000]}"
                            ai_title = model.generate_content(name_prompt).text.strip().replace('"', '')
                            
                            # Send directly to database WITHOUT the [HOLD] tag
                            supabase.table("documents").insert({"title": ai_title, "content": content}).execute()
                            st.write(f"✅ Added to Brain: **{ai_title}**")
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {e}")
                            
            st.success("Intake complete! Go to The Main Database to view files.")

# --- TASK 2: SEARCH & EDIT FILES ---
elif choice == "2. The Main Database":
    st.write("### 📂 The Main Brain Database")
    if st.button("🔄 Sync & Refresh Database"):
        st.cache_data.clear()
        st.rerun()

    search_query = st.text_input("Search files...")
    # Clean, simple database calls with no complex filters
    docs = supabase.table("documents").select("*").ilike("title", f"%{search_query}%").execute() if search_query else supabase.table("documents").select("*").execute()
    
    for d in docs.data:
        with st.expander(f"📄 {d['title']}"):
            new_title = st.text_input("Edit Title:", d['title'], key=f"title_{d['id']}")
            new_edit = st.text_area("Edit Content:", d['content'], height=200, key=f"edit_{d['id']}")
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

# --- TASK 3: THE COURTROOM (Chat & Archive) ---
elif choice == "3. The Courtroom (Chat)":
    st.write("### 💬 The Courtroom")
    
    # Pull all documents from the database directly
    docs = supabase.table("documents").select("title, content").execute()
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
