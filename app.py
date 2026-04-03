import random
import time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="AI Code Vault",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        :root {
            --bg-main: #0a0f1e;
            --bg-panel: #111a2f;
            --bg-card: #16233f;
            --text-main: #e6edf8;
            --text-subtle: #9fb2d9;
            --accent: #3fb4ff;
            --accent-2: #21e3c5;
            --ok: #29d18c;
            --warn: #ffc857;
            --line: #273a5d;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 10%, #16284a 0%, #0d1830 25%, #0a0f1e 60%),
                linear-gradient(140deg, #0b1428 0%, #0a0f1e 100%);
            color: var(--text-main);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1930 0%, #0d1528 100%);
            border-right: 1px solid var(--line);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.5rem;
            max-width: 1200px;
        }

        .hero {
            border: 1px solid var(--line);
            background: linear-gradient(145deg, #162743 0%, #0f1c34 100%);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }

        .card {
            border: 1px solid var(--line);
            background: linear-gradient(145deg, #152440 0%, #111d36 100%);
            border-radius: 12px;
            padding: 0.95rem 1.1rem;
            margin-bottom: 0.9rem;
        }

        .muted {
            color: var(--text-subtle);
        }

        .score-pill {
            display: inline-block;
            border: 1px solid #2f9d8a;
            color: #8ef2db;
            background: rgba(33, 227, 197, 0.1);
            border-radius: 999px;
            padding: 0.15rem 0.65rem;
            font-size: 0.85rem;
            margin-top: 0.35rem;
        }

        .source-chip {
            border-left: 3px solid var(--accent);
            background: rgba(63, 180, 255, 0.08);
            padding: 0.45rem 0.6rem;
            margin-top: 0.4rem;
            border-radius: 6px;
            color: #b7d8f5;
        }

        h1, h2, h3, h4, h5 {
            color: var(--text-main);
            letter-spacing: 0.2px;
        }

        div[data-testid="stMetric"] {
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0.65rem;
            background: linear-gradient(145deg, #15223c, #101a31);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "latencies" not in st.session_state:
        st.session_state.latencies = [1.84, 1.62, 1.47, 1.73, 1.56, 1.35, 1.41, 1.28, 1.59, 1.44]


def handle_login(username: str, password: str) -> bool:
    return username.strip().lower() == "admin" and password.strip() == "vault123"


def render_login() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.title("AI Code Vault")
    st.markdown("<p class='muted'>Secure Agentic RAG access portal</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.35, 1])
    with center:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Login")
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="vault123")

        c1, c2 = st.columns(2)
        with c1:
            sign_in = st.button("Sign In", use_container_width=True)
        with c2:
            quick_demo = st.button("Use Demo Login", use_container_width=True)

        if quick_demo:
            st.session_state.is_logged_in = True
            st.success("Demo access enabled.")
            st.rerun()

        if sign_in:
            if handle_login(username, password):
                st.session_state.is_logged_in = True
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid credentials. Use admin / vault123 for demo.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_dashboard() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.header("Dashboard")
    st.markdown("<p class='muted'>Operational overview of the AI Code Vault platform.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Search Accuracy", "94%")
    c2.metric("Avg Latency", "1.2s")
    c3.metric("Files Indexed", "124")

    st.markdown('<div class="card"><span class="muted">System Status:</span> All core services healthy. Embedding index ready for retrieval.</div>', unsafe_allow_html=True)


def render_file_pipeline() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.header("File Pipeline")
    st.markdown("<p class='muted'>Upload files to simulate chunking and embedding workflow.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    files = st.file_uploader(
        "Upload one or more files",
        accept_multiple_files=True,
        type=["txt", "pdf", "docx", "csv", "md", "py"],
    )

    if files:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"Queued files: {len(files)}")
        if st.button("Run Ingestion Pipeline", use_container_width=True):
            progress = st.progress(0, text="Initializing pipeline...")
            stages = [
                (18, "Validating files..."),
                (42, "Simulating chunking strategy..."),
                (68, "Generating embeddings..."),
                (90, "Building retrieval index..."),
                (100, "Finalizing and storing metadata..."),
            ]
            for value, message in stages:
                time.sleep(0.6)
                progress.progress(value, text=message)
            st.success("Pipeline complete: files processed, chunked, and embedded successfully.")
        st.markdown("</div>", unsafe_allow_html=True)


def build_agentic_response(query: str) -> tuple[str, str, str]:
    q = query.lower()
    if "security" in q or "secure" in q:
        answer = (
            "AI Code Vault applies a credential-gated entry point, environment-based secret handling, "
            "and retrieval-grounded response composition before answer delivery."
        )
        source = "Source: Security_Policy_v2.pdf - Section 3.2"
        confidence = "93%"
    elif "rag" in q or "retrieval" in q:
        answer = (
            "The agent first retrieves top semantic chunks, ranks relevance, and then synthesizes a grounded "
            "response using context windows from the indexed knowledge base."
        )
        source = "Source: RAG_Architecture_Notes.md - Retrieval Flow"
        confidence = "95%"
    else:
        answer = (
            "Based on indexed project context, the best route is to run semantic retrieval first, validate source "
            "evidence, and then return a concise answer with confidence tracking."
        )
        source = "Source: Agent_Orchestration_Guide.md - Decision Layer"
        confidence = "92%"
    return answer, source, confidence


def render_agentic_chat() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.header("Agentic Chat")
    st.markdown("<p class='muted'>Ask questions and receive smart, source-grounded responses.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(item["query"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])
            st.markdown(f"<div class='source-chip'>{item['source']}</div>", unsafe_allow_html=True)
            st.markdown(f"<span class='score-pill'>Confidence Score: {item['confidence']}</span>", unsafe_allow_html=True)

    query = st.chat_input("Ask the agent about your indexed data...")
    if query:
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Agent Routing to Analysis Skill..."):
                time.sleep(1.0)
                answer, source, confidence = build_agentic_response(query)

            st.markdown(answer)
            st.markdown(f"<div class='source-chip'>{source}</div>", unsafe_allow_html=True)
            st.markdown(f"<span class='score-pill'>Confidence Score: {confidence}</span>", unsafe_allow_html=True)

        st.session_state.chat_history.append(
            {
                "query": query,
                "answer": answer,
                "source": source,
                "confidence": confidence,
            }
        )

        # Simulate end-to-end response latency while staying below 2 seconds.
        st.session_state.latencies.append(round(random.uniform(0.95, 1.95), 2))
        st.session_state.latencies = st.session_state.latencies[-10:]


def render_performance_page() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.header("Performance")
    st.markdown("<p class='muted'>Latency trend for the last 10 queries (all below 2 seconds).</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    latencies = st.session_state.latencies[-10:]
    query_ids = [f"Q{i}" for i in range(1, len(latencies) + 1)]
    df = pd.DataFrame({"Query": query_ids, "Latency": latencies})

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(df["Query"], df["Latency"], marker="o", linewidth=2.2, color="#3fb4ff")
    ax.axhline(2.0, color="#ffc857", linestyle="--", linewidth=1.5, label="2.0s Threshold")
    ax.set_ylim(0.7, 2.0)
    ax.set_title("Latency Over Last 10 Queries", color="#e6edf8", pad=10)
    ax.set_xlabel("Query", color="#c8d7f1")
    ax.set_ylabel("Latency (s)", color="#c8d7f1")
    ax.set_facecolor("#101a31")
    fig.patch.set_facecolor("#0f1930")
    ax.grid(True, linestyle=":", alpha=0.35)
    ax.tick_params(colors="#c8d7f1")

    for spine in ax.spines.values():
        spine.set_color("#2d456f")

    ax.legend(facecolor="#101a31", edgecolor="#2d456f", labelcolor="#e6edf8")

    st.pyplot(fig, use_container_width=True)
    st.caption(f"Current average latency: {sum(latencies) / len(latencies):.2f}s")


def render_sidebar() -> str:
    st.sidebar.title("AI Code Vault")
    st.sidebar.caption("Secure Agentic RAG Console")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "File Pipeline", "Agentic Chat", "Performance"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Session**")
    st.sidebar.markdown("Status: Authenticated")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.chat_history = []
        st.rerun()

    return page


def main() -> None:
    init_state()

    if not st.session_state.is_logged_in:
        render_login()
        return

    page = render_sidebar()

    if page == "Dashboard":
        render_dashboard()
    elif page == "File Pipeline":
        render_file_pipeline()
    elif page == "Agentic Chat":
        render_agentic_chat()
    elif page == "Performance":
        render_performance_page()


if __name__ == "__main__":
    main()
