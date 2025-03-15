import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your environment variables or .env file")

def load_documents(directory_path: str) -> list[Document]:
    """Load documents from the specified directory."""
    loader = DirectoryLoader(
        directory_path,
        glob="**/*",
        show_progress=True,
        loader_cls=UnstructuredFileLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {directory_path}")
    return documents

def split_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(documents)
    print(f"Split documents into {len(splits)} chunks")
    return splits

def create_embeddings_and_store(documents: list[Document], persist_directory: str):
    """Create embeddings using OpenAI's text-embedding-3-small and store in Chroma."""
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1536,  # Dimensionality of text-embedding-3-small
    )
    
    # Create and persist the vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    print(f"Created and stored embeddings in {persist_directory}")
    return vectorstore

def main():
    # Directory containing the bank documents
    base_dir = "All Banks Files"
    persist_dir = "embeddings_db"
    
    # Load all documents
    all_documents = []
    for bank_dir in os.listdir(base_dir):
        if bank_dir.startswith('.'):  # Skip hidden files
            continue
        full_path = os.path.join(base_dir, bank_dir)
        if os.path.isdir(full_path):
            try:
                documents = load_documents(full_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error processing {bank_dir}: {str(e)}")
    
    if not all_documents:
        print("No documents were loaded. Please check the directory structure and file formats.")
        return
    
    # Split documents into chunks
    splits = split_documents(all_documents)
    
    # Create embeddings and store in the vector database
    vectorstore = create_embeddings_and_store(splits, persist_dir)
    print("Successfully processed all documents and created embeddings!")

if __name__ == "__main__":
    main() 