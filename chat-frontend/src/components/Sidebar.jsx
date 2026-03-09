import { useState } from 'react';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  PanelLeftClose, 
  PanelLeftOpen, 
  Search 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Sidebar({ chats, activeSessionId, onSelectChat, onNewChat, onDeleteChat }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <motion.div
      animate={{ width: isCollapsed ? 80 : 260 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="bg-dark-800 border-r border-dark-600 flex flex-col h-screen flex-shrink-0 relative"
    >
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-20 bg-dark-700 border border-dark-600 rounded-full p-1.5 hover:text-primary-400 z-50 text-slate-400"
      >
        {isCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
      </button>

      {/* New Chat Button */}
      <div className="p-4 overflow-hidden">
        <button
          onClick={onNewChat}
          className={`flex items-center gap-2 bg-primary-500 hover:bg-blue-600 text-white rounded-xl font-medium transition-all h-11 ${
            isCollapsed ? 'w-11 justify-center' : 'w-full px-4'
          }`}
        >
          <Plus className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && <span className="whitespace-nowrap">New Chat</span>}
        </button>
      </div>

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-2 custom-scrollbar">
        <h3>Chats</h3>
        {chats.map((chat) => (
          <div
            key={chat.session_id}
            onClick={() => onSelectChat(chat.session_id)}
            className={`group relative flex items-center rounded-xl cursor-pointer transition-all h-11 ${
              isCollapsed ? 'justify-center' : 'px-3 gap-3'
            } ${
              activeSessionId === chat.session_id 
                ? 'bg-dark-700 text-primary-400 border border-dark-600' 
                : 'text-slate-400 hover:bg-dark-700/50 hover:text-slate-200'
            }`}
          >
            <MessageSquare className="w-4 h-4 flex-shrink-0" />
            
            {!isCollapsed && (
              <>
                <span className="text-sm truncate flex-1 select-none pr-6">
                  {chat.title || chat.session_id.substring(0, 8)}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.session_id);
                  }}
                  className="absolute right-2 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 p-1 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </>
            )}

            {/* Tooltip for Collapsed State */}
            {isCollapsed && (
              <div className="absolute left-16 scale-0 group-hover:scale-100 transition-transform origin-left bg-dark-600 text-white text-xs py-1.5 px-3 rounded-md whitespace-nowrap z-50 pointer-events-none">
                {chat.title || 'Previous Chat'}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-dark-600 overflow-hidden">
        <div className={`flex items-center gap-3 text-slate-500 ${isCollapsed ? 'justify-center' : ''}`}>
           <div className="w-8 h-8 rounded-lg bg-dark-700 flex items-center justify-center flex-shrink-0">
              <Search className="w-4 h-4 text-primary-400" />
           </div>
           {!isCollapsed && <span className="text-xs font-semibold tracking-wider uppercase">Inquiro v1.0</span>}
        </div>
      </div>
    </motion.div>
  );
}