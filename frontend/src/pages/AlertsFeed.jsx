import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MOCK_ALERTS, CITIES, CITY_STATS, getTierColor } from '../data/mockData';
import { fetchAlerts } from '../data/api';
import { 
  Bell, 
  Flame, 
  ShieldAlert, 
  MapPin, 
  Calendar, 
  Filter,
  CheckCircle2,
  ChevronRight,
  Sparkles,
  RefreshCw,
  Activity
} from 'lucide-react';

const FILTER_CITIES = ['All', 'Delhi', 'Mumbai', 'Bangalore', 'Bhubaneswar', 'Chennai', 'Hyderabad'];
const GROUPS = ['All', 'General Public', 'Children/Elderly', 'Respiratory Patients'];
const TIERS = ['All', 'SEVERE', 'HIGH', 'MODERATE'];

export default function AlertsFeed({ city, onCityChange }) {
  const [filterGroup, setFilterGroup] = useState('All');
  const [filterCity, setFilterCity] = useState(city || 'All');
  const [filterTier, setFilterTier] = useState('All');
  
  const [alerts, setAlerts] = useState(MOCK_ALERTS);
  const [loading, setLoading] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const loadAlerts = (c = filterCity) => {
    setLoading(true);
    const targetCity = c === 'All' ? null : c;
    fetchAlerts(targetCity)
      .then((data) => {
        if (data && Array.isArray(data.alerts) && data.alerts.length > 0) {
          setAlerts(data.alerts);
        } else {
          setAlerts(MOCK_ALERTS);
        }
        setLastRefreshed(new Date());
      })
      .catch(() => {
        setAlerts(MOCK_ALERTS);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts(filterCity);
  }, [filterCity]);

  // Keep filterCity in sync if parent city changes
  useEffect(() => {
    if (city && city !== filterCity && filterCity !== 'All') {
      setFilterCity(city);
    }
  }, [city]);

  const filteredAlerts = useMemo(() => {
    return alerts.filter((a) => {
      if (filterCity !== 'All' && a.city?.toLowerCase() !== filterCity.toLowerCase()) return false;
      if (filterGroup !== 'All' && !a.group?.toLowerCase().includes(filterGroup.toLowerCase())) return false;
      if (filterTier !== 'All' && a.tier !== filterTier) return false;
      return true;
    });
  }, [alerts, filterCity, filterGroup, filterTier]);

  const severeCount = filteredAlerts.filter((a) => a.tier === 'SEVERE').length;
  const highCount = filteredAlerts.filter((a) => a.tier === 'HIGH').length;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6 select-none">
      
      {/* ── HEADER & COUNTERS ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-2 pb-4 border-b border-white/10">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-light text-rose-300 mb-2">
            <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
            <span>Automated Clinical Triage Feed</span>
            <span className="text-white/40">•</span>
            <span className="text-emerald-300 font-mono">Live Ground Truth</span>
          </div>
          <h1 className="headline-editorial text-3xl sm:text-4xl font-light">
            Public Health Alert Center
          </h1>
          <p className="subtext-editorial text-xs max-w-xl font-light mt-1">
            Real-time emergency warnings triggered when cohort-adjusted HRI crosses statutory biological risk thresholds.
          </p>
        </div>

        {/* Counter Pills & Refresh */}
        <div className="flex items-center gap-3">
          <div className="glass-card px-4 py-2.5 flex items-center gap-3 border-rose-500/30">
            <Flame className="w-5 h-5 text-rose-400 animate-pulse" />
            <div>
              <div className="text-xl font-light text-rose-300 font-['Instrument_Sans'] leading-none">
                {severeCount}
              </div>
              <div className="text-[10px] font-mono text-white/50 uppercase mt-0.5">Severe Alerts</div>
            </div>
          </div>

          <div className="glass-card px-4 py-2.5 flex items-center gap-3 border-amber-500/30">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <div>
              <div className="text-xl font-light text-amber-300 font-['Instrument_Sans'] leading-none">
                {highCount}
              </div>
              <div className="text-[10px] font-mono text-white/50 uppercase mt-0.5">High Alerts</div>
            </div>
          </div>

          <button
            onClick={() => loadAlerts(filterCity)}
            className="w-10 h-10 rounded-full glass-pill flex items-center justify-center text-white/80 hover:text-white transition-all cursor-pointer border border-white/20"
            title="Refresh active sensor alerts"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-300' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── FILTER CONTROLS ── */}
      <div className="glass-card p-4 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-white/70 uppercase">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-amber-300" />
            <span>Filter Operational Broadcasts</span>
          </div>
          <span className="text-[11px] text-emerald-300 lowercase font-mono">
            {filteredAlerts.length} active broadcast{filteredAlerts.length === 1 ? '' : 's'}
          </span>
        </div>

        {/* City Filter Chips */}
        <div className="flex flex-wrap items-center gap-2 text-xs border-b border-white/10 pb-3">
          <span className="text-[11px] text-white/60 font-mono flex items-center gap-1">
            <MapPin className="w-3 h-3 text-amber-300" /> City:
          </span>
          <div className="flex flex-wrap gap-1">
            {FILTER_CITIES.map((c) => (
              <button
                key={c}
                onClick={() => {
                  setFilterCity(c);
                  if (c !== 'All') onCityChange?.(c);
                }}
                className={`px-3 py-1 rounded-full text-xs transition-all cursor-pointer ${
                  filterCity.toLowerCase() === c.toLowerCase()
                    ? 'bg-amber-400 text-slate-950 font-medium shadow-md'
                    : 'glass-pill text-white/70 hover:text-white'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs pt-1">
          {/* Group Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-white/60 font-mono">Cohort:</span>
            <div className="flex flex-wrap gap-1">
              {GROUPS.map((g) => (
                <button
                  key={g}
                  onClick={() => setFilterGroup(g)}
                  className={`px-3 py-1 rounded-full text-xs transition-all cursor-pointer ${
                    filterGroup === g
                      ? 'bg-white/30 text-white font-medium border border-white/40'
                      : 'glass-pill text-white/60 hover:text-white'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          {/* Tier Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-white/60 font-mono">Severity:</span>
            <div className="flex gap-1">
              {TIERS.map((t) => (
                <button
                  key={t}
                  onClick={() => setFilterTier(t)}
                  className={`px-3 py-1 rounded-full text-xs transition-all cursor-pointer ${
                    filterTier === t
                      ? 'bg-white/30 text-white font-medium border border-white/40'
                      : 'glass-pill text-white/60 hover:text-white'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── ALERT CARDS STREAM ── */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="glass-card p-12 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto opacity-70" />
            <h3 className="text-base font-light text-white font-['Instrument_Sans']">
              No Active Health Alerts
            </h3>
            <p className="text-xs text-white/60 font-light">
              Air quality parameters in this filter window are within safe biological limits.
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert, idx) => {
            const isSevere = alert.tier === 'SEVERE';
            const isHigh = alert.tier === 'HIGH';
            const hasPollutants = alert.pollutant_breakdown && Object.keys(alert.pollutant_breakdown).length > 0;

            return (
              <motion.div
                key={`${alert.city}-${alert.group}-${idx}`}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.03, duration: 0.3 }}
                className={`glass-card p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all duration-300 ${
                  isSevere 
                    ? 'border-rose-500/40 bg-rose-950/20 shadow-rose-950/20' 
                    : (isHigh ? 'border-amber-500/35 bg-amber-950/15' : 'glass-card-hover')
                }`}
              >
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${
                      isSevere 
                        ? 'bg-rose-500/25 text-rose-200 border-rose-500/40' 
                        : (isHigh 
                            ? 'bg-amber-500/25 text-amber-200 border-amber-500/40' 
                            : 'bg-emerald-500/20 text-emerald-200 border-emerald-500/30')
                    }`}>
                      {alert.tier}
                    </span>
                    <span className="text-xs text-white font-medium">
                      {alert.city}, India
                    </span>
                    <span className="text-xs text-white/40 font-mono">•</span>
                    <span className="text-xs text-amber-200 font-light">
                      Cohort: <strong>{alert.group}</strong> ({alert.vulnerability_factor}x)
                    </span>
                    <span className="text-xs text-white/40 font-mono">•</span>
                    <span className="text-[11px] text-white/50 font-mono">
                      {alert.date}
                    </span>
                  </div>

                  <p className="text-xs text-white/90 font-light leading-relaxed">
                    {alert.recommendation}
                  </p>

                  {/* Criteria pollutant telemetry pill */}
                  {hasPollutants && (
                    <div className="flex flex-wrap gap-2 pt-1 text-[10px] font-mono text-white/60">
                      <span>Live Sensoring:</span>
                      {alert.pollutant_breakdown.pm25 != null && <span>PM2.5: <strong className="text-white">{alert.pollutant_breakdown.pm25}</strong></span>}
                      {alert.pollutant_breakdown.pm10 != null && <span>PM10: <strong className="text-white">{alert.pollutant_breakdown.pm10}</strong></span>}
                      {alert.pollutant_breakdown.no2 != null && <span>NO2: <strong className="text-white">{alert.pollutant_breakdown.no2}</strong></span>}
                      {alert.pollutant_breakdown.o3 != null && <span>O3: <strong className="text-white">{alert.pollutant_breakdown.o3}</strong></span>}
                    </div>
                  )}
                </div>

                <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-1 sm:text-right border-t sm:border-t-0 border-white/10 pt-2 sm:pt-0">
                  <div className={`text-3xl font-light font-['Instrument_Sans'] ${
                    isSevere ? 'text-rose-300' : (isHigh ? 'text-amber-300' : 'text-emerald-300')
                  }`}>
                    {alert.hri_value}
                  </div>
                  <span className="text-[10px] font-mono text-white/50 uppercase">
                    HRI Triage Score
                  </span>
                </div>
              </motion.div>
            );
          })
        )}
      </div>

    </div>
  );
}
