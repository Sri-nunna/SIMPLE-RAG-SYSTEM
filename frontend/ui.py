import streamlit as st
import sys
import os
from pathlib import Path

# ensure parent project folder is importable so we can `import backend.*`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from backend import ingest as backend_ingest
    from backend import investigator as backend_investigator
except Exception:
    backend_ingest = None
    backend_investigator = None

def initialize_page_styles():
    """Defines global layout config and applies a safe dark cyber aesthetic framework."""
    st.set_page_config(
        page_title="AI Detective Agency",
        page_icon="🕵️‍♂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Re-engineered CSS injection to ensure it never overrides structural visibility
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        [data-testid="stSidebar"] {
            background-color: #262626;
        }
        h1, h2, h3, p, span {
            color: #ffffff !important;
        }
        .stButton>button {
            background-color: #ff4b4b !important;
            color: white !important;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renders main workspace splash introduction headers."""
    st.markdown("<h1 style='color: #ff4b4b !important;'>🕵️‍♂️ AI Detective — RAG Powered Investigation System</h1>", unsafe_allow_html=True)
    st.caption("Upload case files, analyze logs, and interrogate the evidence to solve the crime.")
    st.write("---")

def render_suggested_queries():
    """Renders interactive quick-action prompt macro elements."""
    st.subheader("💡 Suggested Lines of Questioning")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🕵️ Who is the prime suspect?"):
            st.session_state.quick_query = "Who is the prime suspect based on the evidence?"
    with col2:
        if st.button("⏰ What happened at 2 AM?"):
            st.session_state.quick_query = "What happened at 2 AM according to logs or statements?"
    with col3:
        if st.button("⚠️ Summarize suspicious activity"):
            st.session_state.quick_query = "Summarize any suspicious activities or anomalies found."
    st.write("---")


def main():
    """Initialize the page and render the top-level UI."""
    initialize_page_styles()
    if 'quick_query' not in st.session_state:
        st.session_state.quick_query = ""

    render_header()

    # Step 1: Upload / ingest evidence
    st.subheader("1) Upload Evidence")
    uploaded = st.file_uploader("Drop evidence files here (logs, txt, images)", accept_multiple_files=True)

    if uploaded:
        st.info(f"{len(uploaded)} file(s) ready to ingest")

    if st.button("Ingest Evidence"):
        if not uploaded:
            st.warning("Please select one or more files before ingesting.")
        else:
            if backend_ingest is None:
                st.error("Backend ingestion module not available.")
            else:
                with st.spinner("Saving files..."):
                    saved = backend_ingest.save_uploaded_files(uploaded)
                    st.session_state.evidence_paths = saved
                st.success(f"Saved {len(saved)} file(s).")

                # build the index now (study files)
                with st.spinner("Indexing evidence (studying files)..."):
                    idxpath = backend_ingest.build_index()
                    st.session_state.index_path = idxpath
                    st.session_state.index_ready = True
                st.success("Index built. The system has studied the evidence and is ready to answer questions.")

    # If evidence is present, run a light analysis and show queries
    evidence = st.session_state.get('evidence_paths', None)
    if evidence or st.session_state.get('index_ready'):
        st.subheader("2) Evidence Summary")
        if backend_investigator is None:
            st.write("Backend investigator not available - showing filenames:")
            st.write(evidence)
        else:
            # prefer index-based summary when available
            idx = st.session_state.get('index_path')
            summary = backend_investigator.analyze_evidence(evidence if not idx else idx)
            st.write(summary.get('summary'))
            st.write(summary.get('files'))

        # Step 3: Suggested queries only after ingestion
        render_suggested_queries()

        # Display the selected quick query (if any) and answer it using backend
        if st.session_state.get('quick_query'):
            st.markdown("---")
            st.subheader("Selected Query")
            st.write(st.session_state.quick_query)

            if backend_investigator is None:
                st.error("Investigator backend not available to answer queries.")
            else:
                with st.spinner("Analyzing evidence and answering query..."):
                    result = backend_investigator.answer_query(evidence, st.session_state.quick_query)
                st.subheader("Answer")
                st.write(result.get('answer'))

            # Chat interface: ask arbitrary questions after ingestion
            st.write("---")
            st.subheader("Chat with the evidence")
            if 'chat' not in st.session_state:
                st.session_state.chat = []

            col_q, col_clear = st.columns([4,1])
            with col_q:
                user_q = st.text_input("Ask a question about the ingested evidence:")
            with col_clear:
                if st.button("Clear chat"):
                    st.session_state.chat = []

            if st.button("Ask") and user_q:
                if backend_investigator is None:
                    st.error("Investigator backend not available.")
                else:
                    idx = st.session_state.get('index_path')
                    with st.spinner("Searching evidence and composing answer..."):
                        ans = backend_investigator.answer_query(idx or evidence, user_q)
                    st.session_state.chat.append({"role": "user", "text": user_q})
                    st.session_state.chat.append({"role": "assistant", "text": ans.get('answer', 'No answer')})

            # Render chat history
            if st.session_state.chat:
                st.markdown("---")
                st.subheader("Conversation")
                for msg in st.session_state.chat:
                    if msg['role'] == 'user':
                        st.markdown(f"**You:** {msg['text']}")
                    else:
                        st.markdown(f"**Agent:** {msg['text']}")


if __name__ == "__main__":
    main()