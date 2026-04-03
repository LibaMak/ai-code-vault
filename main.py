import random
import time

import streamlit as st


st.set_page_config(
    page_title="AI Code Vault Demo",
        page_icon="A",
    layout="wide",
)


# Dark-theme styling for a demo-friendly look.
st.markdown(
    """
    <style>
        :root {
            --bg: #0f1117;
            --surface: #1a1f2e;
            --surface-2: #242b3d;
            --text: #f2f5ff;
            --muted: #a8b1cc;
            --accent: #40c4ff;
            --success: #00d084;
            --warning: #ffc857;
        }
        .stApp {
            background: radial-gradient(circle at 20% 20%, #1a2238 0%, var(--bg) 45%);
            color: var(--text);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }
        h1, h2, h3, h4 {
            color: var(--text);
        }
        .subtle {
            color: var(--muted);
        }
        .card {
            background: linear-gradient(145deg, var(--surface), var(--surface-2));
            border: 1px solid #2d3750;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .confidence {
            color: var(--success);
            font-weight: 700;
        }
        .source {
            color: var(--accent);
        }
        div[data-baseweb="input"] {
            background: #121826;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def check_login(username: str, password: str) -> bool:
    normalized_username = username.strip().lower()
    normalized_password = password.strip()
    return normalized_username == "demo" and normalized_password == "vault123"


def get_mock_response(question: str) -> tuple[str, list[str]]:
    lowered = question.lower()

    if "model" in lowered or "ai" in lowered:
        return (
            "The current mock pipeline uses retrieval-augmented prompts with a compact reasoning layer for response synthesis.",
            [
                "Model_Design_Guide.pdf (Section 2.1)",
                "pipeline_overview.py (lines 14-39)",
            ],
        )

    if "index" in lowered or "file" in lowered or "vault" in lowered:
        return (
            "Indexing is simulated as complete: files are parsed, chunked, and embedded into a placeholder vector store for this demo.",
            [
                "indexing_notes.pdf (Page 3)",
                "index_manager.py (lines 51-87)",
            ],
        )

    if "speed" in lowered or "performance" in lowered:
        return (
            "Processing speed remains within target demo thresholds with stable response generation under concurrent prompts.",
            [
                "analytics_summary.pdf (Page 1)",
                "benchmark_runner.py (lines 8-26)",
            ],
        )

    fallback_responses = [
        (
            "The vault pipeline completed document parsing and generated context-ready snippets for assistant responses.",
            [
                "vault_status_report.pdf (Page 2)",
                "context_builder.py (lines 21-63)",
            ],
        ),
        (
            "Mock retrieval indicates relevant source alignment and high confidence on this query category.",
            [
                "retrieval_log.pdf (Page 4)",
                "retriever.py (lines 34-59)",
            ],
        ),
    ]
    return random.choice(fallback_responses)


def render_login_page() -> None:
    st.title("AI Code Vault - Login")
    st.caption("Category 9 | Secure Access (Demo Mode)")

    if st.button("Use Demo Credentials", use_container_width=True):
        st.session_state.is_authenticated = True
        st.success("Demo access enabled.")
        st.rerun()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sign in to continue")
    username = st.text_input("Username", placeholder="demo")
    password = st.text_input("Password", type="password", placeholder="vault123")

    if st.button("Login", use_container_width=True):
        if check_login(username, password):
            st.session_state.is_authenticated = True
            st.success("Login successful. Access granted.")
            st.rerun()
        else:
            st.error("Invalid credentials. Try demo / vault123 (not case-sensitive for username).")

    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_page() -> None:
    st.title("AI Assistant Chat")
    st.caption("Category 4 & 5 | Mock Response + Confidence + Citations")

    st.markdown('<div class="card">Ask anything about your vault data.</div>', unsafe_allow_html=True)

    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(item["question"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])
            st.markdown('<p class="confidence">Confidence Score: 95%</p>', unsafe_allow_html=True)
            st.markdown("**Source Citations:**")
            for src in item["sources"]:
                st.markdown(f"- <span class='source'>{src}</span>", unsafe_allow_html=True)

    question = st.chat_input("Ask a question...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(1.2)
                answer, sources = get_mock_response(question)

            st.markdown(answer)
            st.markdown('<p class="confidence">Confidence Score: 95%</p>', unsafe_allow_html=True)
            st.markdown("**Source Citations:**")
            for src in sources:
                st.markdown(f"- <span class='source'>{src}</span>", unsafe_allow_html=True)

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
                "sources": sources,
            }
        )


def render_vault_page() -> None:
    st.title("Vault Overview")
    st.caption("Indexed Files (Hardcoded Demo Data)")

    indexed_files = [
        "main.py",
        "retriever.py",
        "index_manager.py",
        "context_builder.py",
        "benchmark_runner.py",
        "Model_Design_Guide.pdf",
        "indexing_notes.pdf",
        "analytics_summary.pdf",
        "vault_status_report.pdf",
        "retrieval_log.pdf",
    ]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Indexed Files")
    for file_name in indexed_files:
        icon = "[PY]" if file_name.endswith(".py") else "[PDF]"
        st.markdown(f"- {icon} {file_name}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_page() -> None:
    st.title("Analytics Dashboard")
    st.caption("Category 6 | Processing Speed vs Accuracy")

    processing_speed = 82
    accuracy = 95

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Performance Metrics")
    left, right = st.columns(2)
    left.metric("Processing Speed", f"{processing_speed}%")
    right.metric("Accuracy", f"{accuracy}%")

    chart_data = {
        "Metric": ["Processing Speed", "Accuracy"],
        "Score": [processing_speed, accuracy],
    }
    st.bar_chart(chart_data, x="Metric", y="Score", color="#40c4ff")
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> str:
    st.sidebar.title("AI Code Vault")
    st.sidebar.caption("Demo Navigation")

    selected = st.sidebar.radio(
        "Go to",
        ["Chat", "Vault", "Analytics"],
        index=0,
    )

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.chat_history = []
        st.rerun()

    return selected


if not st.session_state.is_authenticated:
    render_login_page()
else:
    page = render_sidebar()

    if page == "Chat":
        render_chat_page()
    elif page == "Vault":
        render_vault_page()
    elif page == "Analytics":
        render_analytics_page()
