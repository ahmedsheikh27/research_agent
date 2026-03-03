import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  // GET /chat -> returns list of all chats
  getAllChats: async () => {
    const response = await api.get('/chat');
    return response.data; // FastAPI usually returns an array directly or { "chats": [] }
  },

  // POST /chat/new -> returns { session_id }
  createSession: async () => {
    const response = await api.post('/chat/new');
    return response.data;
  },

  // GET /chat/{session_id} -> returns history
  getChatHistory: async (sessionId) => {
    const response = await api.get(`/chat/${sessionId}`);
    return response.data;
  },

  // POST /chat -> body: { session_id, query }
  sendMessage: async (sessionId, query) => {
    const response = await api.post('/chat', { 
      session_id: sessionId, 
      query: query 
    });
    return response.data;
  },

  // DELETE /chat/{session_id}
  deleteChat: async (sessionId) => {
    const response = await api.delete(`/chat/${sessionId}`);
    return response.data;
  }
};