# 🎓 Alumna Krip AI - College Counselor API

An intelligent FastAPI-based system that guides students in choosing engineering colleges based on academic performance, budget, preferences, and other profile attributes. The system supports chat-based interaction, profile management, and college recommendations.

---

## 🚀 Features

- Conversational API for student counseling
- Dynamic profile building
- College recommendation engine
- SQLite-powered backend
- Full session tracking and analytics
- Docker & Render deployment ready

---

## 📦 Technologies Used

- FastAPI
- Python 3.12
- SQLite3
- Uvicorn
- Docker

---

## 🛠️ Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/aayush598/Alumna_Krip_AI.git
cd Alumna_Krip_AI
````

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the API locally

```bash
python main.py
```

> Access the API at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🚀 Deploying to Render (Docker)

### 1. Push your code to GitHub

### 2. Create a new Web Service on [Render](https://dashboard.render.com/)

* Environment: **Docker**
* Dockerfile path: `Dockerfile`
* Exposed port: `8000`

### 3. Done!

Your app will be live at:
`https://<your-app-name>.onrender.com`

---

## 🔌 API Endpoints

### 📍 `GET /`

> Returns welcome message and API metadata.

**Response:**

```json
{
  "message": "Welcome to Alumna Krip AI - College Counselor API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "chat": "/chat",
    "recommendations": "/recommendations",
    "profile": "/profile/{session_id}",
    "sessions": "/sessions",
    "colleges": "/colleges"
  },
  "documentation": "/docs"
}
```

---

### 🧠 `POST /chat`

Start or continue a counseling session.

**Request:**

```json
{
  "message": "Hi, I scored 92% and want to pursue engineering.",
  "session_id": "optional"
}
```

**Response:**

```json
{
  "response": "That's great! What's your budget range for college fees?",
  "session_id": "session_20250623_123456_0",
  "profile": {
    "grade_12_percentage": 92
  },
  "sufficient_info": false,
  "recommendations": null
}
```

---

### 🎓 `POST /recommendations`

Get college recommendations.

**Request:**

```json
{
  "session_id": "session_20250623_123456_0"
}
```

OR

```json
{
  "profile_data": {
    "grade_12_percentage": 92,
    "jee_score": 5000,
    "budget_max": 800000,
    "preferred_location": "South India",
    "preferred_stream": "Engineering",
    "specialization_interest": "Computer Science"
  },
  "max_results": 5
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "name": "IIT Madras",
      "location": "Chennai, Tamil Nadu",
      "fees": 200000,
      "match_score": 95.0,
      "match_reasons": ["Top CS program", "Great placements"]
    }
  ],
  "total_found": 3,
  "returned": 1,
  "profile_used": { ... }
}
```

---

### 🧑‍🎓 `GET /profile/{session_id}`

Get student profile data.

**Response:**

```json
{
  "session_id": "session_20250623_123456_0",
  "profile": {
    "grade_12_percentage": 92,
    "preferred_stream": "Engineering"
  },
  "sufficient_info": false,
  "extraction_history": [ ... ]
}
```

---

### 🔧 `PUT /profile/{session_id}`

Update profile manually.

**Request:**

```json
{
  "session_id": "session_20250623_123456_0",
  "profile_data": {
    "category": "General",
    "state_of_residence": "Karnataka"
  }
}
```

---

### 🧾 `GET /sessions`

List all sessions.

**Response:**

```json
[
  {
    "session_id": "session_20250623_123456_0",
    "created_at": "2025-06-23T14:22:11",
    "status": "active",
    "message_count": 4
  }
]
```

---

### 🗑️ `DELETE /sessions/{session_id}`

Soft delete a session.

**Response:**

```json
{
  "message": "Session session_20250623_123456_0 deleted successfully"
}
```

---

### 🏛️ `GET /colleges`

Get college database with optional filters.

**Example Query:**

```
GET /colleges?stream=Computer Science&location=South India&max_fees=800000
```

---

### 📊 `GET /analytics`

Basic usage stats.

**Response:**

```json
{
  "total_sessions": 12,
  "active_sessions": 3,
  "total_messages": 55,
  "completed_sessions": 6,
  "completion_rate": "50.0%",
  "endpoint_usage": [
    { "endpoint": "/chat", "calls": 30 },
    { "endpoint": "/recommendations", "calls": 10 }
  ]
}
```

---

## 🧪 Testing with test_project.py

You can use the script `test_project.py` to simulate and validate API behavior.

```bash
python test_project.py
```

This will:

* Run a full counseling conversation
* Validate responses
* Test all endpoints
* Print recommendation and session summaries

---

## 📁 Project Structure

```
.
├── main.py
├── test_project.py
├── counselor.py
├── student_profile.py
├── college_database.py
├── requirements.txt
├── Dockerfile
├── README.md
└── counselor_api.db
```

---

## 📬 Contact

**Author:** Aayush Gid
**Email:** [aayushgid598@gmail.com](mailto:aayushgid598@gmail.com)
**GitHub:** [https://github.com/aayush598](https://github.com/aayush598)

---

## 📜 License

This project is licensed under the MIT License. Feel free to use and modify it.
