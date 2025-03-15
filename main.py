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

from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QuestionRequest):
    question = request.question
    global chat_history
    
    if not question:
        return {"error": "Please provide a question."}
    
    result = chain.invoke({"question": question, "chat_history": chat_history})
    
    if isinstance(result, dict) and "answer" in result and "source_documents" in result:
        answer = result["answer"]
        source_docs = result["source_documents"]
    else:
        logger.error(f"Unexpected output format: {result}")
        answer = "Sorry, an error occurred."
        source_docs = []

    chat_history.append((question, answer))

    response = {"answer": answer}
    if source_docs:
        response["sources"] = [
            {"source": doc.metadata.get('source', 'Unknown source'), 
             "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content}
            for doc in source_docs
        ]

    return response["answer"]

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your environment variables or .env file")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
