import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authService } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({ email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) { setError('Passwords do not match'); return }
    setLoading(true)
    try {
      const data = await authService.register(form.email, form.password)
      login(data.token, { email: form.email })
      navigate('/app')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#080d1a' }}>
      <div className="w-full max-w-md px-8 py-10 rounded-2xl"
        style={{ background: 'rgba(15,22,40,0.8)', border: '1px solid rgba(30,45,74,0.8)' }}>

        <h1 className="font-display text-3xl font-bold text-slate-100 mb-2">Create account</h1>
        <p className="text-slate-500 text-sm mb-8">Start researching with Inquiro</p>

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl text-sm text-red-400"
            style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">Email</label>
            <input
              type="email" name="email" value={form.email}
              onChange={handleChange} required placeholder="you@example.com"
              className="w-full px-4 py-2.5 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none"
              style={{ background: 'rgba(8,13,26,0.8)', border: '1px solid rgba(30,45,74,0.8)' }}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">Password</label>
            <input
              type="password" name="password" value={form.password}
              onChange={handleChange} required placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none"
              style={{ background: 'rgba(8,13,26,0.8)', border: '1px solid rgba(30,45,74,0.8)' }}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">Confirm Password</label>
            <input
              type="password" name="confirm" value={form.confirm}
              onChange={handleChange} required placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none"
              style={{ background: 'rgba(8,13,26,0.8)', border: '1px solid rgba(30,45,74,0.8)' }}
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl font-semibold text-sm text-white transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50 mt-2"
            style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)' }}
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-accent hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}