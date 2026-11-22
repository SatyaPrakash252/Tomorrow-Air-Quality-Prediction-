import React, { useState } from 'react';
import { motion } from 'framer-motion';

/**
 * SineWaveTimeline.jsx
 * ────────────────────
 * Ultra-fluid atmospheric sine-wave forecast timeline:
 * Features liquid SVG path morphing, spring-tracked glowing sun marker,
 * multi-stop radiant atmospheric fill, and interactive hover scrubbing.
 */
export default function SineWaveTimeline({ 
  forecastDays = [], 
  selectedIndex = 1, 
  onSelectDay = () => {},
  mode = 'aqi'
}) {
  const [hoveredIdx, setHoveredIdx] = useState(null);
  const activeIdx = hoveredIdx !== null ? hoveredIdx : selectedIndex;

  // Safe fallback 6-day forecast
  const days = (Array.isArray(forecastDays) && forecastDays.length >= 4) ? forecastDays : [
    { day: 'Today', value: '28°', aqi: 124, condition: 'Moderate' },
    { day: 'Tomorrow', value: '26°', aqi: 112, condition: 'Satisfactory' },
    { day: 'Wednesday', value: '27°', aqi: 138, condition: 'Moderate' },
    { day: 'Thursday', value: '23°', aqi: 184, condition: 'Poor' },
    { day: 'Friday', value: '30°', aqi: 215, condition: 'Very Poor' },
    { day: 'Saturday', value: '25°', aqi: 145, condition: 'Moderate' },
  ];

  const width = 800;
  const height = 110;
  const count = Math.max(2, days.length);
  const step = width / (count - 1);

  // Generate harmonic sine wave coordinates for each day
  const points = days.map((item, i) => {
    const x = i * step;
    // Harmonic wave with natural curvature
    const waveOffset = Math.sin((i / (count - 1)) * Math.PI * 2.8 + 0.3);
    const y = 55 + waveOffset * 32;
    return {
      x: Number.isFinite(x) ? Math.round(x * 10) / 10 : 0,
      y: Number.isFinite(y) ? Math.round(y * 10) / 10 : 55,
      ...item
    };
  });

  // Construct smooth cubic bezier SVG path through points
  let pathD = points.length > 0 ? `M ${points[0].x} ${points[0].y}` : '';
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i];
    const p1 = points[i + 1];
    const cp1x = p0.x + (p1.x - p0.x) / 2;
    const cp1y = p0.y;
    const cp2x = p0.x + (p1.x - p0.x) / 2;
    const cp2y = p1.y;
    pathD += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p1.x} ${p1.y}`;
  }

  // Soft shaded area under the curve
  const areaD = pathD ? `${pathD} L ${width} ${height} L 0 ${height} Z` : '';

  const safeIdx = Math.max(0, Math.min(points.length - 1, activeIdx ?? 0));
  const activePoint = points[safeIdx] || { x: 50, y: 55 };

  const springCurve = { type: "spring", stiffness: 220, damping: 24, mass: 0.7 };

  return (
    <div className="w-full select-none py-2">
      {/* Day Names Row */}
      <div className="flex justify-between items-center px-4 mb-2 text-xs font-light tracking-wide text-white/70">
        {days.map((d, i) => {
          const isActive = i === safeIdx;
          return (
            <motion.button
              key={i}
              whileHover={{ y: -2, scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => onSelectDay(i)}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              className={`transition-colors duration-200 cursor-pointer relative py-1 ${
                isActive 
                  ? 'text-white font-medium opacity-100' 
                  : 'text-white/60 hover:text-white/90'
              }`}
              style={{ width: `${100 / count}%`, textAlign: 'center' }}
            >
              <span>{d.day}</span>
              {isActive && (
                <motion.div
                  layoutId="activeDayDot"
                  className="w-1.5 h-1.5 rounded-full bg-amber-400 mx-auto mt-0.5 shadow-sm shadow-amber-400/80"
                  transition={springCurve}
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Interactive Sine Curve SVG with Liquid Morphing */}
      <div className="relative w-full h-[110px] overflow-visible">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-full overflow-visible"
          preserveAspectRatio="none"
        >
          <defs>
            <filter id="sunGlow" x="-60%" y="-60%" width="220%" height="220%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur1" />
              <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            
            <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(255, 255, 255, 0.45)" />
              <stop offset="50%" stopColor="rgba(255, 255, 255, 0.95)" />
              <stop offset="100%" stopColor="rgba(255, 255, 255, 0.45)" />
            </linearGradient>

            <linearGradient id="waveAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(251, 191, 36, 0.22)" />
              <stop offset="50%" stopColor="rgba(255, 255, 255, 0.08)" />
              <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
            </linearGradient>
          </defs>

          {/* Area under wave */}
          {areaD && (
            <motion.path
              d={areaD}
              fill="url(#waveAreaGrad)"
              initial={false}
              animate={{ d: areaD }}
              transition={springCurve}
            />
          )}

          {/* Vertical dashed guide line to the active sun dot with smooth motion */}
          <motion.line
            animate={{
              x1: activePoint.x,
              y1: activePoint.y,
              x2: activePoint.x,
              y2: height,
            }}
            transition={springCurve}
            stroke="rgba(255, 255, 255, 0.5)"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />

          {/* Smooth undulating sine wave line with spring morphing */}
          {pathD && (
            <motion.path
              d={pathD}
              fill="none"
              stroke="url(#waveGrad)"
              strokeWidth="2.75"
              strokeLinecap="round"
              initial={false}
              animate={{ d: pathD }}
              transition={springCurve}
            />
          )}

          {/* Inactive small milestone dots */}
          {points.map((p, i) => (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={i === safeIdx ? 0 : 3.5}
              fill="rgba(255, 255, 255, 0.45)"
              className="transition-all duration-300 pointer-events-none"
            />
          ))}

          {/* Pulsing Corona outer aura */}
          <motion.circle
            animate={{
              cx: activePoint.x,
              cy: activePoint.y,
              r: [10, 16, 10],
              opacity: [0.45, 0.15, 0.45],
            }}
            transition={{
              cx: springCurve,
              cy: springCurve,
              r: { repeat: Infinity, duration: 2.4, ease: "easeInOut" },
              opacity: { repeat: Infinity, duration: 2.4, ease: "easeInOut" },
            }}
            fill="#fbbf24"
            className="pointer-events-none"
          />

          {/* Glowing Sun-like Active Dot with Spring Physics */}
          <motion.circle
            animate={{
              cx: activePoint.x,
              cy: activePoint.y,
            }}
            transition={springCurve}
            r="7"
            fill="#ffffff"
            filter="url(#sunGlow)"
            className="pointer-events-none"
          />

          {/* Inner intense core */}
          <motion.circle
            animate={{
              cx: activePoint.x,
              cy: activePoint.y,
            }}
            transition={springCurve}
            r="3.5"
            fill="#ffffff"
            className="pointer-events-none"
          />
        </svg>
      </div>

      {/* Values / Temperatures / AQI Row with Smooth Spring Transitions */}
      <div className="flex justify-between items-end px-4 mt-2">
        {days.map((d, i) => {
          const isActive = i === safeIdx;
          const displayMain = mode === 'aqi' ? (d.aqi ?? d.value) : d.value;
          const displaySub = mode === 'aqi' 
            ? `${d.condition || 'Moderate'} • ${d.value}`
            : (d.aqi ? `AQI ${d.aqi}` : d.condition);

          return (
            <motion.button
              key={i}
              whileHover={{ scale: 1.06, y: -2 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => onSelectDay(i)}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              className="transition-all duration-300 text-center cursor-pointer group"
              style={{ width: `${100 / count}%` }}
            >
              <span
                className={`block transition-all duration-300 font-['Instrument_Sans'] ${
                  isActive
                    ? 'text-3xl sm:text-4xl font-light text-white scale-110 tracking-tight drop-shadow'
                    : 'text-2xl sm:text-3xl font-extralight text-white/60 group-hover:text-white/90 tracking-tight'
                }`}
              >
                {displayMain}
              </span>
              <span
                className={`block text-[11px] font-mono mt-0.5 transition-opacity ${
                  isActive ? 'text-amber-200 font-medium opacity-100' : 'text-white/60 opacity-80'
                }`}
              >
                {displaySub}
              </span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
