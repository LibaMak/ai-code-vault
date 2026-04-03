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
    /* Main App */
    .stApp {
        background: linear-gradient(135deg, #09070d, #120c1f, #1a1229);
        color: #f5f3ff;
        font-family: 'Segoe UI', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0911, #140f1f);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] * {
        color: #f1ebff !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    p, span, div, label {
        color: #d6cfff;
    }

    /* Glass Cards */
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

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7b2ff7, #9f44ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: 0.3s ease;
        box-shadow: 0 0 18px rgba(123, 47, 247, 0.35);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(90deg, #8e44ff, #b067ff);
        box-shadow: 0 0 25px rgba(159, 68, 255, 0.55);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background-color: rgba(20, 16, 31, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(180, 130, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
    }

    /* Chat Input */
    div[data-testid="stChatInput"] textarea {
        background-color: rgba(20, 16, 31, 0.95) !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid rgba(180, 130, 255, 0.25) !important;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background: rgba(32, 21, 50, 0.72);
        border: 1px solid rgba(180, 130, 255, 0.15);
        padding: 1rem;
        border-radius: 18px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    /* Chat Messages */
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

    /* Divider line */
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
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

# -----------------------------------
# AUTH
# -----------------------------------
def check_login(username: str, password: str) -> bool:
    return username.strip().lower() == "demo" and password.strip() == "vault123"

# -----------------------------------
# MOCK AI RESPONSES
# -----------------------------------
def get_mock_response(question: str):
    lowered = question.lower()

    if "model" in lowered or "ai" in lowered:
        return (
            "The active mock pipeline uses retrieval-augmented prompting, semantic ranking, and a lightweight reasoning layer for response synthesis.",
            [
                "Model_Design_Guide.pdf (Section 2.1)",
                "pipeline_overview.py (lines 14-39)",
            ],
        )

    if "index" in lowered or "file" in lowered or "vault" in lowered:
        return (
            "Vault indexing is marked complete. Documents are parsed, chunked, embedded, and stored into a placeholder semantic vector structure for demo retrieval.",
            [
                "indexing_notes.pdf (Page 3)",
                "index_manager.py (lines 51-87)",
            ],
        )

    if "speed" in lowered or "performance" in lowered:
        return (
            "System performance remains within target demo thresholds, maintaining stable response generation and retrieval under concurrent prompt simulation.",
            [
                "analytics_summary.pdf (Page 1)",
                "benchmark_runner.py (lines 8-26)",
            ],
        )

    fallback_responses = [
        (
            "The vault pipeline successfully parsed all mock documents and prepared context-aware snippets for downstream assistant generation.",
            [
                "vault_status_report.pdf (Page 2)",
                "context_builder.py (lines 21-63)",
            ],
        ),
        (
            "Mock retrieval indicates strong semantic alignment and high confidence for this query class across indexed vault assets.",
            [
                "retrieval_log.pdf (Page 4)",
                "retriever.py (lines 34-59)",
            ],
        ),
    ]
    return random.choice(fallback_responses)

# -----------------------------------
# LOGIN PAGE
# -----------------------------------
def render_login_page():
    st.markdown("<h1 style='text-align:center;'>🧠 AI Code Vault</h1>", unsafe_allow_html=True)
    st.markdown("<p class='small-muted' style='text-align:center;'>Secure AI Retrieval & Code Intelligence Platform</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔐 Sign in to continue")
        username = st.text_input("Username", placeholder="demo")
        password = st.text_input("Password", type="password", placeholder="vault123")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login", use_container_width=True):
                if check_login(username, password):
                    st.session_state.is_authenticated = True
                    st.success("Access granted.")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use demo / vault123")

        with c2:
            if st.button("Use Demo Login", use_container_width=True):
                st.session_state.is_authenticated = True
                st.success("Demo access enabled.")
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<p class='small-muted'>Demo credentials are enabled for project presentation purposes.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------
def render_sidebar():
    st.sidebar.markdown("## 🧠 AI Code Vault")
    st.sidebar.markdown("<p class='small-muted'>Intelligent Retrieval Dashboard</p>", unsafe_allow_html=True)

    selected = st.sidebar.radio(
        "Navigation",
        ["💬 Chat Assistant", "📁 Vault Overview", "📊 Analytics Dashboard"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ System Status")
    st.sidebar.success("Vault Indexed")
    st.sidebar.info("Demo Mode Active")
    st.sidebar.warning("Confidence Engine Online")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.chat_history = []
        st.rerun()

    return selected

# -----------------------------------
# CHAT PAGE
# -----------------------------------
def render_chat_page():
    st.title("💬 AI Assistant Chat")
    st.caption("Ask anything about your indexed vault content.")

    st.markdown('<div class="glass-card">💡 <b>Try:</b> "How does the indexing work?" or "What model is being used?"</div>', unsafe_allow_html=True)

    for item in st.session_state.chat_history:
        st.markdown(f'<div class="chat-user"><b>👤 You:</b><br>{item["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai"><b>🤖 AI Assistant:</b><br>{item["answer"]}<br><br><span class="confidence">Confidence Score: 95%</span><br><br><b>Source Citations:</b><br>' + "".join([f"<div class='source'>• {src}</div>" for src in item["sources"]]) + '</div>', unsafe_allow_html=True)

    question = st.chat_input("Ask a question about the vault...")
    if question:
        st.markdown(f'<div class="chat-user"><b>👤 You:</b><br>{question}</div>', unsafe_allow_html=True)

        with st.spinner("AI is analyzing vault context..."):
            time.sleep(1.2)
            answer, sources = get_mock_response(question)

        st.markdown(f'<div class="chat-ai"><b>🤖 AI Assistant:</b><br>{answer}<br><br><span class="confidence">Confidence Score: 95%</span><br><br><b>Source Citations:</b><br>' + "".join([f"<div class='source'>• {src}</div>" for src in sources]) + '</div>', unsafe_allow_html=True)

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "sources": sources,
        })

# -----------------------------------
# VAULT PAGE
# -----------------------------------
def render_vault_page():
    st.title("📁 Vault Overview")
    st.caption("Indexed Assets (Hardcoded Demo Data)")

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
    st.caption("System Performance & Accuracy Metrics")

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
# APP FLOW
# -----------------------------------
if not st.session_state.is_authenticated:
    render_login_page()
else:
    page = render_sidebar()

    if page == "💬 Chat Assistant":
        render_chat_page()
    elif page == "📁 Vault Overview":
        render_vault_page()
    elif page == "📊 Analytics Dashboard":
        render_analytics_page()
