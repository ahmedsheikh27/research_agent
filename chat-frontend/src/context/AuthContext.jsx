import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // On mount, restore session from sessionStorage
    const savedToken = sessionStorage.getItem('token')
    const savedUser = sessionStorage.getItem('user')

    if (savedToken && savedUser) {
      try {
        setToken(savedToken)
        setUser(JSON.parse(savedUser))
        setIsAuthenticated(true)
      } catch {
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = (tokenValue, userData) => {
    sessionStorage.setItem('token', tokenValue)
    sessionStorage.setItem('user', JSON.stringify(userData))
    setToken(tokenValue)
    setUser(userData)
    setIsAuthenticated(true)
  }

  const logout = () => {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user')
    setToken(null)
    setUser(null)
    setIsAuthenticated(false)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}