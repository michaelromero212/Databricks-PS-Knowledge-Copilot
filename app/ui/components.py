import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Databricks PS Knowledge Copilot",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    st.markdown("""
        <style>
        .main {
            background-color: #FFFFFF;
        }
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 1px solid #E0E0E0;
            padding: 10px;
        }
        .stButton > button {
            border-radius: 10px;
            background-color: #FF3621; /* Databricks Orange */
            color: white;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #D92B19;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #1B3139; /* Databricks Navy */
            font-family: 'Inter', sans-serif;
        }
        .source-card {
            background-color: #F5F7F8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #FF3621;
        }
        </style>
    """, unsafe_allow_html=True)

def sidebar_info():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=150)
        st.markdown("### PS Knowledge Copilot")
        st.markdown("---")
        st.markdown("**Status:** 🟢 Online")
        st.markdown("**Vector Store:** ChromaDB (Local)")
        st.markdown("**LLM:** LaMini-Flan-T5 (Local)")
        st.markdown("---")
        st.info("This tool helps Databricks PS consultants find answers quickly from internal docs and public guides.")
