import { useState } from 'react';
import { motion } from 'framer-motion';
import { Leaf, Droplets, BrainCircuit, Activity, Globe } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { SatelliteScanner } from './SatelliteScanner';
import { AnalyticsCharts } from './AnalyticsChart';
import { SatelliteMap } from './SatelliteMap';

export function Dashboard() {
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  const handleLocationSelect = (lat: number, lng: number) => {
    setCoords({ lat, lng });
  };

  const handleGlobalScan = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/satellite/global-scan');
      const data = await response.json();
      setScanResult(data);
    } catch (error) {
      console.error('Global scan failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
      <div className="max-w-7xl mx-auto space-y-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-between items-end mb-8"
        >
          <div>
            <h2 className="text-3xl font-bold text-white heading-glow">Advanced Intelligence Dashboard</h2>
            <p className="text-textPrimary/60 mt-1">Global Sentinel-2A monitoring, growth analysis and drought detection.</p>
          </div>
          <motion.div className="flex gap-4">
            <div className="hidden md:flex flex-col items-end justify-center px-4 border-r border-white/10">
               <span className="text-[10px] text-textPrimary/40 font-mono uppercase">Sync Status</span>
               <span className="text-xs text-primary font-bold">{loading ? 'SCANNING...' : 'UP TO DATE'}</span>
            </div>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleGlobalScan}
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
              {loading ? 'Analyzing Earth...' : 'Global Sync Analysis'}
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Top metrics level */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Avg NDVI Index"
            value={coords ? "0.82" : (scanResult ? "0.76" : "0.74")}
            trend="+5.2%"
            trendUp={true}
            icon={<Leaf className="w-6 h-6" />}
            delay={0.1}
          />
          <MetricCard
            title="Soil Moisture (NDWI)"
            value={coords ? "38%" : (scanResult ? "44%" : "42%")}
            trend={scanResult ? "Optimal" : "-1.4%"}
            trendUp={true}
            icon={<Droplets className="w-6 h-6" />}
            delay={0.2}
          />
          <MetricCard
            title="Biomass Growth"
            value={scanResult ? "+14%" : "Optimal"}
            trend={scanResult ? "Accelerated" : "Normal"}
            trendUp={true}
            icon={<Activity className="w-6 h-6" />}
            delay={0.3}
          />
          <MetricCard
            title="Drought Risk"
            value={scanResult?.drought_alerts > 0 ? "Alert" : "Min."}
            trend={scanResult?.drought_alerts > 0 ? "1 Active" : "No Alerts"}
            trendUp={false}
            icon={<BrainCircuit className="w-6 h-6" />}
            delay={0.4}
          />
        </div>

        {/* Global Stats Banner if scan complete */}
        {scanResult && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-4 bg-primary/5 border border-primary/20 flex gap-8 items-center overflow-x-auto whitespace-nowrap"
          >
             <div className="flex flex-col">
                <span className="text-[10px] text-primary/60 font-mono uppercase">Area Scanned</span>
                <span className="text-sm font-bold text-white">{scanResult.total_area_scanned}</span>
             </div>
             {scanResult.regional_data.map((hub: any, i: number) => (
                <div key={i} className="flex flex-col border-l border-white/10 pl-8">
                   <span className="text-[10px] text-textPrimary/40 font-mono uppercase">{hub.region}</span>
                   <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{hub.crop}:</span>
                      <span className={`text-xs font-bold ${hub.condition.includes('Drought') ? 'text-red-400' : 'text-primary'}`}>
                         {hub.condition}
                      </span>
                   </div>
                </div>
             ))}
          </motion.div>
        )}

        {/* Main interactive area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Global Monitoring Map */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="relative"
            >
              <SatelliteMap onLocationSelect={handleLocationSelect} />
            </motion.div>

            {/* Satellite Panel (Now Details Panel) */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.35 }}
            >
              <SatelliteScanner lat={coords?.lat} lng={coords?.lng} />
            </motion.div>
            
            {/* Analytics Panel */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <AnalyticsCharts lat={coords?.lat} lng={coords?.lng} />
            </motion.div>
          </div>

          <div className="lg:col-span-1 space-y-6">
            {/* AI Prediction Panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="glass-card p-6 border-l-4 border-l-primary"
            >
              <div className="flex items-center gap-3 mb-4 border-b border-white/5 pb-4">
                <div className="p-2 bg-primary/20 rounded-lg text-primary">
                  <BrainCircuit className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">AI Prediction</h3>
                  <p className="text-xs text-textPrimary/50">ResNet & Vision Transformer</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-background/40 p-4 rounded-xl border border-white/5">
                  <p className="text-sm text-textPrimary/60 mb-1">Primary Detection</p>
                  <div className="flex justify-between items-baseline mb-2">
                    <h4 className="text-2xl font-bold text-primary heading-glow">Wheat</h4>
                    <span className="text-sm font-semibold text-primary/80">98.4%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-1.5 overflow-hidden">
                    <div className="bg-primary h-1.5 rounded-full shadow-[0_0_10px_rgba(0,245,212,0.8)]" style={{ width: '98.4%' }}></div>
                  </div>
                </div>

                <div className="bg-background/40 p-4 rounded-xl border border-white/5">
                  <p className="text-sm text-textPrimary/60 mb-1">Secondary Detection</p>
                  <div className="flex justify-between items-baseline mb-2">
                    <h4 className="text-lg font-bold text-secondary text-shadow-sm">Maize</h4>
                    <span className="text-sm font-semibold text-secondary/80">1.2%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-1.5 overflow-hidden">
                    <div className="bg-secondary h-1.5 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)]" style={{ width: '1.2%' }}></div>
                  </div>
                </div>
                
                <div className="pt-2">
                  <div className="flex justify-between text-sm py-2 border-b border-white/5">
                    <span className="text-textPrimary/60">Estimated Yield:</span>
                    <span className="font-semibold text-white">4.2 Tons/ha</span>
                  </div>
                  <div className="flex justify-between text-sm py-2">
                    <span className="text-textPrimary/60">Disease Risk:</span>
                    <span className="font-semibold text-green-400">Low (12%)</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Notification/Log Panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="glass-card p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-highlight" /> Active Logs
              </h3>
              
              <div className="space-y-3">
                {[
                  { time: '10:42 AM', msg: 'New satellite image acquired.', type: 'info' },
                  { time: '10:43 AM', msg: 'Cloud cover removed (1.2% obscured).', type: 'success' },
                  { time: '10:45 AM', msg: 'NDVI calculation complete.', type: 'info' },
                  { time: '10:46 AM', msg: 'Inference model complete.', type: 'highlight' },
                ].map((log, i) => (
                  <div key={i} className="flex gap-3 text-sm">
                    <span className="text-textPrimary/40 font-mono text-xs mt-0.5">{log.time}</span>
                    <span className={`
                      ${log.type === 'info' ? 'text-textPrimary/80' : ''}
                      ${log.type === 'success' ? 'text-primary' : ''}
                      ${log.type === 'highlight' ? 'text-highlight' : ''}
                    `}>
                      {log.msg}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
