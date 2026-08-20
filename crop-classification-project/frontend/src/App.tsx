import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { Dashboard } from './components/Dashboard';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="flex h-screen w-full bg-[#0B0F19] text-[#E5E7EB] font-sans selection:bg-[#00F5D4] selection:text-[#0B0F19] overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#00F5D4]/10 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-[#3B82F6]/10 rounded-full blur-[150px] mix-blend-screen pointer-events-none" />
        <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-[#A78BFA]/10 rounded-full blur-[100px] mix-blend-screen pointer-events-none" />
      </div>

      <div className="relative z-10 flex flex-col flex-1">
        <TopNav />
        <main className="flex flex-1 overflow-hidden">
          <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
          
          <AnimatePresence mode="wait">
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 h-full"
              >
                <Dashboard />
              </motion.div>
            )}
            
            {activeTab !== 'overview' && (
              <motion.div
                key="other"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 h-[calc(100vh-4rem)] flex items-center justify-center"
              >
                <div className="glass-card p-12 text-center max-w-md">
                  <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                    <div className="w-8 h-8 rounded-full bg-primary/20 animate-ping absolute" />
                    <div className="w-4 h-4 rounded-full bg-primary shadow-[0_0_15px_rgba(0,245,212,0.8)]" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2">Module Under Construction</h2>
                  <p className="text-textPrimary/60 text-sm">
                    The &apos;{activeTab}&apos; module is currently being optimized by our AI agents. Check back soon.
                  </p>
                  <button 
                    onClick={() => setActiveTab('overview')}
                    className="mt-8 btn-primary px-8"
                  >
                    Return to Overview
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;
