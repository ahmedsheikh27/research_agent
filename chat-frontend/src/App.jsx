// src/App.jsx
import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import useAutoScroll from "./hooks/useAutoScroll";
import * as api from "./api/chatApi";

export default function App() {
  const [chats, setChats] = useState([]);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef();

  useAutoScroll(endRef, messages);

  useEffect(() => {
    api.getChats().then(d => {
      setChats(d.chats || []);
      if (d.chats?.length) loadChat(d.chats[0].session_id);
    });
  }, []);

  const loadChat = async (id) => {
    setSession(id);
    const d = await api.getChat(id);
    setMessages(d.messages || []);
  };

  const createChat = async () => {
    const d = await api.newChat();
    setSession(d.session_id);
    setMessages([]);
    const list = await api.getChats();
    setChats(list.chats);
  };

  const send = async () => {
    if (!input.trim()) return;
    const msg = { role: "user", content: input };
    setMessages(m => [...m, msg]);
    setInput("");
    setLoading(true);

    const d = await api.sendMessage({ session_id: session, query: msg.content });
    setMessages(m => [...m, { role: "assistant", content: d.response }]);
    setLoading(false);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar chats={chats} active={session} onNew={createChat} onSelect={loadChat} />
      <div className="flex-1 flex flex-col">
        <ChatWindow messages={messages} loading={loading} endRef={endRef} />
        <ChatInput value={input} onChange={setInput} onSend={send} loading={loading} />
      </div>
    </div>
  );
}
