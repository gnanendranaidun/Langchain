import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from rag import retriever_tool
from prompts import react_prompt
from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

# Load environment variables


# Initialize ChatOpenAI with the correct model
# Note: As of March 2025, gpt-4o-mini is available (it was released after July 2024)
model_openai = ChatOpenAI(
    model="gpt-4o-mini",
)

# Initialize Tavily search tool
tavily_tool = TavilySearchResults(
    max_results=3,
    search_depth="basic",
)

# Create React agent
react_agent = create_react_agent(model=model_openai, tools=[tavily_tool, retriever_tool], prompt=react_prompt)

# Initialize FastAPI app
app = FastAPI()

# Create a Pydantic model for the request body
class QuestionRequest(BaseModel):
    question: str

@app.get("/welcome")
async def welcome():
    return {"message": "Welcome to the Bank Documents QA System!"}

@app.post("/ask")
async def ask(request: QuestionRequest):

    messages=[]
    with open("conv_history.json", "r", encoding="utf-8") as file:
        data = json.load(file) 
    for entry in data:
        messages.append(HumanMessage(content=entry["Human"]))
        messages.append(AIMessage(content=entry["AI"]))
    res = react_agent.invoke(messages)
     # Store the conversation in memory
    conversation_entry = {"Human": request.question, "AI": res["message"][-1].content}

    # Write updated history to JSON file
    with open("conv_history.json", "w", encoding="utf-8") as f:
        json.dump(conversation_entry, f, indent=4)

    return res["messages"][-1].content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
