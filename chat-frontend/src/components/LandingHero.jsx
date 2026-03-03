import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Brain, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import FeatureCard from './FeatureCard';

export default function LandingHero() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary-500/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[120px] rounded-full pointer-events-none" />

      <main className="flex-1 flex flex-col items-center justify-center px-4 z-10">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center mt-10 gap-2 px-3 py-1 rounded-full bg-dark-800 border border-dark-600 text-sm text-slate-300 mb-8">
            <Sparkles className="w-4 h-4 text-primary-400" />
            <span>Next-gen research capabilities</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight mb-6">
            Inquiro
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-400 mb-10 font-light">
            Ask. Discover. Understand.
            <br className="hidden md:block" /> Transform questions into deep, structured insights powered by intelligent web search and AI-driven synthesis.
          </p>
          
          <button 
            onClick={() => navigate('/app')}
            className="group inline-flex items-center gap-2 bg-primary-500 hover:bg-primary-400 text-white px-8 py-4 rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(79,70,229,0.3)]"
          >
            Start Research
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-24">
          <FeatureCard 
            icon={Search}
            title="Web Search"
            description="Real-time internet access to pull the most recent and relevant data for your queries."
            delay={0.2}
          />
          <FeatureCard 
            icon={Brain}
            title="RAG Intelligence"
            description="Advanced retrieval-augmented generation to contextualize and cross-reference information."
            delay={0.4}
          />
          <FeatureCard 
            icon={Sparkles}
            title="Structured Output"
            description="Clean, markdown-formatted responses that are easy to read and export."
            delay={0.6}
          />
        </div>
      </main>

      <footer className="py-8 text-center text-slate-500 mt-10 text-sm z-10 border-t border-dark-800">
        &copy; {new Date().getFullYear()} AI Research Agent. All rights reserved.
      </footer>
    </div>
  );
}