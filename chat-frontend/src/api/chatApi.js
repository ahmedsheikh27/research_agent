// src/api/chatApi.js
const BASE = "http://127.0.0.1:8000";

export const getChats = () => fetch(`${BASE}/chat`).then(r => r.json());
export const newChat = () => fetch(`${BASE}/chat/new`, { method: "POST" }).then(r => r.json());
export const getChat = (id) => fetch(`${BASE}/chat/${id}`).then(r => r.json());
export const sendMessage = (body) =>
  fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  }).then(r => r.json());
