import sys
import json
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import extract_msg
import re

# Load multilingual BERT sentiment model (1 to 5 stars)
MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

stop_words = set(ENGLISH_STOP_WORDS)

def clean_text(text, stop_words):
    text = text.lower()
    text = re.sub(r"\d+", "", text)  # remove digits
    return ' '.join([word for word in text.split() if word not in stop_words])

def get_sentiment_score(text):
    try:
        cleaned_text = clean_text(text, stop_words)
        inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        outputs = model(**inputs)
        probs = outputs.logits.softmax(dim=1).detach().numpy()[0]

        stars = np.argmax(probs) + 1  # 1 to 5 stars
        normalized_score = round(((stars - 3) / 2), 3)  # scale -1 to 1
        return cleaned_text, normalized_score, f"{stars}-star"

    except Exception as e:
        print("🔥 Error in get_sentiment_score:", str(e))
        return text, 0.0, "error"

# =============================
# Main Execution Block
# =============================
if __name__ == "__main__":
    file_path = sys.argv[1]
    email_text = None
    msg_sender = ""
    msg_subject = ""
    msg_body = ""

    try:
        try:
            msg = extract_msg.Message(file_path)
            msg_sender = msg.sender or ""
            msg_subject = msg.subject or ""
            msg_body = msg.body or ""
            email_text = msg_body
        except:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    email_text = f.read()
                    msg_body = email_text
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    email_text = f.read()
                    msg_body = email_text
    except Exception as e:
        print(json.dumps({"error": f"Failed to extract email: {str(e)}"}))
        sys.exit(1)

    if not email_text:
        print(json.dumps({"error": "No email content extracted."}))
        sys.exit(1)

    try:
        processed_text, sentiment_score, sentiment_label = get_sentiment_score(email_text)
    except Exception as e:
        print(json.dumps({"error": f"Sentiment scoring failed: {str(e)}"}))
        sys.exit(1)

    result = {
        "emailText": email_text,
        "emailSender": msg_sender,
        "emailSubject": msg_subject,
        "emailBody": msg_body,
        "summary": f"The email you uploaded has a sentiment score of {sentiment_score}.",
        "score": sentiment_score,
        "label": sentiment_label,
        "showDetails": True
    }

    print(json.dumps(result))