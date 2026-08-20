import { LayoutDashboard, Map, Leaf, BrainCircuit, BarChart3, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

const NAV_ITEMS = [
  { name: 'Overview', icon: LayoutDashboard, id: 'overview' },
  { name: 'Satellite Map', icon: Map, id: 'map' },
  { name: 'Crop Health', icon: Leaf, id: 'health' },
  { name: 'AI Prediction', icon: BrainCircuit, id: 'prediction' },
  { name: 'Analytics', icon: BarChart3, id: 'analytics' },
  { name: 'Settings', icon: Settings, id: 'settings' },
];

export function Sidebar({ activeTab, setActiveTab }: { activeTab: string; setActiveTab: (id: string) => void }) {
  return (
    <motion.aside 
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      className="w-64 border-r border-borderGlow h-[calc(100vh-4rem)] p-4 flex flex-col gap-2 bg-card/30 backdrop-blur-xl"
    >
      <div className="text-xs uppercase text-textPrimary/40 font-semibold tracking-wider mb-2 ml-4">
        Menu
      </div>
      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item w-full text-left flex items-center gap-3 relative overflow-hidden ${isActive ? 'active' : ''}`}
            >
              {isActive && (
                <motion.div 
                  layoutId="activeTabIndicator" 
                  className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-glow"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <Icon className={`w-5 h-5 z-10 ${isActive ? 'text-primary' : 'text-textPrimary/50'}`} />
              <span className={`z-10 font-medium ${isActive ? 'text-primary' : 'text-textPrimary/70'}`}>
                {item.name}
              </span>
            </button>
          );
        })}
      </nav>
      
      <div className="mt-auto pt-4 border-t border-borderGlow">
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-textPrimary/60">System Status</p>
            <p className="text-sm font-semibold text-primary">Operational</p>
          </div>
          <div className="w-3 h-3 rounded-full bg-primary shadow-glow animate-pulse"></div>
        </div>
      </div>
    </motion.aside>
  );
}
