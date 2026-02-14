// src/components/Sidebar.jsx
export default function Sidebar({ chats, active, onNew, onSelect }) {
  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col">
      <button
        onClick={onNew}
        className="m-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
      >
        + New Chat
      </button>
      <div className="flex-1 overflow-y-auto">
        {chats.map(c => (
          <div
            key={c.session_id}
            onClick={() => onSelect(c.session_id)}
            className={`px-4 py-3 cursor-pointer border-b border-zinc-800 hover:bg-zinc-900 ${
              active === c.session_id ? "bg-zinc-800" : ""
            }`}
          >
            {c.title}
          </div>
        ))}
      </div>
    </aside>
  );
}
