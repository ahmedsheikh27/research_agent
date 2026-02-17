# Research Agent – Full Stack AI Application

A full-stack AI-powered Research Agent built with:

- **FastAPI** (Backend)
-  **Next.js** (Frontend)
-  **MongoDB Atlas** (Database)
-  **FAISS** (Vector Store)
-  **Tavily API** (Web Search)
-  **Google API** (AI Integration)

---

#  Project Overview

This project allows users to interact with an AI-powered research assistant.  
The backend handles AI processing, database storage, and vector search.  
The frontend provides a clean chat interface for users.

---

# Prerequisites

Make sure you have the following installed:

- Python (3.10 or higher recommended)
- Node.js (v18+ recommended)
- npm
- MongoDB Atlas account
- Google API Key
- Tavily API Key

---

#  Project Structure

```
project-root/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│
├── chat-frontend/
│   ├── package.json
│
└── README.md
```

---

#  Backend Setup (FastAPI)

## 1️⃣ Navigate to the Backend Folder

```bash
cd backend
```

---

## 2️⃣ Create a Python Virtual Environment

```bash
python -m venv venv
```

---

## 3️⃣ Activate the Virtual Environment

### On Windows:
```bash
venv\Scripts\activate
```

### On macOS/Linux:
```bash
source venv/bin/activate
```

---

## 4️⃣ Install Backend Dependencies

After activating your virtual environment:

```bash
pip install -r requirements.txt
```
## 5️⃣ Create the `.env` File

Inside the `backend` folder, create a file named:

```
.env
```

Copy all variables from `.env.example` and paste them into your `.env` file.

Your `.env` file should look like this:

```env
MONGO_URI="mongodb+srv://uername:password@cluster0.eivnv6m.mongodb.net/?appName=Cluster0"
DB_NAME=research_agent
GOOGLE_API_KEY="your google api key"
FAISS_PATH=faiss_index
TAVILY_API_KEY="tavily api key here"
```

---

# 🔐 MongoDB Atlas Configuration

1. Go to MongoDB Atlas.
2. Create a new cluster (if you don’t already have one).
3. Click **Connect → Drivers**.
4. Copy your MongoDB connection string.
5. Replace:

```
Your MongoDB connection string here
```

with your actual connection string.

Example:

```env
MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```
Make sure:
- Your IP address is added in **Network Access**
- Database user credentials are correct

---


---

## 6️⃣ Run the Backend Server

Open a **new terminal**, then:

```bash
cd backend
venv\Scripts\activate   # Windows
```

(or `source venv/bin/activate` on macOS/Linux)

Then run:

```bash
uvicorn app.main:app --reload
```

If successful, your backend will run at:
```
http://127.0.0.1:8000
```

---

#  Frontend Setup (React.js + Vite)

## 1️⃣ Open a New Terminal

```bash
cd chat-frontend
```

---

## 2️⃣ Install Node Dependencies

```bash
npm install
```

---

## 3️⃣ Run the Frontend

```bash
npm run dev
```

Your frontend will start at:

```
http://localhost:5173
```

---

#  Running the Application

After both backend and frontend are running:

1. Open your browser (Google Chrome recommended).
2. Visit:

```
http://localhost:5173/
```

Your full-stack Research Agent application should now be running successfully 🎉

---

# Quick Command Summary

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend

```bash
cd chat-frontend
npm install
npm run dev
```