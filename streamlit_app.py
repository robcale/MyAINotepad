import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

# --- SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", layout="wide")

# Connect to your secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return None

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Add to Case File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

# --- SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", layout="wide")

# Connect to your secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

# --- SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", layout="wide")

# Connect to your secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return None

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Add to Case File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

# --- SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", layout="wide")

# Connect to your secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return None

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Add to Case File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!"import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

# --- SETUP ---
st.set_page_config(page_title="Rob's AI Case Files", layout="wide")

# Connect to your secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return None

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Add to Case File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")  ['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")enerativeMode>
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in   d_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")  ['content']>
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")enerativeMode>
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")
d_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")  ['content']>
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")enerativeMode>
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")
d_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            context = " ".join([d['content'] for d in docs.data])
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")  ['content']>
            # 2. Ask Gemini
            prompt = f"Using these documents: {context}\n\nQuestion: {query}"
            response = model.generate_content(prompt)
            st.markdown("### Answer:")
            st.write(response.text)
        else:
            st.warning("No documents found in the cloud yet. Upload something first!")enerativeMode>
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files") oud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.data:
            contextiveModel('gemini-1.5-flash')
except Exception as e:
    st.error("Check your Streamlit Secrets! Something is missing.")

st.title("📑 Rob's AI Case Files")

# --- HELPER FUNCTIONS ---
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return None

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Add to Case File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        if st.button("Save to Cloud"):
            with st.spinner("Processing text..."):
                file_text = extract_text(uploaded_file)
                data = {"file_name": uploaded_file.name, "content": file_text}
                # Saves to your Supabase table
                supabase.table("documents").insert(data).execute()
                st.success(f"Successfully saved {uploaded_file.name}!")

# --- MAIN INTERFACE: SEARCH ---
query = st.text_input("Ask a question about your files:")

if query:
    with st.spinner("Searching..."):
        # 1. Pull data from Supabase
        docs = supabase.table("documents").select("content").execute()
        if docs.da
