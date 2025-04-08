FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Create the directory and copy the lexicon file
RUN mkdir -p /usr/share/nltk_data/sentiment
COPY vader_lexicon.txt /usr/share/nltk_data/sentiment/vader_lexicon.txt


# Copy the rest of your code
COPY . .

# Launch FastAPI
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]
