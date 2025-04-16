# backend for running the FastAPI server for the chatbot
from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from helper_functions.utility import text_import
from logics.email_query_handler import full_workflow
from nlp import get_sentiment_score
import os
import uvicorn

app = FastAPI()

# CORS is optional now since only Node accesses this internally
# You can keep this with allow_origins=["*"] or remove it entirely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    content: str

class TextRequest(BaseModel):
    text: str

# Route to handle chatbot queries
@app.post("/chat")
async def chat(request: ChatRequest):
    public_query, email_elements = text_import(request.content)
    response = await full_workflow(public_query, email_elements)
    return {"response": response}

# Route to analyse email or raw text
@app.post("/analyze")
async def analyze(req: Request):
    try:
        data = await req.json()
        text = data.get("text")

        if not text:
            return JSONResponse(status_code=400, content={"error": "Missing 'text' field"})

        print(">>> Received text length:", len(text))

        cleaned, score, label = get_sentiment_score(text)

        result = {
            "emailText": text,
            "emailSender": "",
            "emailSubject": "",
            "emailBody": text,
            "summary": f"The email you uploaded has a sentiment score of {score}.",
            "score": score,
            "showDetails": True
        }

        return JSONResponse(content=result)

    except Exception as e:
        print("🔥 ERROR in /analyze:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
