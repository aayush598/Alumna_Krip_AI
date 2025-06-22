# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (Gradio UI will use this)
EXPOSE 8000

# Run both FastAPI (background) and Gradio on same port (8000)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 9000 & python app.py"]
