import React from 'react';

/**
 * SkeletonGlass.jsx
 * ─────────────────
 * Frosted glass skeleton loader matching the atmospheric WeatherWise theme.
 */
export default function SkeletonGlass({ className = 'h-6 w-full', rounded = 'rounded-2xl' }) {
  return (
    <div
      className={`relative overflow-hidden bg-white/10 backdrop-blur-md border border-white/10 ${rounded} ${className}`}
    >
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/15 to-transparent" />
    </div>
  );
}
