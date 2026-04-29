import { motion } from 'framer-motion';

export default function FeatureCard({ icon: Icon, title, description, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="bg-dark-800 border border-dark-600 p-6 rounded-2xl hover:bg-dark-700 transition-colors"
    >
      <div className="bg-dark-900 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-primary-400" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
    </motion.div>
  );
}