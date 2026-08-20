import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendUp?: boolean;
  icon: ReactNode;
  delay?: number;
}

export function MetricCard({ title, value, trend, trendUp, icon, delay = 0 }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass-card p-6 flex flex-col justify-between h-full bg-card/40 hover:bg-card/60"
    >
      <div className="flex items-start justify-between">
        <div className="p-3 bg-white/5 rounded-xl border border-white/10 text-primary">
          {icon}
        </div>
        {trend && (
          <div className={`px-2 py-1 rounded-md text-xs font-semibold ${trendUp ? 'bg-primary/20 text-primary' : 'bg-red-500/20 text-red-400'}`}>
            {trend}
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-textPrimary/60 mb-1">{title}</p>
        <h3 className="text-3xl font-bold tracking-tight text-white mb-2 heading-glow">{value}</h3>
        <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: typeof value === 'string' && value.includes('%') ? value : '70%' }}
            transition={{ duration: 1, delay: delay + 0.2 }}
            className="h-full bg-primary relative"
          >
            <div className="absolute top-0 right-0 bottom-0 w-4 bg-white/50 blur-sm animate-pulse"></div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
