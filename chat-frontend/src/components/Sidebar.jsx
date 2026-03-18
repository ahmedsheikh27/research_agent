import { useRef, useState } from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  FileUp,    // Added missing import
  FileText   // Added for the PDF logo in history
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Sidebar({ chats, activeSessionId, onSelectChat, onNewChat, onDeleteChat, onUploadPDF, isUploading }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const fileInputRef = useRef(null);

  return (
    <motion.div
      animate={{ width: isCollapsed ? 80 : 260 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="bg-dark-800 border-r border-dark-600 flex flex-col h-screen flex-shrink-0 relative z-30"
    >
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-20 bg-dark-700 border border-dark-600 rounded-full p-1.5 hover:text-primary-400 z-50 text-slate-400 shadow-lg"
      >
        {isCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
      </button>

      {/* Action Buttons */}
      <div className="p-4 space-y-2">
        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          className={`w-full flex items-center gap-2 bg-primary-500 hover:bg-primary-400 text-white rounded-xl transition-all shadow-lg shadow-primary-500/10 ${
            isCollapsed ? 'justify-center p-2.5' : 'px-4 py-2.5'
          }`}
          title="New Chat"
        >
          <Plus size={18} />
          {!isCollapsed && <span className="font-medium">New Chat</span>}
        </button>

        {/* Upload PDF Button */}
        <button
          onClick={() => fileInputRef.current.click()}
          disabled={isUploading}
          className={`w-full flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-slate-200 rounded-xl border border-dark-600 transition-all disabled:opacity-50 ${
            isCollapsed ? 'justify-center p-2.5' : 'px-4 py-2.5'
          }`}
          title="Upload PDF"
        >
          <FileUp size={18} className={isUploading ? "animate-pulse" : ""} />
          {!isCollapsed && <span className="font-medium text-sm text-nowrap">{isUploading ? "Uploading..." : "Upload PDF"}</span>}
        </button>

        <input
          type="file"
          ref={fileInputRef}
          hidden
          accept=".pdf"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              onUploadPDF(e.target.files[0]);
              e.target.value = null; // Reset to allow same file re-upload
            }
          }}
        />
      </div>

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-1 custom-scrollbar">
        {!isCollapsed && (
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 mb-2">
            History
          </h3>
        )}
        
        {chats.map((chat) => {
          // Check if it's a PDF chat by title or a flag from backend
          const isPdfChat = chat.is_pdf || chat.title?.toLowerCase().endsWith('.pdf');

          return (
            <div
              key={chat.session_id}
              onClick={() => onSelectChat(chat.session_id)}
              className={`group relative flex items-center rounded-xl cursor-pointer transition-all h-11 ${
                isCollapsed ? 'justify-center' : 'px-3 gap-3'
              } ${
                activeSessionId === chat.session_id
                  ? 'bg-dark-700 text-primary-400 border border-dark-600 shadow-inner'
                  : 'text-slate-400 hover:bg-dark-700/50 hover:text-slate-200'
              }`}
            >
              {/* Dynamic Icon based on PDF status */}
              {isPdfChat ? (
                <FileText className="w-4 h-4 flex-shrink-0 text-red-400/80" />
              ) : (
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
              )}

              {!isCollapsed && (
                <>
                  <span className="text-sm truncate flex-1 select-none pr-6">
                    {chat.title || "Untitled Chat"}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteChat(chat.session_id);
                    }}
                    className="absolute right-2 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 p-1.5 transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </>
              )}

              {/* Tooltip for Collapsed State */}
              {isCollapsed && (
                <div className="absolute left-16 scale-0 group-hover:scale-100 transition-all origin-left bg-dark-600 text-white text-[11px] py-1.5 px-3 rounded-lg shadow-xl whitespace-nowrap z-50 pointer-events-none border border-dark-500">
                  {chat.title || 'Untitled Chat'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-dark-600 bg-dark-800/50">
        <div className={`flex items-center gap-3 text-slate-500 ${isCollapsed ? 'justify-center' : ''}`}>
          <div className="w-8 h-8 rounded-lg bg-dark-900 border border-dark-600 flex items-center justify-center flex-shrink-0 shadow-inner">
            <Search className="w-3.5 h-3.5 text-primary-500" />
          </div>
          {!isCollapsed && (
             <div className="flex flex-col">
               <span className="text-[10px] font-bold text-slate-400 tracking-tighter uppercase">Inquiro AI</span>
               <span className="text-[9px] text-slate-600">v1.0.4-stable</span>
             </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}