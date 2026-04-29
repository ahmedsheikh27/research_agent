import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import AppPage from './pages/App'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Open to guests — limit enforced inside */}
        <Route path="/app" element={<AppPage />} />
        <Route path="/app/:sessionId" element={<AppPage />} />
        <Route path="/app/chat/:sessionId" element={<AppPage />} />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App