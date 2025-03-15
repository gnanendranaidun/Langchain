import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import logging
import sys
from typing import Optional
from unstructured.partition.md import partition_md

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CustomUnstructuredFileLoader(UnstructuredFileLoader):
    """Custom loader with better error handling."""
    def _get_elements(self) -> list:
        try:
            if self.file_path.lower().endswith('.md'):
                return partition_md(filename=self.file_path)
            return super()._get_elements()
        except Exception as e:
            logger.warning(f"Error processing file {self.file_path}: {str(e)}")
            return []

def load_documents_from_directory(directory_path: str) -> list[Document]:
    """Load documents from a directory."""
    try:
        loader = DirectoryLoader(
            directory_path,
            glob="**/*",  # Load all files recursively
            show_progress=True,
            loader_cls=CustomUnstructuredFileLoader,
            use_multithreading=True
        )
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading documents from {directory_path}: {str(e)}")
        return []

def split_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
    """Split documents into smaller chunks."""
    if not documents:
        logger.warning("No documents to split")
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(documents)
    logger.info(f"Split documents into {len(splits)} chunks")
    return splits

def create_embeddings_and_store(documents: list[Document], persist_directory: str) -> Optional[Chroma]:
    """Create embeddings using OpenAI's text-embedding-3-small and store in Chroma."""
    if not documents:
        logger.error("No documents to create embeddings for")
        return None
        
    try:
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
        logger.info(f"Created and stored embeddings in {persist_directory}")
        return vectorstore
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        return None

def main():
    try:
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Please set OPENAI_API_KEY in your environment variables or .env file")

        # Directory containing the bank documents
        base_dir = "All Banks Files"
        persist_dir = "embeddings_db"
        
        if not os.path.exists(base_dir):
            raise ValueError(f"Directory '{base_dir}' does not exist")
        
        # Load all documents
        all_documents = []
        for bank_dir in os.listdir(base_dir):
            if bank_dir.startswith('.'):  # Skip hidden files
                continue
            full_path = os.path.join(base_dir, bank_dir)
            if os.path.isdir(full_path):
                documents = load_documents_from_directory(full_path)
                all_documents.extend(documents)
        
        if not all_documents:
            logger.error("No documents were loaded. Please check the directory structure and file formats.")
            sys.exit(1)
        
        # Split documents into chunks
        splits = split_documents(all_documents)
        
        if not splits:
            logger.error("Failed to split documents into chunks.")
            sys.exit(1)
        
        # Create embeddings and store in the vector database
        vectorstore = create_embeddings_and_store(splits, persist_dir)
        
        if not vectorstore:
            logger.error("Failed to create and store embeddings.")
            sys.exit(1)
            
        logger.info("Successfully processed all documents and created embeddings!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 