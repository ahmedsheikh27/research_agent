import { Hash, MoreHorizontal, Search, Share2 } from 'lucide-react'
import React from 'react'
import { useNavigate } from 'react-router-dom'

const Header = () => {
    const navigate = useNavigate()
    return (
        <header className="h-16  border-b border-dark-600 bg-dark-900/50 backdrop-blur-md flex items-center justify-between px-6 z-20">
          <div className="flex items-center gap-3">
            <div onClick={() => navigate("/")} className="flex items-center gap-2 cursor-pointer group">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                <Search className="w-4 h-4 text-white stroke-[3px]" />
              </div>
              <span className="text-xl font-bold tracking-tight">inquiro</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 text-slate-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
              <Share2 size={18} />
            </button>
            <button className="p-2 text-slate-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
              <MoreHorizontal size={18} />
            </button>
          </div>
        </header>
    )
}

export default Header