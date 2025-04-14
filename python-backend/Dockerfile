# This Dockerfile is for a FastAPI application that uses Python 3.11 and installs dependencies from a requirements.txt file. For python-backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt



# Copy the rest of the application code
COPY . .

# Launch FastAPI
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]


