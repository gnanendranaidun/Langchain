import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def load_retrieval_chain(persist_directory: str = "embeddings_db"):
    """Load the vector store and create a retrieval chain."""
    try:
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536
        )
        
        # Load the persisted vector store
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        # Create a retriever
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Return top 3 most relevant chunks
        )
        
        # Initialize the language model
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0
        )
        
        # Create a conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create the conversational chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True
        )
        
        return chain
    
    except Exception as e:
        logger.error(f"Error loading retrieval chain: {str(e)}")
        raise

def chat(question):
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Please set OPENAI_API_KEY in your environment variables or .env file")
    
    # Load the retrieval chain
    chain = load_retrieval_chain()
    
    # print("\nWelcome to the Bank Documents QA System!")
    # print("Type 'exit' to end the conversation.\n")
    
    # Get user question

    # Get response from the chain
    
    result = chain.invoke({"question": question, "chat_history": []})

    # Ensure correct unpacking of results
    if isinstance(result, dict) and "answer" in result and "source_documents" in result:
        answer = result["answer"]
        source_docs = result["source_documents"]
    else:
        logger.error(f"Unexpected output format: {result}")
        answer = "Sorry, an error occurred."
        source_docs = []

    # Print the answer
    # print("\nAnswer:", answer)

    # Print source documents if available
    if source_docs:
        print("\nSources:")
        for i, doc in enumerate(source_docs, 1):
            source = doc.metadata.get('source', 'Unknown source')
            content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            # print(f"\n{i}. From {source}:")
            # print(f"   {content}")

        # Update chat history

        return answer
        
if __name__ == "__main__":
    st = input("Enter your question: ")
    result = chat(st)
    print(result)