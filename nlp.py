# Import necessary libraries
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import extract_msg
import json
import os
import sys

# Initialize sentiment analyzer and lemmatizer
analyzer = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()

# Custom list of words to exclude from sentiment scoring
excluded_words = {"PUB", "pub"}

# Preprocessing function with exclusions
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [
        token for token in tokens
        if token.isalnum() and token not in stopwords.words('english') and token not in excluded_words
    ]
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    return ' '.join(lemmatized_tokens)

# Sentiment scoring function (0 to 1)
def get_sentiment_score(text):
    processed_text = preprocess_text(text)
    score = analyzer.polarity_scores(processed_text)['pos']  # use 'pos' score for positivity
    return processed_text, round(score, 2)

# =============================
# Main Execution Block
# =============================
if __name__ == "__main__":
    file_path = sys.argv[1]
    email_text = None

    try:
        # Try parsing as .msg
        try:
            msg = extract_msg.Message(file_path)
            msg_sender = msg.sender or ""
            msg_subject = msg.subject or ""
            msg_body = msg.body or ""
            email_text = f"From: {msg_sender}\nSubject: {msg_subject}\n\n{msg_body}".strip()
        except:
            # Fallback to text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    email_text = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    email_text = f.read()
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
        "emailSender": msg.sender,
        "emailSubject": msg.subject,
        "emailBody": msg.body,
        "summary": f"The email you uploaded has a sentiment score of {sentiment_score}.",
        "score": sentiment_score,
        "showDetails": True
    }

    print(json.dumps(result))
