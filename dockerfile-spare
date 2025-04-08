FROM python:3.11-slim

ENV PYTHONUNBUFFERED=true

# Install Node 20 from NodeSource and other tools
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd --gid 1001 app && useradd --uid 1001 --gid 1001 -ms /bin/bash app

WORKDIR /home/app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Install Node.js deps
COPY package*.json ./
RUN npm install

# Copy the rest of the code
COPY --chown=app:app . ./
COPY .streamlit /app/.streamlit
COPY supervisord.conf /etc/supervisord.conf
COPY .env .env
USER 1001

EXPOSE 3000 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
