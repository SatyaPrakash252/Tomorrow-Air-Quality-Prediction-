import React, { useEffect, useRef } from 'react';
import { useMotionValue, useSpring, useTransform, motion } from 'framer-motion';

/**
 * AnimatedNumber.jsx
 * ──────────────────
 * Ultra-smooth spring-interpolated number counter component.
 * Uses Framer Motion's spring physics to fluidly glide between numbers
 * without jarring text snap, providing an Apple-grade fluid animation.
 */
export default function AnimatedNumber({
  value = 0,
  formatter = (v) => Math.round(v),
  suffix = '',
  className = '',
  springConfig = { stiffness: 95, damping: 18, mass: 0.6 }
}) {
  const parsed = typeof value === 'number' ? value : parseFloat(value);
  const numericVal = Number.isFinite(parsed) ? parsed : 0;
  const motionVal = useMotionValue(numericVal);
  const springVal = useSpring(motionVal, springConfig);
  const displayVal = useTransform(springVal, (current) => `${formatter(current)}${suffix}`);
  
  const spanRef = useRef(null);

  useEffect(() => {
    motionVal.set(numericVal);
  }, [numericVal, motionVal]);

  // Subscribe to string changes for zero-re-render high performance
  useEffect(() => {
    const unsubscribe = displayVal.on('change', (latest) => {
      if (spanRef.current) {
        spanRef.current.textContent = latest;
      }
    });
    return () => unsubscribe();
  }, [displayVal]);

  return (
    <span ref={spanRef} className={className}>
      {formatter(numericVal)}{suffix}
    </span>
  );
}
