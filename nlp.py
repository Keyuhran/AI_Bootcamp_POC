# Import necessary libraries
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import json


# Download required NLTK resources (first time only)
# nltk.download('vader_lexicon')
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('wordnet')

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
    #print(f"[Keyword Log] Extracted Tokens: {lemmatized_tokens}")
    return ' '.join(lemmatized_tokens)
# Sentiment scoring function (0 to 1)
def get_sentiment_score(text):
    processed_text = preprocess_text(text)
    score = analyzer.polarity_scores(processed_text)['pos']  # use 'pos' score for positivity
    return processed_text, round(score, 2)

# Example usage
# input_text = "PUB officers are so friendly! Love the work you do at PUB!"
# processed_text, sentiment_score = get_sentiment_score(input_text)

# print(f"Input: {input_text}")
# print(f"Processed: {processed_text}")
# print(f"Sentiment Score (0 to 1): {sentiment_score}")

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            text = f.read()

    processed_text, sentiment_score = get_sentiment_score(text)

    result = {
        "summary": f"The email you uploaded has a sentiment score of {sentiment_score}/0.30.",
        "showDetails": True  # this tells the frontend to show the "View Details" button
    }

    print(json.dumps(result))