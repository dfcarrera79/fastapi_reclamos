# The base image to start from
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the working image
WORKDIR /app

# Copy files from the host to the working image
COPY pyproject.toml poetry.lock .env .gitignore ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

# Copy the application code
COPY src ./src

# Expose the FastAPI port
EXPOSE 8000

# Set the default command for the container
CMD ["poetry", "run", "python", "src/main.py"]

