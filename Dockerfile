# Build stage for frontend
FROM node:lts-alpine as build-stage

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install

COPY ./frontend .

RUN npm run build

# Build stage for backend
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /backend

COPY ./backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend files from the first stage
COPY --from=build-stage /app/dist ../frontend/dist

COPY ./backend .

COPY settings.toml .

RUN mkdir data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]