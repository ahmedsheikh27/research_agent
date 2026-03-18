import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import { chatService } from "../services/api";
import Header from "../components/Header";

export default function AppLayout() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);

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

      setMessages((prev) => (history.length > 0 ? history : prev));

    } catch (error) {
      console.error("Error fetching history:", error);
      navigate("/app");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadChats();
  }, [loadChats, sessionId]);

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

  // App.jsx
  const handleSendMessage = async (query) => {
    if (!query.trim()) return;

    // 1. Update UI locally
    setMessages(prev => [...prev, { role: "user", content: query }]);

    try {
      // 2. The call to the backend
      const response = await chatService.sendMessage(sessionId, query);

      // 3. REFRESH SIDEBAR NOW (Don't wait for assistant response)
      // This makes the title update in the sidebar while the AI is still "typing"
      await loadChats();

      // 4. Update UI with assistant response
      setMessages(prev => [...prev, { role: "assistant", content: response.response }]);

    } catch (error) {
      console.error("Error:", error);
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
  const handleUploadPDF = async (file) => {
    if (!file) return;

    // Basic validation
    if (file.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      return;
    }

    setIsUploading(true);
    try {
      const data = await chatService.uploadPDF(file);

      const welcomeMessage = {
        role: "assistant",
        content: `The PDF: ${file.name} uploaded successfully. Ask anything about pdf.`,
        isInitial: true
      };

      setMessages([welcomeMessage]);

      await loadChats();

      navigate(`/app/chat/${data.session_id}`);

    } catch (error) {
      console.error("PDF Upload Error:", error);
      alert("Failed to upload PDF. Ensure your backend is running.");
    } finally {
      setIsUploading(false);
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
        onUploadPDF={handleUploadPDF}
        isUploading={isUploading}
      />

      <div className="flex-1 flex flex-col min-w-0">

        <Header />

        <main className="flex-1 overflow-hidden relative">
          {sessionId ? (
            // SHOW CHAT WINDOW IF SESSION EXISTS
            <ChatWindow messages={messages} onSendMessage={handleSendMessage} />
          ) : (
            // SHOW DASHBOARD IF NO SESSION (Empty State)
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
              <h2 className="text-2xl font-bold mb-6">Start a new research session</h2>
              <div className="flex gap-4">
                <button
                  onClick={handleNewChat}
                  className="px-6 py-3 bg-primary-500 rounded-xl font-medium"
                >
                  New Chat
                </button>
                <button
                  onClick={() => document.querySelector('input[type="file"]').click()}
                  className="px-6 py-3 bg-dark-700 border border-dark-600 rounded-xl font-medium"
                >
                  Upload PDF
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}