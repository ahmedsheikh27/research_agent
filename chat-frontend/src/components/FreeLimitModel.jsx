import { useNavigate } from 'react-router-dom'
import { LogIn, UserPlus, X } from 'lucide-react'

export default function FreeLimitModal({ onClose }) {
  const navigate = useNavigate()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-8 relative"
        style={{ background: 'rgba(15,22,40,0.95)', border: '1px solid rgba(30,45,74,0.9)' }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-500 hover:text-slate-300 transition-colors"
          style={{ background: 'rgba(30,45,74,0.4)' }}
        >
          <X size={16} />
        </button>

        {/* Icon */}
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6"
          style={{ background: 'rgba(79,142,247,0.1)', border: '1px solid rgba(79,142,247,0.2)' }}
        >
          <span className="text-2xl">🔒</span>
        </div>

        <h2 className="font-display text-2xl font-bold text-slate-100 mb-2">
          Free Limit Reached
        </h2>
        <p className="text-slate-400 text-sm leading-relaxed mb-8">
          You have used all <span className="text-accent font-semibold">5 free messages</span>.
          Create a free account or sign in to continue researching with unlimited access and PDF uploads.
        </p>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/register')}
            className="w-full py-3 rounded-xl font-semibold text-sm text-white transition-all duration-200 hover:scale-105 active:scale-95"
            style={{ background: 'linear-gradient(135deg, #4f8ef7, #2563eb)', boxShadow: '0 0 20px rgba(79,142,247,0.3)' }}
          >
            <UserPlus size={16} className="inline mr-2" />
            Create Free Account
          </button>

          <button
            onClick={() => navigate('/login')}
            className="w-full py-3 rounded-xl font-semibold text-sm text-slate-300 transition-all duration-200 hover:scale-105 active:scale-95"
            style={{ background: 'rgba(30,45,74,0.4)', border: '1px solid rgba(30,45,74,0.8)' }}
          >
            <LogIn size={16} className="inline mr-2" />
            Sign In
          </button>
        </div>
      </div>
    </div>
  )
}