import { useState, useMemo } from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wind, 
  Activity, 
  ShieldAlert, 
  Bell, 
  BookOpen, 
  MapPin, 
  ChevronDown, 
  Sparkles,
  Search,
  Sun,
  Moon,
  Menu,
  X
} from 'lucide-react';
import { CITIES, CITY_STATS, getAQICategory } from '../data/mockData';
import { useTheme } from '../context/ThemeContext';
import AnimatedNumber from './AnimatedNumber';

export default function Navbar({ selectedCity, onCityChange, liveAQI }) {
  const { theme, toggleTheme } = useTheme();
  const [cityDropdownOpen, setCityDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCities = useMemo(() => {
    if (!searchTerm.trim()) return CITIES;
    const q = searchTerm.toLowerCase();
    return CITIES.filter((c) => {
      const s = CITY_STATS[c] || {};
      return (
        c.toLowerCase().includes(q) ||
        (s.state && s.state.toLowerCase().includes(q)) ||
        (s.region && s.region.toLowerCase().includes(q))
      );
    });
  }, [searchTerm]);

  const navItems = [
    { to: '/', label: 'Overview', icon: Wind },
    { to: '/dashboard', label: 'Forecast', icon: Activity },
    { to: '/risk', label: 'Health Risk', icon: ShieldAlert },
    { to: '/alerts', label: 'Alerts', icon: Bell },
    { to: '/about', label: 'Research', icon: BookOpen },
  ];

  const currentStats = CITY_STATS[selectedCity] || { avg_aqi: 150 };
  const effectiveAQI = liveAQI != null ? Math.round(liveAQI) : Math.round(currentStats.avg_aqi);
  const currentCat = getAQICategory(effectiveAQI);

  return (
    <header className="fixed top-3 left-0 right-0 z-50 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto pointer-events-none">
      <div className="glass-panel px-4 sm:px-6 h-16 sm:h-18 rounded-full flex items-center justify-between gap-4 pointer-events-auto border border-white/20 shadow-lg backdrop-blur-2xl">
        
        {/* Brand Logo */}
        <NavLink to="/" className="flex items-center gap-3 group text-decoration-none select-none">
          <div className="w-9 h-9 rounded-full bg-white/15 border border-white/25 flex items-center justify-center shadow-inner group-hover:bg-white/25 transition-all">
            <Wind className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-light text-lg sm:text-xl tracking-tight text-white font-['Instrument_Sans']">
                WeatherWise
              </span>
              <span className="text-[10px] uppercase font-mono tracking-wider px-1.5 py-0.5 rounded-full bg-white/15 text-white/80 border border-white/20">
                AI 2.0
              </span>
            </div>
          </div>
        </NavLink>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-white/5 p-1 rounded-full border border-white/10">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => `
                  flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-light tracking-wide transition-all duration-200 cursor-pointer
                  ${isActive 
                    ? 'text-white bg-white/25 font-normal shadow-sm border border-white/25' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                  }
                `}
              >
                <Icon className="w-3.5 h-3.5 opacity-80" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Right Controls: Location Finder, Live AQI Pill, and Theme Switcher */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Theme Toggle (Dusk vs Storm) */}
          <button
            onClick={toggleTheme}
            className="w-9 h-9 rounded-full glass-pill flex items-center justify-center text-white/90 hover:text-white hover:scale-105 transition-all cursor-pointer"
            title={`Switch to ${theme === 'dusk' ? 'Storm' : 'Dusk'} theme`}
          >
            {theme === 'dusk' ? (
              <Moon className="w-4 h-4 text-amber-200" />
            ) : (
              <Sun className="w-4 h-4 text-amber-300" />
            )}
          </button>

          {/* Quick City Dropdown Button */}
          <div className="relative">
            <button
              onClick={() => setCityDropdownOpen(!cityDropdownOpen)}
              className="px-3.5 py-1.5 rounded-full glass-pill flex items-center gap-2 text-xs font-light text-white/95 hover:bg-white/20 transition-all cursor-pointer"
            >
              <MapPin className="w-3.5 h-3.5 text-amber-300" />
              <span className="hidden sm:inline font-normal">{selectedCity}</span>
              <ChevronDown className={`w-3 h-3 text-white/60 transition-transform ${cityDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* City Search Dropdown Modal */}
            <AnimatePresence>
              {cityDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.96 }}
                  className="absolute right-0 mt-3 w-72 rounded-2xl glass-card p-3 shadow-2xl border border-white/20 z-50 backdrop-blur-3xl bg-slate-900/85"
                >
                  <div className="relative mb-2">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-white/50" />
                    <input
                      type="text"
                      placeholder="Search 38 cities..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl bg-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-1 focus:ring-amber-400 border border-white/10"
                    />
                  </div>
                  <div className="max-h-56 overflow-y-auto space-y-1 pr-1">
                    {filteredCities.map((c) => (
                      <button
                        key={c}
                        onClick={() => {
                          onCityChange(c);
                          setCityDropdownOpen(false);
                          setSearchTerm('');
                        }}
                        className={`w-full text-left px-3 py-1.5 rounded-xl text-xs flex items-center justify-between transition-colors cursor-pointer ${
                          c === selectedCity ? 'bg-amber-500/25 text-white font-medium' : 'text-white/80 hover:bg-white/10'
                        }`}
                      >
                        <span>{c}</span>
                        <span className="text-[10px] font-mono text-white/40">
                          {CITY_STATS[c]?.state || 'India'}
                        </span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Live AQI Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full glass-pill text-xs font-mono">
            <span className="w-2 h-2 rounded-full animate-pulse bg-emerald-400" />
            <span className="text-white/70">AQI</span>
            <AnimatedNumber value={effectiveAQI} className="font-semibold text-white" />
          </div>

          {/* Mobile Menu Hamburger Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden w-9 h-9 rounded-full glass-pill flex items-center justify-center text-white/90 hover:text-white transition-all cursor-pointer"
            title="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>

        </div>

      </div>

      {/* Mobile Navigation Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className="md:hidden mt-2 p-3 rounded-2xl glass-card border border-white/20 shadow-2xl backdrop-blur-3xl bg-slate-900/90 pointer-events-auto space-y-1"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-light tracking-wide transition-colors
                    ${isActive 
                      ? 'text-white bg-white/20 font-medium' 
                      : 'text-white/80 hover:bg-white/10'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 text-amber-300" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
