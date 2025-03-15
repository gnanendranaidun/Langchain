import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
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

app = FastAPI()

# Initialize the retrieval chain
def load_retrieval_chain(persist_directory: str = "embeddings_db"):
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536
        )
        
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Return top 3 most relevant chunks
        )
        
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
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

# Load the retrieval chain once
chain = load_retrieval_chain()

# Store chat history in memory for simplicity
# In a real application, consider using a database
chat_history = []

@app.get("/welcome")
async def welcome():
    return {"message": "Welcome to the Bank Documents QA System!"}

@app.post("/ask")
async def ask(question: str):
    global chat_history
    
    if not question:
        return {"error": "Please provide a question."}
    
    # Get response from the chain
    result = chain.invoke({"question": question, "chat_history": chat_history})

    if isinstance(result, dict) and "answer" in result and "source_documents" in result:
        answer = result["answer"]
        source_docs = result["source_documents"]
    else:
        logger.error(f"Unexpected output format: {result}")
        answer = "Sorry, an error occurred."
        source_docs = []

    # Update chat history
    chat_history.append((question, answer))

    # Return the answer and source documents if available
    response = {"answer": answer}
    if source_docs:
        response["sources"] = []
        for i, doc in enumerate(source_docs, 1):
            source = doc.metadata.get('source', 'Unknown source')
            content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            response["sources"].append({
                "source": source,
                "content": content
            })

    return response["answer"]

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your environment variables or .env file")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
