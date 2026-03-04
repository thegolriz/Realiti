#build backend
FROM python:3.11-slim  
RUN apt-get update && apt-get install -y \
     gcc \
     libpq-dev \
     && rm -rf /var/lib/apt/lists/*
RUN pip3 install poetry
WORKDIR /app
# Copy only the dependency files first for better caching
COPY pyproject.toml poetry.lock* ./
    
# Install dependencies (no root to avoid unnecessary install)
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "python"]

