import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Vietnam Tourism RAG Chatbot",
    page_icon="",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("Vietnam Tourism RAG")
    st.caption("Hybrid dense + BM25 + RRF retrieval with citations")
    top_k = st.slider("Retrieved chunks", 3, 10, 5)

st.title("Vietnam Tourism RAG Chatbot")
st.caption("Ask questions about the collected Vietnam tourism law and public travel corpus.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            metadata = source["metadata"]
            label = metadata.get("title") or metadata.get("source")
            with st.expander(f"{label} - {source['retrieval_method']} - {source['score']:.4f}"):
                if metadata.get("url"):
                    st.markdown(f"Source URL: {metadata['url']}")
                else:
                    st.markdown(f"Source file: {metadata.get('source')}")
                st.markdown(source["content"])

query = st.chat_input("Enter a question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving evidence..."):
            result = generate_with_citation(query, top_k)
        answer = result["answer"]
        sources = result["sources"]
        st.markdown(answer)
        st.caption(f"Retrieval source: {result['retrieval_source']}")

        for source in sources:
            metadata = source["metadata"]
            label = metadata.get("title") or metadata.get("source")
            with st.expander(f"{label} - {source['retrieval_method']} - {source['score']:.4f}"):
                if metadata.get("url"):
                    st.markdown(f"Source URL: {metadata['url']}")
                else:
                    st.markdown(f"Source file: {metadata.get('source')}")
                st.markdown(source["content"])

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
