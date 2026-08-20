import { Bell, Settings, User } from 'lucide-react';
import { motion } from 'framer-motion';

export function TopNav() {
  return (
    <header className="h-16 border-b border-borderGlow bg-background/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10 w-full">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold tracking-wide flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          Sentinel <span className="text-primary/90 font-light">Dashboard</span>
        </h1>
      </div>
      
      <div className="flex items-center gap-4">
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="p-2 rounded-full hover:bg-white/5 relative">
          <Bell className="w-5 h-5 text-textPrimary/70" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-secondary rounded-full border border-background"></span>
        </motion.button>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="p-2 rounded-full hover:bg-white/5">
          <Settings className="w-5 h-5 text-textPrimary/70" />
        </motion.button>
        <div className="w-px h-6 bg-borderGlow mx-2"></div>
        <motion.button whileHover={{ scale: 1.05 }} className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
          <User className="w-4 h-4 text-primary" />
        </motion.button>
      </div>
    </header>
  );
}
