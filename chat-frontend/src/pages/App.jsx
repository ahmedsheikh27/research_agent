import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import { chatService } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { Loader2 } from 'lucide-react'

export default function AppPage() {
  const navigate = useNavigate()
  const { sessionId: routeSessionId } = useParams()
  const { isAuthenticated, user, logout } = useAuth()
  const [chats, setChats] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [currentMessages, setCurrentMessages] = useState([])
  const [sidebarLoading, setSidebarLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)
  const createChatPromiseRef = useRef(null)

  const navigateToSession = useCallback((sessionId) => {
    if (!sessionId) return
    navigate(`/app/${sessionId}`, { replace: true })
  }, [navigate])

  const createNewChat = useCallback(async () => {
    if (createChatPromiseRef.current) {
      return createChatPromiseRef.current
    }

    const createPromise = (async () => {
      setSidebarLoading(true)
      try {
        const data = await chatService.createSession()
        const sessionId = data.session_id

        if (isAuthenticated) {
          setChats(prev => (
            prev.some(chat => chat.session_id === sessionId)
              ? prev
              : [{ session_id: sessionId, messages: [] }, ...prev]
          ))
        }

        setCurrentSessionId(sessionId)
        setCurrentMessages([])
        navigateToSession(sessionId)
        return sessionId
      } catch (err) {
        console.error('Failed to create chat:', err)
        return null
      } finally {
        setSidebarLoading(false)
        createChatPromiseRef.current = null
      }
    })()

    createChatPromiseRef.current = createPromise

    return createPromise
  }, [isAuthenticated, navigateToSession])

  const handleSelectChat = useCallback(async (sessionId) => {
    if (!sessionId || sessionId === currentSessionId) return
    setCurrentSessionId(sessionId)
    navigateToSession(sessionId)
    try {
      const chatData = await chatService.getChatHistory(sessionId)
      setCurrentMessages(chatData.messages || [])
    } catch (err) {
      console.error('Failed to load chat:', err)
      setCurrentMessages([])
    }
  }, [currentSessionId, navigateToSession])

  const handleDeleteChat = useCallback(async (deletedId) => {
    if (!deletedId) return
    try {
      await chatService.deleteChat(deletedId)
      const updated = chats.filter(c => c.session_id !== deletedId)
      setChats(updated)

      if (currentSessionId === deletedId) {
        if (updated.length > 0) {
          await handleSelectChat(updated[0].session_id)
        } else {
          setCurrentSessionId(null)
          setCurrentMessages([])
          navigate('/app', { replace: true })
        }
      }
    } catch (err) {
      console.error('Failed to delete chat:', err)
    }
  }, [chats, currentSessionId, handleSelectChat, navigate])

  const handleUploadPDF = useCallback(async (file) => {
    if (!file) return
    setIsUploading(true)
    try {
      const data = await chatService.uploadPDF(file)
      const uploadedSessionId = data?.session_id

      if (uploadedSessionId) {
        if (!chats.some(chat => chat.session_id === uploadedSessionId)) {
          setChats(prev => [{ session_id: uploadedSessionId, title: file.name, is_pdf: true }, ...prev])
        }
        await handleSelectChat(uploadedSessionId)
      }
    } catch (err) {
      console.error('Failed to upload PDF:', err)
    } finally {
      setIsUploading(false)
    }
  }, [chats, handleSelectChat])

  useEffect(() => {
    let isMounted = true

    const init = async () => {
      setIsInitializing(true)

      if (isAuthenticated) {
        // Authenticated users: load existing chats only.
        // Do not auto-create chat sessions.
        try {
          const savedChats = await chatService.getAllChats()
          if (!isMounted) return
          const normalizedChats = savedChats || []
          setChats(normalizedChats)

          if (normalizedChats.length > 0) {
            const routeMatch = routeSessionId
              ? normalizedChats.find(chat => chat.session_id === routeSessionId)
              : null
            const target = routeMatch || normalizedChats[0]

            setCurrentSessionId(target.session_id)
            if (!routeMatch) navigateToSession(target.session_id)
            try {
              const chatData = await chatService.getChatHistory(target.session_id)
              if (!isMounted) return
              setCurrentMessages(chatData.messages || [])
            } catch {
              if (!isMounted) return
              setCurrentMessages([])
            }
          } else {
            setCurrentSessionId(null)
            setCurrentMessages([])
            if (routeSessionId) navigate('/app', { replace: true })
          }
        } catch {
          if (!isMounted) return
          setChats([])
          setCurrentSessionId(null)
          setCurrentMessages([])
        }
      } else {
        // Guest — create a temporary session, no API history calls
        if (routeSessionId) {
          setCurrentSessionId(routeSessionId)
          setCurrentMessages([])
        } else {
          await createNewChat()
        }
      }

      if (isMounted) setIsInitializing(false)
    }
    init()

    return () => {
      isMounted = false
    }
  }, [createNewChat, isAuthenticated, navigateToSession, routeSessionId])

  if (isInitializing) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: '#080d1a' }}>
        <div className="text-center">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-4"
            style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)', boxShadow: '0 0 24px rgba(79,142,247,0.4)' }}>
            <Loader2 size={22} color="white" className="animate-spin" />
          </div>
          <p className="text-slate-500 text-sm">Initializing Inquiro...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex overflow-hidden" style={{ background: '#080d1a' }}>

      {/* Sidebar — authenticated users only */}
      {isAuthenticated && (
        <Sidebar
          chats={chats}
          activeSessionId={currentSessionId}
          onSelectChat={handleSelectChat}
          onNewChat={createNewChat}
          onDeleteChat={handleDeleteChat}
          onUploadPDF={handleUploadPDF}
          isUploading={isUploading || sidebarLoading}
        />
      )}

      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="flex-shrink-0 px-6 py-3 flex items-center justify-between"
          style={{ background: 'rgba(8,13,26,0.8)', borderBottom: '1px solid rgba(30,45,74,0.5)' }}>

          <div className="flex items-center gap-3">
            {!isAuthenticated && (
              <span className="text-xs px-2.5 py-1 rounded-full font-medium"
                style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)', color: '#f59e0b' }}>
                Guest Mode
              </span>
            )}
            <div>
              <h1 className="font-display text-base font-semibold text-slate-200">
                {isAuthenticated ? `Welcome, ${user?.email}` : 'Inquiro Research'}
              </h1>
              {currentSessionId && (
                <p className="text-xs text-slate-600 font-mono">{currentSessionId}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500"
                    style={{ boxShadow: '0 0 6px rgba(34,197,94,0.6)' }} />
                  <span className="text-xs text-slate-500">Connected</span>
                </div>
                <button onClick={logout}
                  className="text-xs text-slate-500 hover:text-red-400 transition-colors px-3 py-1.5 rounded-lg"
                  style={{ background: 'rgba(30,45,74,0.3)' }}>
                  Logout
                </button>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login"
                  className="text-xs px-3 py-1.5 rounded-lg text-slate-300 transition-all hover:scale-105"
                  style={{ background: 'rgba(30,45,74,0.4)', border: '1px solid rgba(30,45,74,0.8)' }}>
                  Sign In
                </Link>
                <Link to="/register"
                  className="text-xs px-3 py-1.5 rounded-lg text-white transition-all hover:scale-105"
                  style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)' }}>
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>

        <ChatWindow
          key={currentSessionId}
          sessionId={currentSessionId}
          initialMessages={currentMessages}
          onCreateChat={createNewChat}
        />
      </main>
    </div>
  )
}