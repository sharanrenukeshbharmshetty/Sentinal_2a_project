import { useState, useCallback } from 'react';
import Map, { Marker, NavigationControl, FullscreenControl } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Target } from 'lucide-react';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || 'YOUR_MAPBOX_TOKEN_HERE';

interface SatelliteMapProps {
  onLocationSelect?: (lat: number, lng: number) => void;
}

export function SatelliteMap({ onLocationSelect }: SatelliteMapProps) {
  const [viewState, setViewState] = useState({
    latitude: 20.5937,
    longitude: 78.9629,
    zoom: 4
  });

  const [marker, setMarker] = useState<{ lat: number; lng: number } | null>(null);

  const onMapClick = useCallback((event: any) => {
    const { lng, lat } = event.lngLat;
    setMarker({ lat, lng });
    if (onLocationSelect) {
      onLocationSelect(lat, lng);
    }
  }, [onLocationSelect]);

  return (
    <div className="glass-card h-[400px] overflow-hidden relative border border-white/5">
      <div className="absolute top-4 left-4 z-10">
         <div className="bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2 shadow-xl">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-mono text-white/80">Select Region for Analysis</span>
         </div>
      </div>

      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        onClick={onMapClick}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/satellite-v9"
        mapboxAccessToken={MAPBOX_TOKEN}
        cursor="crosshair"
      >
        <NavigationControl position="bottom-right" />
        <FullscreenControl position="bottom-right" />

        {marker && (
          <Marker longitude={marker.lng} latitude={marker.lat}>
            <div className="relative">
              <div className="absolute -top-8 -left-1/2 whitespace-nowrap bg-primary text-black text-[10px] font-bold px-2 py-0.5 rounded shadow-lg translate-x-3">
                 TARGET LOCKED
              </div>
              <Target className="text-primary w-8 h-8 drop-shadow-[0_0_8px_rgba(0,245,212,0.8)]" />
            </div>
          </Marker>
        )}
      </Map>

      {/* Map Overlays */}
      <div className="absolute bottom-4 left-4 z-10 pointer-events-none">
        <div className="flex flex-col gap-1 text-[10px] font-mono text-white/50 bg-black/40 p-2 rounded border border-white/5">
           <span>SOURCE: ESA Sentinel-2A</span>
           <span>MODE: Multitemporal</span>
           {marker && (
             <span className="text-primary/80">COORD: {marker.lat.toFixed(4)}N, {marker.lng.toFixed(4)}E</span>
           )}
        </div>
      </div>
    </div>
  );
}
