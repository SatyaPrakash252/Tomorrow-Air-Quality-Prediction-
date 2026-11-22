import React, { createContext, useContext, useState, useEffect } from 'react';
import { THEMES } from '../styles/themeTokens';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(() => {
    const saved = localStorage.getItem('weatherwise-theme');
    if (saved && (saved === 'dusk' || saved === 'storm')) return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'storm';
    }
    return 'dusk';
  });

  useEffect(() => {
    localStorage.setItem('weatherwise-theme', themeId);
    document.documentElement.setAttribute('data-theme', themeId);
    document.body.className = `theme-${themeId} antialiased selection:bg-amber-500/30 selection:text-amber-200 min-h-screen`;
  }, [themeId]);

  const toggleTheme = () => {
    setThemeId(prev => (prev === 'dusk' ? 'storm' : 'dusk'));
  };

  const currentTheme = THEMES[themeId] || THEMES.dusk;

  return (
    <ThemeContext.Provider value={{ theme: themeId, tokens: currentTheme, toggleTheme, setTheme: setThemeId }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
