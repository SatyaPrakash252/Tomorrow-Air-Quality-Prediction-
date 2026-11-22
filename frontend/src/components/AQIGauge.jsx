import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getAQICategory } from '../data/mockData';
import { Activity, ShieldAlert, Sparkles } from 'lucide-react';

export default function AQIGauge({ value, size = 260, label = "CPCB Real-Time AQI" }) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const maxAQI = 500;
  const clampedValue = Math.min(Math.max(value, 0), maxAQI);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(clampedValue), 150);
    return () => clearTimeout(timer);
  }, [clampedValue]);

  const center = size / 2;
  const radius = (size / 2) - 24;
  const strokeWidth = 16;
  const startAngle = 140;
  const endAngle = 400;
  const totalAngle = endAngle - startAngle;

  const valueAngle = startAngle + (animatedValue / maxAQI) * totalAngle;

  // Arc path generator
  const describeArc = (cx, cy, r, startAng, endAng) => {
    const startRad = (startAng * Math.PI) / 180;
    const endRad = (endAng * Math.PI) / 180;
    const x1 = cx + r * Math.cos(startRad);
    const y1 = cy + r * Math.sin(startRad);
    const x2 = cx + r * Math.cos(endRad);
    const y2 = cy + r * Math.sin(endRad);
    const largeArc = endAng - startAng > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
  };

  const segments = [
    { max: 50, color: '#10B981', label: 'Good' },
    { max: 100, color: '#34D399', label: 'Satisfactory' },
    { max: 200, color: '#FBBF24', label: 'Moderate' },
    { max: 300, color: '#F97316', label: 'Poor' },
    { max: 400, color: '#EF4444', label: 'Very Poor' },
    { max: 500, color: '#991B1B', label: 'Severe' },
  ];

  const category = getAQICategory(clampedValue);

  // Needle position
  const needleAngle = startAngle + (animatedValue / maxAQI) * totalAngle;
  const needleRad = (needleAngle * Math.PI) / 180;
  const needleLength = radius - 14;
  const needleX = center + needleLength * Math.cos(needleRad);
  const needleY = center + needleLength * Math.sin(needleRad);

  return (
    <div className="flex flex-col items-center justify-center relative p-2">
      
      {/* Subtle Glow Aura behind the dial */}
      <div 
        className="absolute w-44 h-44 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-700"
        style={{ backgroundColor: category.color }}
      />

      <svg width={size} height={size * 0.78} viewBox={`0 0 ${size} ${size * 0.85}`} className="overflow-visible">
        <defs>
          <linearGradient id="needleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor={category.color} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Track Base */}
        <path
          d={describeArc(center, center, radius, startAngle, endAngle)}
          fill="none"
          stroke="rgba(255, 255, 255, 0.06)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Subtle Category Segment Tick Backgrounds */}
        {segments.map((seg, i) => {
          const prevMax = i === 0 ? 0 : segments[i - 1].max;
          const segStart = startAngle + (prevMax / maxAQI) * totalAngle;
          const segEnd = startAngle + (seg.max / maxAQI) * totalAngle;
          return (
            <path
              key={i}
              d={describeArc(center, center, radius, segStart, segEnd)}
              fill="none"
              stroke={seg.color}
              strokeWidth={strokeWidth}
              strokeLinecap="butt"
              opacity={0.22}
            />
          );
        })}

        {/* Dynamic Colored Active Arc */}
        <motion.path
          d={describeArc(center, center, radius, startAngle, Math.min(valueAngle, endAngle))}
          fill="none"
          stroke={category.color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          style={{ filter: 'url(#glow)' }}
        />

        {/* Sleek Tapered Needle */}
        <motion.line
          x1={center}
          y1={center}
          x2={needleX}
          y2={needleY}
          stroke="url(#needleGradient)"
          strokeWidth={3}
          strokeLinecap="round"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          style={{ filter: `drop-shadow(0 0 6px ${category.color})` }}
        />

        {/* Needle Pivot Center */}
        <circle cx={center} cy={center} r={7} fill="#0f172a" stroke={category.color} strokeWidth={2.5} />
        <circle cx={center} cy={center} r={3} fill="#ffffff" />

        {/* Numeric Value */}
        <text 
          x={center} 
          y={center + 38} 
          textAnchor="middle"
          fill="#ffffff" 
          fontSize="2.75rem" 
          fontWeight="900"
          className="font-['Outfit'] tracking-tight select-none"
        >
          {Math.round(animatedValue)}
        </text>

        {/* Category Pill Inside Dial */}
        <text 
          x={center} 
          y={center + 60} 
          textAnchor="middle"
          fill={category.color} 
          fontSize="0.8rem" 
          fontWeight="700"
          letterSpacing="0.12em"
          className="font-mono uppercase select-none"
        >
          {category.label}
        </text>
      </svg>

      {/* Footer Sub-label with Pulsing Indicator */}
      <div className="flex items-center gap-2 mt-1 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08]">
        <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: category.color }} />
        <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">{label}</span>
      </div>

    </div>
  );
}
