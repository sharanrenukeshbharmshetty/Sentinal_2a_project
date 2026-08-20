import { motion, AnimatePresence } from 'framer-motion';
import { Target, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SatelliteScannerProps {
  lat?: number;
  lng?: number;
}

export function SatelliteScanner({ lat, lng }: SatelliteScannerProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (!lat || !lng) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/api/satellite/fetch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lat, lon: lng }),
        });
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Failed to fetch satellite data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [lat, lng]);

  return (
    <div className="glass-card flex flex-col h-[400px] overflow-hidden relative group cursor-crosshair">
      <div className="p-4 bg-background/50 border-b border-white/5 flex justify-between items-center z-10">
        <div>
          <h3 className="font-semibold text-white flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${loading ? 'bg-highlight animate-ping' : 'bg-secondary'}`} /> 
            Live Satellite Feed
          </h3>
          <p className="text-xs text-textPrimary/60 font-mono mt-1">
            {lat ? `LAT: ${lat.toFixed(4)}° | LNG: ${lng?.toFixed(4)}°` : 'Awaiting Coordinate Selection...'}
          </p>
        </div>
        <div className="flex gap-2 text-xs font-mono">
          <span className="px-2 py-1 bg-primary/10 rounded border border-primary/20 text-primary/70">IR Scan Active</span>
          {data?.status === 'demo' && (
            <span className="px-2 py-1 bg-amber-500/10 rounded border border-amber-500/20 text-amber-500/80">Demo Mode</span>
          )}
        </div>
      </div>
      
      <div className="flex-1 relative bg-[#020617] overflow-hidden flex items-center justify-center">
        {/* Animated Grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,245,212,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,212,0.05)_1px,transparent_1px)] bg-[size:20px_20px]" />
        
        {loading ? (
          <div className="flex flex-col items-center gap-4 z-20">
            <RefreshCw className="w-12 h-12 text-primary animate-spin" />
            <p className="text-primary font-mono text-sm animate-pulse italic">DECRYPTING SATELLITE TELEMETRY...</p>
          </div>
        ) : data ? (
          <AnimatePresence>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 z-10"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-green-900/40 via-blue-900/20 to-purple-900/40 mix-blend-overlay" />
              
              {/* Target Data Overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <motion.div 
                     animate={{ scale: [1, 1.1, 1], opacity: [0.6, 1, 0.6] }}
                     transition={{ duration: 3, repeat: Infinity }}
                     className="w-48 h-48 border border-primary/30 rounded-full flex items-center justify-center"
                  >
                    <div className="w-32 h-32 border border-primary/20 rounded-full" />
                  </motion.div>
                  
                  <div className="absolute -top-16 -right-32 glass-card p-3 border-l-2 border-l-primary scale-90 w-48">
                    <p className="text-[10px] text-primary font-bold uppercase tracking-widest">Detection Result</p>
                    <p className="text-xl font-bold text-white">{data.classification_preview.crop}</p>
                    <div className="flex items-center gap-2 mt-1 mb-2">
                       <span className="text-xs text-textPrimary/60">Confidence:</span>
                       <span className="text-xs font-bold text-primary">{data.classification_preview.confidence}%</span>
                    </div>
                    {data.agri_metrics && (
                       <div className="border-t border-white/5 pt-2 space-y-1">
                          <div className="flex justify-between text-[10px]">
                             <span className="text-textPrimary/40">GROWTH:</span>
                             <span className="text-primary font-bold">{data.agri_metrics.growth_momentum}</span>
                          </div>
                          <div className="flex justify-between text-[10px]">
                             <span className="text-textPrimary/40">MOISTURE:</span>
                             <span className="text-white font-bold">{(data.agri_metrics.moisture_index * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between text-[10px]">
                             <span className="text-textPrimary/40">RAIN EST:</span>
                             <span className="text-secondary font-bold">{data.agri_metrics.rainfall_estimate}</span>
                          </div>
                       </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        ) : (
          <div className="flex flex-col items-center gap-2 text-textPrimary/30 z-20 px-12 text-center">
             <Target className="w-12 h-12 opacity-20 mb-2" />
             <p className="text-sm">CLICK ON THE GLOBAL MONITORING MAP TO FETCH LOCALIZED TELEMETRY</p>
          </div>
        )}

        {/* Scanning Line */}
        {loading && (
          <motion.div 
            initial={{ y: -100 }}
            animate={{ y: 500 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_0_15px_rgba(0,245,212,0.8)] z-30"
          />
        )}
        
        {/* UI Overlays */}
        <div className="absolute bottom-4 left-4 text-[10px] text-textPrimary/40 font-mono flex flex-col gap-1 z-20">
          <span>Engine: TensorScan v4.1</span>
          <span>Buffer: {data ? 'LIVE STREAM' : 'STANDBY'}</span>
          <span>Ref: S2A_MSIL1C_20240315</span>
        </div>
      </div>
    </div>
  );
}
