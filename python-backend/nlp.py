import sys
import json
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import pipeline
import extract_msg  # For .msg file parsing


from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import pipeline
import re

stop_words = set(ENGLISH_STOP_WORDS)
sentiment_pipeline = pipeline("sentiment-analysis")

def clean_text(text, stop_words):
    text = text.lower()
    text = re.sub(r"\d+", "", text)  # remove digits
    return ' '.join([word for word in text.split() if word not in stop_words])

def get_sentiment_score(text):
    cleaned = clean_text(text, stop_words)
    result = sentiment_pipeline(cleaned)[0]
    score = round(result['score'], 3)
    sentiment_score = score if result['label'] == "POSITIVE" else -score
    return cleaned, sentiment_score

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
        processed_text, sentiment_score = get_sentiment_score(email_text)
    except Exception as e:
        print(json.dumps({"error": f"Sentiment scoring failed: {str(e)}"}))
        sys.exit(1)

    result = {
        "emailText": email_text,
        "emailSender": msg_sender,
        "emailSubject": msg_subject,
        "emailBody": msg_body,
        "summary": f"The email you uploaded has a sentiment score of {sentiment_score}.",
        "score": str(sentiment_score),
        "showDetails": True
    }
    print("DEBUG:", result)
    print("FINAL JSON OUTPUT:", json.dumps(result))
    print(json.dumps(result))
