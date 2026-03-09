import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import { chatService } from "../services/api";
import Header from "../components/Header";

export default function AppLayout() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadChats = useCallback(async () => {
    try {
      const data = await chatService.getAllChats();
      const chatList = Array.isArray(data) ? data : data.chats || [];
      setChats(chatList);
      return chatList;
    } catch (error) {
      console.error("Error fetching chat list:", error);
    }
  }, []);

  const loadHistory = async (id) => {
    setIsLoading(true);
    try {
      const data = await chatService.getChatHistory(id);
      const history = Array.isArray(data) ? data : data.history || data.messages || [];
      setMessages(history);
    } catch (error) {
      console.error("Error fetching history:", error);
      navigate("/app");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const list = await loadChats();
      if (!sessionId && list && list.length > 0) {
        navigate(`/app/chat/${session_id}`, { replace: true });
      }
    };
    init();
  }, [loadChats, navigate, sessionId]);

  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId);
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  const handleNewChat = async () => {
    try {
      const { session_id } = await chatService.createSession();
      navigate(`/app/chat/${session_id}`);
      await loadChats();
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  const handleSendMessage = async (query) => {
    if (!sessionId) return;

    setIsLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      const data = await chatService.sendMessage(sessionId, query);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      loadChats();
    } catch (error) {
      console.error("Message error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = async (id) => {
    try {
      await chatService.deleteChat(id);
      if (sessionId === id) navigate("/app");
      loadChats();
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  return (
    <div className="flex h-screen bg-dark-900 text-slate-100 overflow-hidden">
      <Sidebar
        chats={chats}
        activeSessionId={sessionId}
        onSelectChat={(id) => navigate(`/app/chat/${id}`)}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      <div className="flex-1 flex flex-col min-w-0">
        
        <Header/>

        <main className="flex-1 overflow-hidden relative">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </main>
      </div>
    </div>
  );
}