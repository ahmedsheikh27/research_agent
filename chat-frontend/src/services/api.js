import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  getAllChats: async () => {
    const response = await api.get('/chat');
    return response.data;
  },

  createSession: async () => {
    const response = await api.post('/chat/new');
    return response.data;
  },

  getChatHistory: async (sessionId) => {
    const response = await api.get(`/chat/${sessionId}`);
    return response.data;
  },

  sendMessage: async (sessionId, query) => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      query: query
    });
    return response.data;
  },

  deleteChat: async (sessionId) => {
    const response = await api.delete(`/chat/${sessionId}`);
    return response.data;
  },

  uploadPDF: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/chat/upload-pdf", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data; // { message, session_id }
  },
};