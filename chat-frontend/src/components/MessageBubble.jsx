// src/components/MessageBubble.jsx
export default function MessageBubble({ role, content }) {
  return (
    <div
      className={`max-w-[70%] px-4 py-3 rounded-lg ${
        role === "user"
          ? "ml-auto bg-zinc-800"
          : "mr-auto bg-none"
      }`}
    >
      {content}
    </div>
  );
}
