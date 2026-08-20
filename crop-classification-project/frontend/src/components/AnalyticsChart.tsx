import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';

interface AnalyticsChartsProps {
  lat?: number;
  lng?: number;
}

const defaultData = [
  { name: 'Oct 23', ndvi: 0.2 },
  { name: 'Nov 23', ndvi: 0.35 },
  { name: 'Dec 23', ndvi: 0.65 },
  { name: 'Jan 24', ndvi: 0.78 },
  { name: 'Feb 24', ndvi: 0.74 },
  { name: 'Mar 24', ndvi: 0.68 },
];

export function AnalyticsCharts({ lat, lng }: AnalyticsChartsProps) {
  const [chartData, setChartData] = useState(defaultData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!lat || !lng) return;

    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/api/satellite/history', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lat, lon: lng }),
        });
        const result = await response.json();
        
        // Handle both formats: [{date: '...'}, ...] or {dates: [], ndvi: []}
        if (Array.isArray(result)) {
            setChartData(result);
        } else if (result.dates && result.ndvi) {
            const formatted = result.dates.map((d: string, i: number) => ({
                name: d,
                ndvi: result.ndvi[i]
            }));
            setChartData(formatted);
        }
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [lat, lng]);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-6 h-full mt-0 relative"
    >
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-semibold text-textPrimary">Vegetation Index (NDVI) History</h3>
          <p className="text-sm text-textPrimary/60 mt-1">6-month temporal health analysis.</p>
        </div>
        {loading && <Activity className="w-5 h-5 text-primary animate-spin" />}
      </div>
      
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorNdvi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00F5D4" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#00F5D4" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="rgba(255,255,255,0.3)" 
              tick={{fill: 'rgba(255,255,255,0.5)', fontSize: 10}} 
            />
            <YAxis 
              stroke="rgba(255,255,255,0.3)" 
              tick={{fill: 'rgba(255,255,255,0.5)', fontSize: 10}} 
              domain={[0, 1]} 
            />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.95)', borderColor: 'rgba(0, 245, 212, 0.2)', borderRadius: '8px' }}
              itemStyle={{ color: '#00F5D4' }}
              cursor={{ stroke: 'rgba(0, 245, 212, 0.2)', strokeWidth: 2 }}
            />
            <Area 
               type="monotone" 
               dataKey="ndvi" 
               stroke="#00F5D4" 
               strokeWidth={3} 
               fillOpacity={1} 
               fill="url(#colorNdvi)" 
               animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-4 border-t border-white/5 flex gap-4 text-[10px] font-mono text-textPrimary/40">
         <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded bg-primary/20 border border-primary/40" />
            <span>GROWTH STAGE: {chartData[chartData.length-1]?.ndvi > 0.7 ? 'PEAK' : 'DEVELOPING'}</span>
         </div>
         <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded bg-secondary/20 border border-secondary/40" />
            <span>LAST SCAN: MARCH 2024</span>
         </div>
      </div>
    </motion.div>
  );
}
