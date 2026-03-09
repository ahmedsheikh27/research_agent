import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ messages, onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-dark-900 relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-50">
            <Sparkles className="w-12 h-12 text-primary-500 mb-4" />
            <h2 className="text-xl font-medium text-white mb-2">What would you like to research?</h2>
            <p className="text-slate-400 max-w-md">
              Ask anything. I will search the web, analyze data, and synthesize a structured report.
            </p>
          </div>
        ) : (
          <div className="space-y-6 pb-24">
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} />
            ))}
            {isLoading && (
              <div className="flex gap-4 w-full max-w-4xl mx-auto p-6">
                <div className="w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center flex-shrink-0">
                  <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                </div>
                <div className="pt-1.5 flex items-center">
                  <span className="text-slate-400 animate-pulse">Researching...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-2 bg-gradient-to-t from-gray-950 via-dark-900 to-transparent pt-10 pb-6 px-2 md:px-8 pointer-events-none">

        <div className="max-w-4xl mx-auto pointer-events-auto">

          <form
            onSubmit={handleSubmit}
            className="relative bg-dark-800 border border-dark-600 rounded-2xl shadow-xl overflow-hidden focus-within:border-primary-500/50 transition-colors"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask a research question..."
              className="w-full bg-transparent text-slate-100 p-4 pr-14 max-h-48 resize-none focus:outline-none scrollbar-thin"
              rows={1}
              style={{ minHeight: '56px' }}
            />

            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 bottom-2 p-2 rounded-xl bg-primary-500 text-white disabled:opacity-50 disabled:bg-dark-600 hover:bg-primary-400 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>

          <div className="text-center mt-2">
            <span className="text-xs text-slate-500">
              AI can make mistakes. Verify important information.
            </span>
          </div>

        </div>
      </div>
    </div>
  );
}