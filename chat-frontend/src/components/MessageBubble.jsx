import { motion } from 'framer-motion';
import { Brain, User, ExternalLink } from 'lucide-react';

export default function MessageBubble({ message }) {
  const { role, content } = message;
  const isUser = role === "user";

  // Your extraction logic
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

  // Split content into lines for the list view
  const lines = content.split("\n").filter(line => line.trim() !== "");

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 w-full max-w-4xl mx-auto p-4 md:p-6 rounded-2xl transition-all ${
        isUser ? "bg-transparent" : "bg-dark-800/50 border border-dark-600/50 shadow-sm"
      }`}
    >
      {/* Icon Avatar */}
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 ${
        isUser ? "bg-dark-700" : "bg-primary-500/10 border border-primary-500/20"
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-slate-400" />
        ) : (
          <Brain className="w-5 h-5 text-primary-400" />
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {!isUser ? (
          <ul className="list-none space-y-4">
            {lines.map((line, index) => {
              const { text, sources } = extractSources(line);
              
              return (
                <li key={index} className="text-slate-200 leading-relaxed">
                  <div className="flex flex-col gap-2">
                    {/* The Research Text */}
                    <span>{text}</span>
                    
                    {/* Clickable Sources Chip-style */}
                    {sources.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-1">
                        {sources.map((source, i) => (
                          <a
                            key={i}
                            href={source}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-dark-700 hover:bg-dark-600 border border-dark-600 text-xs text-primary-400 transition-colors group"
                          >
                            <ExternalLink className="w-3 h-3 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                            Source {sources.length > 1 ? i + 1 : ""}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-slate-200 pt-1.5 leading-relaxed">{content}</p>
        )}
      </div>
    </motion.div>
  );
}