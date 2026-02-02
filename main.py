import streamlit as st
import os
from dotenv import load_dotenv
from app.ingestor import RepoIngestor
from app.processor import RepoProcessor
import streamlit_mermaid as stmd

load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "code_map" not in st.session_state:
    st.session_state.code_map = None

st.set_page_config(page_title="RepoPilot AI", layout="wide")

st.title("🚀 RepoPilot: Senior Dev Mentor")
st.markdown("Ingest any GitHub repo and visualize its architecture instantly.")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("1. Ingest Repository")
    repo_url = st.text_input("GitHub URL", placeholder="https://github.com/pallets/flask")
    
    st.divider()
    st.header("⚡ Quick Actions")
    if st.button("Generate Onboarding Guide"):
        prompt = "Give me a high-level technical onboarding guide for a new developer. What are the 3 most important files to understand?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        # This will trigger the chat loop automatically

    if st.button("Identify Risk Areas"):
        prompt = "Which parts of this codebase are the most complex or 'brittle' (highest technical debt)?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    if st.button("Clone & Map"):
        if not repo_url or repo_url.strip() == "":
            st.error("Please enter a GitHub URL first!")
        else:
            with st.spinner("Analyzing codebase..."):
                try:
                    ingestor = RepoIngestor()
                    path = ingestor.clone_repo(repo_url)
                    code_map = ingestor.map_codebase(path)
                    st.session_state.code_map = code_map
                    st.success("Codebase Ingested!")
                except Exception as e:
                    st.error(f"Error cloning repository: {str(e)}")

# --- Main Chat Interface ---
if st.session_state.code_map:  # Changed to use the actual value, not just check key
    # Note: messages is already initialized at the top, so we don't need to check here

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "mermaid" in message["content"] and "```mermaid" in message["content"]:
                # Split text and diagram
                parts = message["content"].split("```mermaid")
                st.markdown(parts[0])
                mermaid_code = parts[1].split("```")[0]
                stmd.st_mermaid(mermaid_code)
                if len(parts) > 1 and "```" in parts[1]:
                    st.markdown(parts[1].split("```")[-1])
            else:
                st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Ask about the architecture..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            processor = RepoProcessor()
            processor.set_context(st.session_state.code_map)
            
            with st.spinner("Senior Dev is reasoning..."):
                response = processor.get_query_response(prompt)
                
                # Check for mermaid block
                if "```mermaid" in response:
                    parts = response.split("```mermaid")
                    st.markdown(parts[0])
                    mermaid_code = parts[1].split("```")[0].strip()
                    stmd.st_mermaid(mermaid_code) # Render the visual!
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please enter a GitHub URL in the sidebar to begin.")