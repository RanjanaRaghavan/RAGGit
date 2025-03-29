import re
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.github import GithubRepositoryReader, GithubClient
import os
from dotenv import load_dotenv
import streamlit as st
# Load environment variables from .env file
load_dotenv()

# Retrieve GitHub token and OpenAPI key from environment variables
github_token = os.getenv('GITHUB_TOKEN')
openapi_key = os.getenv('OPENAI_API_KEY')

if not github_token:
    raise ValueError("GitHub token not found in environment variables")

if not openapi_key:
    raise ValueError("OpenAPI key not found in environment variables")


def parse_github_url(url):
    pattern = r'https://github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, url)
    if match:
        owner, repo = match.groups()
        return owner, repo
    else:
        raise ValueError("Invalid GitHub URL")


def create_index_from_github(owner, repo, branch, github_token):
    github_client = GithubClient(github_token=github_token, verbose=True)
    documents = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo,
        use_parser=False,
        verbose=False
    ).load_data(branch=branch)
    
    index = VectorStoreIndex.from_documents(documents)
    return index, len(documents)

def main():
    st.title("GitHub Repository Query App")
    url = st.text_input("Enter GitHub Repository URL", "https://github.com/RanjanaRaghavan/TicTacToe")
    branch = st.text_input("Enter Branch Name", "master")
    
    if st.button("Create Index"):
        try:
            owner, repo = parse_github_url(url)
            st.write(f"Owner: {owner}, Repo: {repo}")
            index, doclen = create_index_from_github(owner, repo, branch, github_token)
            st.success("Index created for the GitHub repository")
            
            # Store the index in session state to persist across reruns
            st.session_state.index = index
            st.session_state.doclen = doclen
        except Exception as e:
            st.error(f"Error: {e}")

    if 'index' in st.session_state:
        user_input = st.text_input("Ask a question")
        if st.button("Query"):
            query_engine = st.session_state.index.as_query_engine()
            response = query_engine.query(user_input)
            st.write("Response:", response)

if __name__ == "__main__":
    main()


# Example usage
