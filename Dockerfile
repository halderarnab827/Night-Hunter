# Build the React dashboard first.
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Run the Flask API and serve the built dashboard from one public service.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY . ./
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["sh", "-c", "waitress-serve --listen=0.0.0.0:${PORT:-8000} api.server:app"]
