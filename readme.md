---

# **Research Agent – Full Stack AI Application**

A full-stack AI-powered Research Agent designed to deliver intelligent, context-aware responses using Retrieval-Augmented Generation (RAG).

The system combines modern backend architecture, scalable data storage, and an interactive frontend to provide a ChatGPT-like experience with private user sessions, document-based querying, and real-time knowledge retrieval.

---

## **Tech Stack**

### **Backend**

* FastAPI
* Python
* MongoDB Atlas
* FAISS (Vector Store)
* Google Generative AI (Gemini)
* Tavily API (Web Search)
* Wikipedia API (Knowledge Source)
* JWT Authentication

### **Frontend**

* React
* Vite

---

## **Core Features**

* Multi-user authentication with JWT-based security
* Private chat sessions per user
* Guest mode for temporary usage
* Retrieval-Augmented Generation (RAG) pipeline
* PDF-based document chat
* Web search integration (Tavily API)
* Wikipedia-based knowledge retrieval
* Vector similarity search using FAISS
* Dynamic chat title generation
* Session-based memory management
* Clean and responsive chat interface

---

## **Project Overview**

This application allows users to interact with an AI-powered research assistant capable of answering queries using:

* Stored vector knowledge
* Uploaded documents
* Real-time web data
* Structured conversation history

The backend handles AI processing, authentication, and data management, while the frontend provides a seamless user experience for chat interactions.

---

## **Project Structure**

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

## **Prerequisites**

Ensure the following are installed:

* Python (3.10 or higher)
* Node.js (v18 or higher)
* npm
* MongoDB Atlas account
* Google API Key
* Tavily API Key

---

## **Backend Setup (FastAPI)**

### 1. Navigate to Backend

```
cd backend
```

### 2. Create Virtual Environment

```
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**

```
venv\Scripts\activate
```

**macOS/Linux:**

```
source venv/bin/activate
```

### 4. Install Dependencies

```
pip install -r requirements.txt
```

### 5. Environment Configuration

Create a `.env` file inside the backend directory and copy values from `.env.example`.

Example configuration:

```
MONGO_URI="your_mongodb_connection_string"
DB_NAME=research_agent
GOOGLE_API_KEY="your_google_api_key"
FAISS_PATH=faiss_index
TAVILY_API_KEY="your_tavily_api_key"
JWT_SECRET_KEY="your_secret_key"
JWT_ALGORITHM="HS256"
```

---

## **MongoDB Atlas Configuration**

* Create a cluster in MongoDB Atlas
* Add your IP address in Network Access
* Create database user credentials
* Obtain the connection string and update `MONGO_URI`

---

## **Running the Backend**

```
cd backend
venv\Scripts\activate   # Windows
# or
source venv/bin/activate

uvicorn app.main:app --reload
```

Backend will be available at:

```
http://127.0.0.1:8000
```

---

## **Frontend Setup (React + Vite)**

### 1. Navigate to Frontend

```
cd chat-frontend
```

### 2. Install Dependencies

```
npm install
```

### 3. Run Development Server

```
npm run dev
```

Frontend will be available at:

```
http://localhost:5173
```

---

## **Running the Application**

1. Start the backend server
2. Start the frontend server
3. Open the application in your browser

```
http://localhost:5173
```

---

## **System Architecture**

The system follows a modular architecture:

1. User sends a query through the frontend
2. Backend authenticates and validates the user
3. Query is processed through the RAG pipeline
4. Data is retrieved from:

   * FAISS vector store
   * PDF embeddings
   * Web search (Tavily)
   * Wikipedia API
5. Context is passed to the language model
6. Response is generated and stored per session
7. Result is returned to the frontend

---

## **Future Improvements**

* Streaming responses
* Redis caching layer
* Rate limiting
* Chat sharing capabilities
* Deployment with Docker and CI/CD
---
## **License**
This project is for educational and development purposes.
---
