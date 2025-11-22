import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.ui.components import set_page_config, apply_custom_css, sidebar_info
from app.rag.retriever import Retriever
from app.rag.llm_connector import LLMConnector
from app.ingest.document_loader import DocumentLoader
from app.rag.embedder import Embedder
from app.vectorstore.chroma_client import ChromaClient

# Initialize components
# Note: In a real app, these should be cached or initialized once
retriever = Retriever(use_databricks=False) # Default to Chroma for local demo
llm = LLMConnector(provider="huggingface_local")

def main():
    set_page_config()
    apply_custom_css()
    sidebar_info()

    st.title("🧠 Databricks PS Knowledge Copilot")
    st.markdown("Ask questions about Databricks best practices, architecture, and optimization.")

    # Query Input
    query = st.text_input("Enter your question:", placeholder="e.g., How do I optimize MERGE performance?")

    if query:
        with st.spinner("Searching knowledge base..."):
            # 1. Retrieve
            docs = retriever.retrieve(query, k=3)
            
            # 2. Generate Answer
            if docs:
                answer = llm.generate_answer(query, docs)
            else:
                answer = "No relevant documents found."

            # 3. Display Results
            st.markdown("### Answer")
            st.markdown(answer)

            st.markdown("### Sources")
            if docs:
                for doc in docs:
                    with st.container():
                        st.markdown(f"""
                        <div class="source-card">
                            <b>Source:</b> {doc['metadata']['source']}<br>
                            <small>{doc['content'][:200]}...</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No sources cited.")

    # Ingestion Sidebar (for demo purposes)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Admin Tools")
        if st.button("Re-ingest Knowledge Base"):
            with st.spinner("Ingesting documents..."):
                loader = DocumentLoader("./data/example_inputs")
                documents = loader.load_documents()
                
                if documents:
                    # Prepare for Chroma
                    texts = [doc['content'] for doc in documents]
                    metadatas = [{"source": doc['source']} for doc in documents]
                    ids = [doc['source'] for doc in documents]
                    
                    embedder = Embedder()
                    embeddings = embedder.generate_embeddings(texts)
                    
                    chroma = ChromaClient()
                    chroma.upsert_documents(texts, metadatas, ids, embeddings)
                    st.success(f"Ingested {len(documents)} documents!")
                else:
                    st.warning("No documents found in data/example_inputs")

if __name__ == "__main__":
    main()
