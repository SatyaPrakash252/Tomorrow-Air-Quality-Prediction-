/**
 * themeTokens.js
 * ──────────────
 * Authoritative design tokens for the WeatherWise atmospheric design system.
 * Implements Dusk and Storm themes matching the reference screenshots.
 */

export const THEMES = {
  dusk: {
    id: 'dusk',
    name: 'Dusk Glow',
    outerBg: '#cfd4ce', // Soft neutral canvas outside the 32px container
    skyImage: '/backgrounds/sky-dusk.jpg',
    skyFallback: 'radial-gradient(ellipse at 85% 90%, rgba(245, 158, 11, 0.45) 0%, rgba(180, 83, 9, 0.25) 30%, transparent 65%), linear-gradient(135deg, #475569 0%, #64748b 40%, #78716c 70%, #44403c 100%)',
    headlineText: '#fef3c7', // Warm cream — visible on dark gradients
    headlineTextMuted: '#fde68a',
    bodyText: '#f8fafc',
    subText: 'rgba(255, 255, 255, 0.78)',
    heroNumber: '#ffffff',
    activeMarker: '#ffffff',
    inactiveMarker: 'rgba(255, 255, 255, 0.4)',
    glassPanelBg: 'rgba(255, 255, 255, 0.14)',
    glassPanelBorder: 'rgba(255, 255, 255, 0.25)',
    glassCardBg: 'rgba(255, 255, 255, 0.10)',
    glassCardBorder: 'rgba(255, 255, 255, 0.18)',
    glassPillBg: 'rgba(255, 255, 255, 0.16)',
    glassPillBorder: 'rgba(255, 255, 255, 0.25)',
    accentAmber: '#d97706',
    accentGold: '#f59e0b',
    timelineLine: 'rgba(255, 255, 255, 0.65)',
    timelineGlow: 'rgba(255, 255, 255, 0.95)',
  },
  storm: {
    id: 'storm',
    name: 'Storm Charcoal',
    outerBg: '#13161c', // Deep neutral canvas outside container
    skyImage: '/backgrounds/sky-storm.jpg',
    skyFallback: 'radial-gradient(ellipse at 50% 85%, rgba(245, 158, 11, 0.40) 0%, rgba(180, 83, 9, 0.2) 30%, transparent 60%), linear-gradient(145deg, #0f172a 0%, #1e293b 45%, #334155 75%, #1e1e24 100%)',
    headlineText: '#e2e8f0', // Light grey — visible on dark bg
    headlineTextMuted: '#cbd5e1',
    bodyText: '#f1f5f9',
    subText: 'rgba(226, 232, 240, 0.80)',
    heroNumber: '#ffffff',
    activeMarker: '#ffffff',
    inactiveMarker: 'rgba(255, 255, 255, 0.35)',
    glassPanelBg: 'rgba(15, 23, 42, 0.42)',
    glassPanelBorder: 'rgba(255, 255, 255, 0.15)',
    glassCardBg: 'rgba(15, 23, 42, 0.30)',
    glassCardBorder: 'rgba(255, 255, 255, 0.12)',
    glassPillBg: 'rgba(255, 255, 255, 0.10)',
    glassPillBorder: 'rgba(255, 255, 255, 0.18)',
    accentAmber: '#f59e0b',
    accentGold: '#fbbf24',
    timelineLine: 'rgba(255, 255, 255, 0.60)',
    timelineGlow: 'rgba(255, 255, 255, 0.95)',
  }
};
