# chat_backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from helper_functions.utility import text_import
from logics.email_query_handler import full_workflow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later.
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    content: str

@app.post("/chat")
async def chat(request: ChatRequest):
    public_query, email_elements = text_import(request.content)
    response = await full_workflow(public_query, email_elements)
    return {"response": response}
