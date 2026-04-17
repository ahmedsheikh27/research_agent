import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

const extractErrorMessage = (error) => {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || JSON.stringify(item)).join(', ')
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return error.message || 'An error occurred'
}

const getStoredAuthToken = () => {
  return sessionStorage.getItem('token') || sessionStorage.getItem('guest_token')
}

const ensureGuestToken = async () => {
  const existing = getStoredAuthToken()
  if (existing) return existing

  const res = await axios.post('http://127.0.0.1:8000/auth/guest')
  const guestToken = res.data?.token
  if (guestToken) {
    sessionStorage.setItem('guest_token', guestToken)
    return guestToken
  }
  return null
}

// Attach token from sessionStorage to every request
api.interceptors.request.use(async (config) => {
  let token = getStoredAuthToken()
  const path = config.url || ''
  const needsAuthForGuest = path.startsWith('/chat')

  if (!token && needsAuthForGuest) {
    token = await ensureGuestToken()
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const hasToken = !!sessionStorage.getItem('token')
    if (error.response?.status === 401 && hasToken) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      window.location.href = '/login'
    }
    const message = extractErrorMessage(error)
    return Promise.reject(new Error(message))
  }
)

// ─── AUTH ────────────────────────────────────────────────
export const authService = {
  // POST /auth/register → { token }
  register: async (email, password) => {
    const res = await api.post('/auth/register', { email, password })
    return res.data
  },

  // POST /auth/login → { token }
  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password })
    return res.data
  },
}

// ─── CHAT ────────────────────────────────────────────────
export const chatService = {
  // POST /chat/new → { session_id } (works for guest + auth)
  createSession: async () => {
    const res = await api.post('/chat/new')
    return res.data
  },

  // GET /chat → { chats: [...] } (auth only — 401 for guests)
  getAllChats: async () => {
    const res = await api.get('/chat')
    return res.data.chats
  },

  // GET /chat/:session_id → { session_id, messages, user_email } (auth only)
  getChatHistory: async (sessionId) => {
    const res = await api.get(`/chat/${sessionId}`)
    return res.data
  },

  // POST /chat → { response } (guest: max 5 messages, auth: unlimited)
  sendMessage: async (sessionId, query) => {
    const res = await api.post('/chat', { session_id: sessionId, query })
    return res.data
  },

  // DELETE /chat/:session_id → { message } (auth only)
  deleteChat: async (sessionId) => {
    const res = await api.delete(`/chat/${sessionId}`)
    return res.data
  },

  // POST /chat/upload-pdf → { message, session_id } (auth only)
  uploadPDF: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/chat/upload-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
}

export default api