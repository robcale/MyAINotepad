import streamlit as st
import datetime
import time
import google.generativeai as genai

# --- CONFIGURATION ---
# (Keep your existing API key setup here)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API Key not found. Please check your Streamlit Secrets.")

st.title("⚖️ Rob's AI Case Files")
st.subheader("📝 Smart Add to the Brain")

# --- THE NEW UNIQUE NAMING SYSTEM ---
def generate_unique_id():
    # Uses a combination of a Unix timestamp (seconds) and a microsecond counter
    # Example format: Case-1712771234-56789
    timestamp = int(time.time())
    micro = datetime.datetime.now().strftime("%f")
    return f"Case-{timestamp}-{micro}"

# --- FILE UPLOAD SECTION ---
uploaded_files = st.file_uploader("Upload Multiple Files (PDF, Word, TXT)", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # 1. Generate the unique ID/Number
        unique_title = generate_unique_id()
        
        # 2. Read the actual content
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        
        st.info(f"Processing: {uploaded_file.name} as **{unique_title}**")
        
        # --- DATABASE INJECTION ---
        # Replace the below with your specific database saving logic
        # (e.g., st.session_state, SQLite, or a cloud DB)
        
        try:
            # We are ignoring the AI naming check (line 52) and using unique_title instead
            # This bypasses the google.api_core.exceptions.NotFound error
            
            # TODO: Your code to save 'file_content' with 'unique_title' goes here
            
            st.success(f"Successfully added to the brain! ID: {unique_title}")
        except Exception as e:
            st.error(f"Failed to save {unique_title}: {e}")

# --- OTHER METHODS ---
# (Keep your Voice Memo, Manual Entry, and OCR sections below)
