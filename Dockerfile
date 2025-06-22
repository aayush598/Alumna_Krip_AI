# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose only the Gradio UI port (7860) - since it is the user-facing part
EXPOSE 7860

# Run FastAPI backend in background, and Gradio app in foreground
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python app.py"]
