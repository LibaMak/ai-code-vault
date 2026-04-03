import random
import time
import streamlit as st
import pandas as pd

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI Code Vault",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# ADVANCED DARK PURPLE THEME CSS
# -----------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #09070d, #120c1f, #1a1229);
        color: #f5f3ff;
        font-family: 'Segoe UI', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0911, #140f1f);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] * {
        color: #f1ebff !important;
    }

    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    p, span, div, label {
        color: #d6cfff;
    }

    .glass-card {
        background: rgba(32, 21, 50, 0.72);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(180, 130, 255, 0.15);
        border-radius: 20px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        margin-bottom: 1rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(76,29,149,0.55), rgba(17,24,39,0.72));
        border: 1px solid rgba(180, 130, 255, 0.15);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        margin-bottom: 1.5rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #7b2ff7, #9f44ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        transition: 0.3s ease;
        box-shadow: 0 0 18px rgba(123, 47, 247, 0.35);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(90deg, #8e44ff, #b067ff);
        box-shadow: 0 0 25px rgba(159, 68, 255, 0.55);
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        background-color: rgba(20, 16, 31, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(180, 130, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: rgba(20, 16, 31, 0.95) !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid rgba(180, 130, 255, 0.25) !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(32, 21, 50, 0.72);
        border: 1px solid rgba(180, 130, 255, 0.15);
        padding: 1rem;
        border-radius: 18px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    .chat-user {
        background: rgba(80, 40, 130, 0.35);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(180, 130, 255, 0.15);
    }

    .chat-ai {
        background: rgba(20, 16, 31, 0.95);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(180, 130, 255, 0.15);
    }

    .confidence {
        color: #7effc1;
        font-weight: 700;
        font-size: 15px;
    }

    .source {
        color: #8fd3ff;
        font-weight: 500;
    }

    .small-muted {
        color: #a89bc7;
        font-size: 14px;
    }

    .status-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(123,47,247,0.18);
        border: 1px solid rgba(180,130,255,0.15);
        margin-right: 8px;
        margin-top: 8px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# -----------------------------------
# AUTH
# -----------------------------------
def check_login(username: str, password: str) -> bool:
    return username.strip().lower() == "demo" and password.strip() == "vault123"

# -----------------------------------
# MOCK AI RESPONSE (temporary)
# Replace later with your real backend/database call
# -----------------------------------
def get_mock_response(question: str):
    lowered = question.lower()

    if "database" in lowered or "sql" in lowered:
        return (
            "Database connector is currently in demo mode. In production, this section will query your backend and retrieve live structured records.",
            [
                "db_connector.py (future backend module)",
                "schema_reference.sql (planned integration)"
            ],
        )

    if "model" in lowered or "ai" in lowered:
        return (
            "The active mock pipeline uses retrieval-augmented prompting and semantic ranking before response generation.",
            [
                "Model_Design_Guide.pdf (Section 2.1)",
                "pipeline_overview.py (lines 14-39)",
            ],
        )

    if "index" in lowered or "file" in lowered or "vault" in lowered:
        return (
            "Vault indexing is simulated as complete. Files are parsed, chunked, and prepared for semantic retrieval.",
            [
                "indexing_notes.pdf (Page 3)",
                "index_manager.py (lines 51-87)",
            ],
        )

    return (
        "Your AI assistant is currently running in demo mode. Once connected, this panel will respond using your actual backend and database.",
        [
            "backend_api.py (future integration)",
            "vector_store.py (future integration)"
        ],
    )

# -----------------------------------
# LOGIN PAGE
# -----------------------------------
def render_login_page():
    st.markdown("<h1 style='text-align:center;'>🧠 AI Code Vault</h1>", unsafe_allow_html=True)
    st.markdown("<p class='small-muted' style='text-align:center;'>Secure AI Retrieval & Intelligent Chat Workspace</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.25, 1])

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔐 Login to Access Workspace")

        username = st.text_input("Username", placeholder="demo")
        password = st.text_input("Password", type="password", placeholder="vault123")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Login", use_container_width=True):
                if check_login(username, password):
                    st.session_state.is_authenticated = True
                    st.session_state.current_page = "workspace"
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use demo / vault123")

        with c2:
            if st.button("Use Demo Login", use_container_width=True):
                st.session_state.is_authenticated = True
                st.session_state.current_page = "workspace"
                st.success("Demo access enabled.")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='small-muted'>This login screen leads to the main AI workspace where the chatbot will later connect to your real backend, database, and retrieval pipeline.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR INSIDE WORKSPACE
# -----------------------------------
def render_sidebar():
    st.sidebar.markdown("## 🧠 AI Code Vault")
    st.sidebar.markdown("<p class='small-muted'>Main AI Workspace</p>", unsafe_allow_html=True)

    selected = st.sidebar.radio(
        "Navigation",
        ["🤖 Main Chatbot", "📁 Vault Files", "📊 Analytics", "⚙ Backend Status"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Live System State")
    st.sidebar.success("Workspace Active")
    st.sidebar.info("Authentication Passed")
    st.sidebar.warning("Backend Connection: Demo Mode")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_page = "login"
        st.session_state.chat_history = []
        st.rerun()

    return selected

# -----------------------------------
# MAIN CHATBOT PAGE
# -----------------------------------
def render_main_chatbot():
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.title("🤖 Main Chatbot Interface")
    st.write("This is your **main AI workspace**. Later, this chatbot will connect to your **actual database, backend API, document vault, and retrieval pipeline**.")
    st.markdown("""
    <span class="status-pill">AI Assistant Ready</span>
    <span class="status-pill">Backend Placeholder Active</span>
    <span class="status-pill">Database Integration Pending</span>
    <span class="status-pill">RAG Pipeline Ready for Hookup</span>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">💡 <b>Future purpose:</b> Ask database questions, retrieve file knowledge, generate intelligent responses, and connect with your backend.</div>', unsafe_allow_html=True)

    for item in st.session_state.chat_history:
        st.markdown(f'<div class="chat-user"><b>👤 You:</b><br>{item["question"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="chat-ai"><b>🤖 AI Assistant:</b><br>{item["answer"]}'
            f'<br><br><span class="confidence">Confidence Score: 95%</span>'
            f'<br><br><b>Source Citations:</b><br>'
            + "".join([f"<div class='source'>• {src}</div>" for src in item["sources"]])
            + '</div>',
            unsafe_allow_html=True
        )

    question = st.chat_input("Ask your AI assistant...")

    if question:
        st.markdown(f'<div class="chat-user"><b>👤 You:</b><br>{question}</div>', unsafe_allow_html=True)

        with st.spinner("AI is processing your query..."):
            time.sleep(1.2)

            # -----------------------------------
            # FUTURE BACKEND CONNECTION POINT
            # Replace this later with:
            # answer, sources = call_backend_api(question)
            # -----------------------------------
            answer, sources = get_mock_response(question)

        st.markdown(
            f'<div class="chat-ai"><b>🤖 AI Assistant:</b><br>{answer}'
            f'<br><br><span class="confidence">Confidence Score: 95%</span>'
            f'<br><br><b>Source Citations:</b><br>'
            + "".join([f"<div class='source'>• {src}</div>" for src in sources])
            + '</div>',
            unsafe_allow_html=True
        )

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "sources": sources,
        })

# -----------------------------------
# VAULT PAGE
# -----------------------------------
def render_vault_page():
    st.title("📁 Vault Files")
    st.caption("Hardcoded demo files for now — later connect real uploaded / indexed files")

    indexed_files = [
        "main.py", "retriever.py", "index_manager.py", "context_builder.py",
        "benchmark_runner.py", "Model_Design_Guide.pdf", "indexing_notes.pdf",
        "analytics_summary.pdf", "vault_status_report.pdf", "retrieval_log.pdf"
    ]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📂 Indexed Files")
    for file_name in indexed_files:
        icon = "🐍" if file_name.endswith(".py") else "📄"
        st.markdown(f"- {icon} **{file_name}**")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# ANALYTICS PAGE
# -----------------------------------
def render_analytics_page():
    st.title("📊 Analytics Dashboard")
    st.caption("System metrics for your AI assistant workspace")

    processing_speed = 82
    accuracy = 95
    retrieval_success = 91
    indexed_assets = 10

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ Processing Speed", f"{processing_speed}%")
    c2.metric("🎯 Accuracy", f"{accuracy}%")
    c3.metric("🔍 Retrieval Success", f"{retrieval_success}%")
    c4.metric("📂 Indexed Assets", indexed_assets)

    st.markdown("<br>", unsafe_allow_html=True)

    chart_df = pd.DataFrame({
        "Metric": ["Processing Speed", "Accuracy", "Retrieval Success"],
        "Score": [processing_speed, accuracy, retrieval_success]
    })

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📈 Performance Overview")
    st.bar_chart(chart_df, x="Metric", y="Score")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# BACKEND STATUS PAGE
# -----------------------------------
def render_backend_status():
    st.title("⚙ Backend Connection Panel")
    st.caption("This page shows where your real backend and DB will be connected.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔌 Planned Backend Integration")
    st.write("""
    This is where your system will later connect to:

    - **SQL / Oracle / MySQL / PostgreSQL Database**
    - **Python backend (Flask / FastAPI / Django)**
    - **RAG pipeline**
    - **Vector database**
    - **Document retrieval engine**
    - **AI model response generation**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🧠 Future Chatbot Flow")
    st.code("""
User enters query
   ↓
Frontend (Streamlit)
   ↓
Backend API
   ↓
Database / File Retriever / Vector Search
   ↓
AI Response Generation
   ↓
Answer shown in chatbot
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# APP FLOW
# -----------------------------------
if not st.session_state.is_authenticated or st.session_state.current_page == "login":
    render_login_page()
else:
    selected_page = render_sidebar()

    if selected_page == "🤖 Main Chatbot":
        render_main_chatbot()
    elif selected_page == "📁 Vault Files":
        render_vault_page()
    elif selected_page == "📊 Analytics":
        render_analytics_page()
    elif selected_page == "⚙ Backend Status":
        render_backend_status()
