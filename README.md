
# 🎓 Alumna Krip AI - College Counseling Chatbot

**Alumna Krip AI** is an intelligent, dynamic college counseling assistant built using **FastAPI** and **Gradio**. It guides students through a conversation to collect academic information, assess college readiness, and generate a downloadable student profile. The system logs every interaction in a local SQLite database for transparency and monitoring.

> 🔗 Live Demo: [https://alumna-krip-ai.onrender.com](https://alumna-krip-ai.onrender.com)  
> 📦 GitHub Repo: [github.com/aayush598/Alumna_Krip_AI](https://github.com/aayush598/Alumna_Krip_AI)

---

## 📌 Features

- 💬 Conversational AI for student counseling.
- 🧠 Smart profile builder based on user inputs.
- ✅ Readiness status tracking (`sufficient_info` flag).
- 🧾 Downloadable student profile in JSON format.
- 🔁 Resettable sessions via API.
- 📊 Logs all chat and API interactions in `logs.db`.
- 🐳 Dockerized deployment support.
- 🌐 Integrated Gradio UI + FastAPI backend on the same port.

---

## 📁 File Structure

```

Alumna_Krip_AI/
│
├── app.py                  # Gradio frontend app
├── main.py                 # FastAPI backend with endpoints
├── counselor.py            # Core logic for chatbot
├── student\_profile.py      # Student profile model
├── interface.py            # Gradio interface builder
├── college\_database.py     # (Optional) Mock college data interface
├── utils.py                # Helper utilities
├── logs.db                 # SQLite database (auto-generated)
├── .env                    # Environment config (optional)
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md               # You're here!

````

---

## 🚀 Quick Start

### 🔧 1. Clone & Setup

```bash
git clone https://github.com/aayush598/Alumna_Krip_AI.git
cd Alumna_Krip_AI
pip install -r requirements.txt
````

### ▶️ 2. Run the App

Make sure `main.py` and `app.py` are in the same folder.

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 & python app.py
```

Or use the combined CMD inside Docker (recommended).

---

## 🐳 Docker Deployment

### 🔹 Dockerfile

```dockerfile
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
```

### 🔹 Build & Run

```bash
docker build -t alumna-ai .
docker run -p 8000:8000 alumna-ai
```

Access the app at: [http://localhost:8000](http://localhost:8000)

---

## 🔗 API Endpoints

| Method | Endpoint            | Description                                                            |
| ------ | ------------------- | ---------------------------------------------------------------------- |
| POST   | `/chat`             | Accepts message + history, returns response, profile, readiness status |
| GET    | `/download-profile` | Returns generated `student_profile.json`                               |
| POST   | `/reset`            | Resets the chatbot session                                             |
| GET    | `/logs`             | Retrieves the latest 100 logs from `logs.db`                           |

---

## 🧠 Core Logic

* **`DynamicCollegeCounselorChatbot`** (in `counselor.py`): Manages conversation, updates profile, tracks info completeness.
* **`StudentProfile`** (in `student_profile.py`): Pydantic model to store academic and interest data.
* **`logs.db`**: Auto-generated SQLite file storing API logs for `/chat`, `/reset`, `/profile`, etc.

---

## 💬 Gradio Chat UI

The Gradio interface is created in `interface.py` and launched via `app.py`:

```python
from interface import create_chatbot_interface

if __name__ == "__main__":
    app = create_chatbot_interface()
    app.launch(server_name="0.0.0.0", server_port=8000)
```

---

## 🌐 Live Hosted Version

The app is deployed on Render and available at:

🔗 **[https://alumna-krip-ai.onrender.com](https://alumna-krip-ai.onrender.com)**

---

## 📄 Example `.env` (Optional)

```env
GROQ_API_KEY=<GROQ_API_KEY>
```

---

## 🛡️ Security Notes

* CORS is enabled for development (`allow_origins=["*"]`). Restrict this in production.
* No personal data is stored unless explicitly logged.
* SQLite used for logs; switch to PostgreSQL or MongoDB for scaling.

---

## 🙌 Author

**Aayush Gid**
📧 [aayushgid598@gmail.com](mailto:aayushgid598@gmail.com)
🌐 [github.com/aayush598](https://github.com/aayush598)

---

## 📜 License

This project is licensed under the **MIT License**.

---
