// src/components/ChatWindow.jsx
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, loading, endRef }) {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((m, i) => (
        <MessageBubble key={i} {...m} />
      ))}
      {loading && (
        <div className="bg-emerald-800 px-4 py-3 rounded-lg w-fit animate-pulse">
          Typing...
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
