import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Search, Zap, Upload, Lock, Plus } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { chatService } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useGuestLimit } from '../hooks/useMessageLimit'
import FreeLimitModal from './FreeLimitModel'
import { Link } from 'react-router-dom'

function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-6 transition-all duration-300 ease-out opacity-100 translate-y-0">
      <div className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center"
        style={{ background: 'rgba(15,22,40,0.8)', border: '1px solid rgba(30,45,74,0.8)' }}>
        <Zap size={14} color="#4f8ef7" strokeWidth={1.5} />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-3"
        style={{ background: 'rgba(12,20,34,0.9)', border: '1px solid rgba(30,45,74,0.8)' }}>
        <div className="flex items-center gap-1.5">
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent inline-block" />
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent inline-block" />
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-accent inline-block" />
        </div>
        <span className="text-xs text-slate-400 animate-pulse">Generating response...</span>
      </div>
    </div>
  )
}

function EmptyState({ canCreateChat, onCreateChat }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center px-6 py-12">
      <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
        style={{ background: 'rgba(79,142,247,0.1)', border: '1px solid rgba(79,142,247,0.2)' }}>
        <Search size={28} color="#4f8ef7" strokeWidth={1.5} />
      </div>
      <h2 className="font-display text-2xl font-bold text-slate-200 mb-3">Ask Anything</h2>
      <p className="text-slate-500 text-sm max-w-sm leading-relaxed">
        Inquiro searches the web, analyzes sources, and synthesizes structured research answers.
      </p>
      {canCreateChat && (
        <button
          onClick={onCreateChat}
          className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm text-white transition-all hover:scale-105"
          style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)' }}
        >
          <Plus size={14} />
          Start a new chat
        </button>
      )}
    </div>
  )
}

export default function ChatWindow({ sessionId, initialMessages, onCreateChat }) {
  const { isAuthenticated } = useAuth()
  const { hasReachedLimit, increment, remaining } = useGuestLimit()

  const [messages, setMessages] = useState(initialMessages || [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showLimitModal, setShowLimitModal] = useState(false)
  const [isPdfUploading, setIsPdfUploading] = useState(false)

  const bottomRef = useRef(null)
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => { setMessages(initialMessages || []) }, [sessionId, initialMessages])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, isLoading])

  const handleSend = async () => {
    const query = input.trim()
    if (!query || isLoading || !sessionId) return

    // Block guests who hit the limit
    if (!isAuthenticated && hasReachedLimit()) {
      setShowLimitModal(true)
      return
    }

    setMessages(prev => [...prev, { role: 'user', content: query }])
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setIsLoading(true)
    setError(null)

    try {
      const data = await chatService.sendMessage(sessionId, query)
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])

      // Only count for guests
      if (!isAuthenticated) increment()

    } catch (err) {
      if (err.message?.includes('403') || err.message?.includes('limit')) {
        setShowLimitModal(true)
      } else {
        setError(err.message || 'Something went wrong.')
      }
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  const handlePdfClick = () => {
    if (!isAuthenticated) {
      setShowLimitModal(true)
      return
    }
    fileInputRef.current?.click()
  }

  const handlePdfUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsPdfUploading(true)
    setError(null)
    try {
      await chatService.uploadPDF(file)
    } catch (err) {
      setError(err.message || 'PDF upload failed.')
    } finally {
      setIsPdfUploading(false)
      e.target.value = ''
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const handleInput = (e) => {
    setInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px'
    }
  }

  return (
    <div className="flex flex-col flex-1 h-full overflow-hidden">

      {/* Guest banner */}
      {!isAuthenticated && (
        <div className="flex-shrink-0 px-6 py-2 flex items-center justify-between"
          style={{ background: 'rgba(245,158,11,0.05)', borderBottom: '1px solid rgba(245,158,11,0.15)' }}>
          <p className="text-xs text-slate-500">
            Guest mode —{' '}
            <span className="font-medium" style={{ color: '#f59e0b' }}>
              {remaining()} free message{remaining() !== 1 ? 's' : ''} remaining
            </span>
          </p>
          <Link to="/register" className="text-xs text-accent hover:underline font-medium">
            Sign up for unlimited access →
          </Link>
        </div>
      )}

      {!sessionId ? (
        <div className="flex-1 flex items-center justify-center px-6 py-6">
          <EmptyState
            canCreateChat={isAuthenticated}
            onCreateChat={onCreateChat}
          />
        </div>
      ) : (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-6">
            {messages.length !== 0 &&
              <div className="max-w-3xl mx-auto">
                {messages.map((msg, i) => (
                  <MessageBubble key={i} message={msg} />
                ))}
                {isLoading && <TypingIndicator />}
              </div>
            }
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-6 pb-6 pt-2">
            <div className="max-w-3xl mx-auto rounded-2xl overflow-hidden"
              style={{ background: 'rgba(12,20,34,0.9)', border: '1px solid rgba(30,45,74,0.9)' }}>

              <div className="flex items-end gap-3 p-3 pl-4">

                {/* PDF button with tooltip */}
                <div className="relative group flex-shrink-0">
                  <button
                    onClick={handlePdfClick}
                    disabled={isPdfUploading}
                    className="flex items-center gap-2 px-3 h-9 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50 text-xs font-medium whitespace-nowrap"
                    style={{
                      background: 'rgba(30,45,74,0.5)',
                      border: '1px solid rgba(30,45,74,0.8)',
                      color: isAuthenticated ? '#4f8ef7' : '#475569',
                    }}
                  >
                    {isPdfUploading
                      ? <Loader2 size={14} color="#4f8ef7" className="animate-spin" />
                      : isAuthenticated
                        ? <Upload size={14} color="#4f8ef7" strokeWidth={1.5} />
                        : <Lock size={14} color="#475569" strokeWidth={1.5} />
                    }
                    {isPdfUploading ? 'Uploading...' : 'Upload PDF'}
                  </button>

                  {/* Tooltip for guests */}
                  {!isAuthenticated && (
                    <div
                      className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2.5 w-48 px-3 py-2.5 rounded-xl text-xs text-slate-300 text-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50"
                      style={{
                        background: 'rgba(12,20,34,0.97)',
                        border: '1px solid rgba(79,142,247,0.25)',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                      }}
                    >
                      <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0"
                        style={{
                          borderLeft: '5px solid transparent',
                          borderRight: '5px solid transparent',
                          borderTop: '5px solid rgba(79,142,247,0.25)',
                        }}
                      />
                      <span className="text-accent font-semibold block mb-1">🔒 Login Required</span>
                      PDF upload is only available for registered users.
                      <Link to="/register" className="block mt-1.5 text-accent hover:underline">
                        Create free account →
                      </Link>
                    </div>
                  )}
                </div>

                <input ref={fileInputRef} type="file" accept=".pdf" onChange={handlePdfUpload} className="hidden" />

                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInput}
                  onKeyDown={handleKeyDown}
                  placeholder={isAuthenticated ? 'Ask a research question...' : 'Ask a question (guest mode)...'}
                  rows={1}
                  disabled={isLoading}
                  className="flex-1 bg-transparent text-slate-200 placeholder-slate-600 text-sm resize-none outline-none leading-relaxed py-1.5 max-h-40"
                  style={{ scrollbarWidth: 'none', minHeight: '36px' }}
                />

                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                  style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)' }}
                >
                  {isLoading
                    ? <Loader2 size={15} color="white" className="animate-spin" />
                    : <Send size={15} color="white" strokeWidth={2} />
                  }
                </button>
              </div>

              <div className="px-4 pb-2.5">
                <p className="text-xs text-slate-700">Enter to send — Shift+Enter for newline</p>
              </div>
            </div>
          </div>
        </>
      )}
      {/* Error */}
      {error && (
        <div className="px-6 pb-2">
          <div className="max-w-3xl mx-auto px-4 py-2.5 rounded-xl text-xs text-red-400"
            style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
            {error}
          </div>
        </div>
      )}
      {showLimitModal && <FreeLimitModal onClose={() => setShowLimitModal(false)} />}
    </div>
  )
}