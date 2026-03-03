import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import { chatService } from '../services/api';

export default function AppLayout() {
  const [chats, setChats] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadChats();
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      loadHistory(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

// Inside src/pages/App.jsx

const loadChats = async () => {
  try {
    const data = await chatService.getAllChats();
    // If your backend returns [ {session_id: '...'}, ... ]
    // or if it returns { chats: [...] }
    const chatList = Array.isArray(data) ? data : (data.chats || []);
    setChats(chatList);
  } catch (error) {
    console.error("Error fetching chat list:", error);
  }
};

const loadHistory = async (sessionId) => {
  setIsLoading(true); // Show loading state while fetching history
  try {
    const data = await chatService.getChatHistory(sessionId);
    
    // LOGIC CHECK: 
    // If your backend returns the messages array directly: setMessages(data)
    // If your backend returns { history: [...] }: setMessages(data.history)
    const history = Array.isArray(data) ? data : (data.history || data.messages || []);
    
    setMessages(history);
  } catch (error) {
    console.error("Error fetching history:", error);
  } finally {
    setIsLoading(false);
  }
};

  const handleNewChat = async () => {
    try {
      const { session_id } = await chatService.createSession();
      setActiveSessionId(session_id);
      loadChats(); // Refresh list
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  const handleDeleteChat = async (sessionId) => {
    try {
      await chatService.deleteChat(sessionId);
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
      }
      loadChats();
    } catch (error) {
      console.error("Failed to delete chat:", error);
    }
  };

  const handleSendMessage = async (query) => {
    let currentSessionId = activeSessionId;
    
    // Auto-create session if none exists when sending a message
    if (!currentSessionId) {
       try {
         const { session_id } = await chatService.createSession();
         currentSessionId = session_id;
         setActiveSessionId(session_id);
         loadChats();
       } catch (error) {
         console.error("Failed to create session for message:", error);
         return;
       }
    }

    const newUserMsg = { role: 'user', content: query };
    setMessages((prev) => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const { response } = await chatService.sendMessage(currentSessionId, query);
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [...prev, { role: 'assistant', content: '**Error:** Failed to reach the research agent.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-dark-900 text-slate-100 overflow-hidden">
      <Sidebar 
        chats={chats} 
        activeSessionId={activeSessionId}
        onSelectChat={setActiveSessionId}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />
      <ChatWindow 
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}