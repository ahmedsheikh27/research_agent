export default function MessageBubble({ role, content }) {
  const lines = content.split("\n").filter(line => line.trim() !== "");

  const extractSources = (text) => {
    const urlRegex = /(https?:\/\/[^\s)]+)/g;
    const matches = [...text.matchAll(urlRegex)];

    const sources = matches
      .map(match => match[0])
      .filter(url => {
        try {
          new URL(url);
          return true;
        } catch {
          return false;
        }
      });

    const cleanText = text.replace(urlRegex, "").trim();

    return { text: cleanText, sources };
  };

  return (
    <div
      className={`max-w-[70%] px-4 py-3 rounded-lg ${
        role === "user"
          ? "ml-auto bg-zinc-800"
          : "mr-auto bg-zinc-900 border border-zinc-700"
      }`}
    >
      {role === "assistant" ? (
        <ol className="list-decimal list-inside space-y-3">
          {lines.map((line, index) => {
            const { text, sources } = extractSources(line);

            return (
              <li key={index}>
                {/* Render all text first */}
                <span>{text}</span>

                {/* Render all URLs at the END of the line */}
                {sources.length > 0 && (
                  <span className="ml-1">
                    {sources.map((source, i) => (
                      <a
                        key={i}
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 underline ml-1"
                      >
                        ([{source}])
                      </a>
                    ))}
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      ) : (
        <p>{content}</p>
      )}
    </div>
  );
}