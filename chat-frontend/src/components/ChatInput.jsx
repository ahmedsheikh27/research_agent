// src/components/ChatInput.jsx
export default function ChatInput({ value, onChange, onSend, loading }) {
  return (
    <div className="border-t border-zinc-800 p-4 flex gap-2">
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={e => e.key === "Enter" && onSend()}
        className="flex-1 bg-zinc-900 border border-zinc-800 rounded px-4 py-2 outline-none"
        placeholder="Type a message..."
      />
      <button
        onClick={onSend}
        disabled={loading}
        className="bg-emerald-600 hover:bg-emerald-500 px-4 rounded disabled:opacity-50"
      >
        Send
      </button>
    </div>
  );
}
