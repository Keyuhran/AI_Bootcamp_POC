# chat_backend.py
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from helper_functions.utility import text_import
from logics.email_query_handler import full_workflow
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from nlp import get_sentiment_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    content: str

class TextRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat(request: ChatRequest):
    public_query, email_elements = text_import(request.content)
    response = await full_workflow(public_query, email_elements)
    return {"response": response}


@app.post("/analyze")
def analyze(text: str = Form(...)):
    return get_sentiment_score(text)


@app.post("/analyze-text")
def analyze_text(payload: TextRequest):
    return {
        "emailText": payload.text,
        "emailSender": "noreply@example.com",
        "emailSubject": "Mock subject",
        "emailBody": payload.text,
        "score": 0
    }