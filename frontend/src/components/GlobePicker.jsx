import React from 'react';
import { motion } from 'framer-motion';
import { Navigation } from 'lucide-react';

/**
 * GlobePicker.jsx
 * ───────────────
 * Circular orb location picker with fluid radar scan,
 * glowing ping beacons, and reactive spring selection.
 */
export default function GlobePicker({ 
  currentCity = 'Delhi', 
  onCitySelect = () => {},
  cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Bhubaneswar']
}) {
  // Approximate coordinate percentages for Indian subcontinent on the stylized globe
  const cityCoordinates = {
    'Delhi': { x: 44, y: 32 },
    'Mumbai': { x: 34, y: 56 },
    'Bangalore': { x: 46, y: 72 },
    'Chennai': { x: 55, y: 74 },
    'Hyderabad': { x: 48, y: 60 },
    'Bhubaneswar': { x: 62, y: 52 },
    'Kolkata': { x: 68, y: 46 },
    'Jaipur': { x: 38, y: 36 },
  };

  return (
    <div className="relative flex flex-col items-center select-none">
      {/* Globe Container */}
      <div className="relative w-40 h-40 rounded-full overflow-hidden border border-white/20 shadow-2xl flex items-center justify-center bg-gradient-to-br from-white/10 via-white/5 to-black/40 backdrop-blur-xl group">
        
        {/* Subtle Map Silhouette Vector */}
        <svg
          viewBox="0 0 160 160"
          className="absolute inset-0 w-full h-full opacity-35 transition-transform duration-700 group-hover:scale-105"
        >
          <defs>
            <radialGradient id="globeAtmosphere" cx="50%" cy="50%" r="50%">
              <stop offset="65%" stopColor="transparent" />
              <stop offset="100%" stopColor="rgba(255, 255, 255, 0.28)" />
            </radialGradient>
          </defs>
          <circle cx="80" cy="80" r="78" fill="url(#globeAtmosphere)" />
          {/* Stylized continent outline */}
          <path
            d="M 60 20 Q 75 35 70 55 T 85 85 Q 95 105 75 130 Q 65 140 55 125 T 45 95 Q 35 70 50 45 Z"
            fill="rgba(255, 255, 255, 0.22)"
          />
          <path
            d="M 90 40 Q 110 35 125 55 T 130 85 Q 115 105 105 90 Z"
            fill="rgba(255, 255, 255, 0.16)"
          />
        </svg>

        {/* Ambient Radar Sweep */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 12, ease: "linear" }}
          className="absolute inset-0 pointer-events-none rounded-full"
          style={{
            background: 'conic-gradient(from 0deg, transparent 0deg, transparent 310deg, rgba(251, 191, 36, 0.18) 360deg)',
          }}
        />

        {/* Ambient Orb Highlight Glint */}
        <div className="absolute top-1 left-2 w-20 h-10 rounded-full bg-gradient-to-b from-white/25 to-transparent blur-sm pointer-events-none transform -rotate-12" />

        {/* City Location Pins */}
        {cities.map((c) => {
          const coords = cityCoordinates[c] || { x: 50, y: 50 };
          const isSelected = c.toLowerCase() === currentCity.toLowerCase();

          return (
            <motion.button
              key={c}
              whileHover={{ scale: 1.4 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => onCitySelect(c)}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10"
              style={{ left: `${coords.x}%`, top: `${coords.y}%` }}
              title={c}
            >
              {isSelected ? (
                <div className="relative flex items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-4 w-4 rounded-full bg-amber-400 opacity-80" />
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-white border border-amber-500 shadow-md shadow-amber-500/60" />
                </div>
              ) : (
                <div className="w-2 h-2 rounded-full bg-white/60 hover:bg-white hover:scale-125 transition-all border border-black/40 shadow-sm" />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Selected City Pill Chip */}
      <motion.div 
        key={currentCity}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 350, damping: 25 }}
        className="mt-3.5 px-4 py-1.5 rounded-full glass-pill flex items-center gap-2 text-xs font-light text-white/95 border border-white/20 shadow-md"
      >
        <Navigation className="w-3 h-3 text-amber-300 transform -rotate-45" />
        <span className="font-medium">{currentCity}, India</span>
      </motion.div>
    </div>
  );
}
