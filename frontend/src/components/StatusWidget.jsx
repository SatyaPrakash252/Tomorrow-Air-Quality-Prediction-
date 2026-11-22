import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ChevronRight, HelpCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

/**
 * StatusWidget.jsx
 * ────────────────
 * Left sidebar status card with fluid micro-animations:
 * Features a dynamic curve with path drawing animation, glowing milestone,
 * floating frosted bubble, and hover spring physics.
 */
export default function StatusWidget({ 
  statusLabel = 'Severe Risk', 
  trendPercent = '23.8%', 
  aqiValue = 184,
  category = 'Unhealthy' 
}) {
  const navigate = useNavigate();

  // Dynamic bubble text and color based on category/aqi
  const isDangerous = aqiValue > 150;
  const isModerate = aqiValue > 100 && aqiValue <= 150;
  const bubbleText = isDangerous ? 'Dangerous' : (isModerate ? 'Moderate' : 'Good Air');
  const bubbleBg = isDangerous 
    ? 'bg-rose-500/90 text-white border border-rose-300/40 shadow-rose-900/40' 
    : (isModerate 
        ? 'bg-amber-400 text-slate-950 border border-amber-300 shadow-amber-900/30' 
        : 'bg-emerald-400 text-slate-950 border border-emerald-300 shadow-emerald-900/30');

  return (
    <div className="w-full space-y-2 select-none">
      {/* Label and Badge */}
      <div className="flex items-center justify-between text-xs text-white/70 font-light px-0.5">
        <span>Atmospheric Status</span>
        <span className="text-[10px] font-mono text-white/50">{category}</span>
      </div>

      {/* Glass Status Card */}
      <motion.div 
        whileHover={{ y: -3, scale: 1.015 }}
        transition={{ type: "spring", stiffness: 350, damping: 22 }}
        className="glass-card p-3.5 relative overflow-hidden group cursor-pointer"
        onClick={() => navigate('/risk')}
      >
        {/* Trend Pill & Info */}
        <div className="flex items-center justify-between mb-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/15 text-[11px] text-white/90 font-light border border-white/20">
            <TrendingUp className="w-2.5 h-2.5 text-amber-300" />
            <span>↑ {trendPercent}</span>
          </div>
          <HelpCircle className="w-3.5 h-3.5 text-white/40 group-hover:text-white/80 transition-colors" />
        </div>

        {/* Mini Curve with Callout Bubble */}
        <div className="relative h-16 w-full flex items-center justify-center">
          <svg viewBox="0 0 180 60" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="statusGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="60%" stopColor="#fbbf24" />
                <stop offset="100%" stopColor="#f43f5e" />
              </linearGradient>
              <filter id="dotGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="3" />
                <feMerge>
                  <feMergeNode />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {/* Smooth upward curve with animated stroke */}
            <motion.path
              d="M 10 50 C 60 50, 110 35, 155 16"
              fill="none"
              stroke="url(#statusGrad)"
              strokeWidth="2.5"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            />
            {/* Glowing Milestone Dot on curve */}
            <motion.circle
              cx="155"
              cy="16"
              r="4.5"
              fill="#ffffff"
              stroke="#fbbf24"
              strokeWidth="2"
              filter="url(#dotGlow)"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.9, type: "spring", stiffness: 400, damping: 20 }}
            />
          </svg>

          {/* Floating Frosted Callout Bubble with subtle breathing spring */}
          <motion.div 
            initial={{ scale: 0.8, opacity: 0, y: 5 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            transition={{ delay: 0.3, type: "spring", stiffness: 300, damping: 20 }}
            className={`absolute top-2 left-6 px-3 py-1 rounded-full text-xs font-semibold shadow-lg backdrop-blur-md ${bubbleBg}`}
            style={{ borderRadius: '14px 14px 14px 4px' }}
          >
            <span>{bubbleText}</span>
          </motion.div>
        </div>
      </motion.div>

      {/* See More Details Link */}
      <button
        onClick={() => navigate('/risk')}
        className="flex items-center justify-center gap-1 w-full text-center text-xs text-white/60 hover:text-white transition-colors pt-1 cursor-pointer group"
      >
        <span>See Health Details</span>
        <ChevronRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
      </button>
    </div>
  );
}
