FROM python:3.11-slim

ENV PYTHONUNBUFFERED=true

RUN apt-get update && apt-get install -y \
    nodejs npm \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd --gid 1001 app && useradd --uid 1001 --gid 1001 -ms /bin/bash app

WORKDIR /home/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install Node.js dependencies
COPY package*.json ./
RUN npm install

# Copy code
COPY --chown=app:app . ./
COPY .streamlit /app/.streamlit
COPY supervisord.conf /etc/supervisord.conf
USER 1001

EXPOSE 3000 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
