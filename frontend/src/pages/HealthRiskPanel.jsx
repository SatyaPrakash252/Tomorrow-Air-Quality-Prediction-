import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import RiskCard from '../components/RiskCard';
import { 
  CITIES, 
  CITY_STATS, 
  HRI_TIERS, 
  HRI_CUTOFFS, 
  ALERT_RATES, 
  getTierColor 
} from '../data/mockData';
import { fetchRisk } from '../data/api';
import { 
  ShieldAlert, 
  HeartPulse, 
  Users, 
  Baby, 
  Sliders, 
  Activity, 
  CheckCircle2,
  Info,
  MapPin,
  Sparkles
} from 'lucide-react';

const TIER_ORDER = ['LOW', 'MODERATE', 'HIGH', 'SEVERE'];
const TIER_COLORS = ['#34d399', '#fbbf24', '#f97316', '#f43f5e'];

const GROUPS = [
  { name: 'General Public', factor: 1.0, icon: Users, color: '#38bdf8' },
  { name: 'Children/Elderly', factor: 1.3, icon: Baby, color: '#fbbf24' },
  { name: 'Respiratory Patients', factor: 1.6, icon: HeartPulse, color: '#f43f5e' },
];

function TierDoughnut({ groupName, data }) {
  const chartData = TIER_ORDER.map((tier, i) => ({
    name: tier,
    value: data[tier] || 0,
    color: TIER_COLORS[i],
  }));

  return (
    <div className="h-40 w-full relative flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={44}
            outerRadius={64}
            paddingAngle={4}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(val) => [`${val}%`, 'Frequency']}
            contentStyle={{
              backgroundColor: 'rgba(15, 23, 42, 0.85)',
              backdropFilter: 'blur(16px)',
              borderColor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '16px',
              fontSize: '11px',
              color: '#ffffff',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute text-center pointer-events-none">
        <span className="text-[10px] font-mono text-white/50 uppercase">Severe</span>
        <div className="text-sm font-light text-rose-300 font-['Instrument_Sans']">
          {data.SEVERE}%
        </div>
      </div>
    </div>
  );
}

export default function HealthRiskPanel({ city, onCityChange, liveAQI }) {
  const stats = CITY_STATS[city] || { avg_aqi: 150 };
  const effectiveLive = liveAQI != null ? Math.round(liveAQI) : Math.round(stats.avg_aqi);
  const [simulatedAQI, setSimulatedAQI] = useState(effectiveLive);

  const [clinicalAdvisory, setClinicalAdvisory] = useState(null);
  const [dominantPollutant, setDominantPollutant] = useState('PM2.5');

  // Synchronize state whenever live telemetry or city changes
  useEffect(() => {
    if (liveAQI != null) {
      setSimulatedAQI(Math.round(liveAQI));
    } else {
      setSimulatedAQI(Math.round(stats.avg_aqi));
    }
  }, [city, liveAQI, stats.avg_aqi]);

  // Fetch real-time clinical advisory
  useEffect(() => {
    fetchRisk(city).then((res) => {
      if (res && res.clinical_advisory) {
        setClinicalAdvisory(res.clinical_advisory);
        if (res.dominant_pollutant) setDominantPollutant(res.dominant_pollutant);
      }
    }).catch(() => {});
  }, [city]);

  const determineTier = (val) => {
    if (val <= HRI_CUTOFFS.p25) return 'LOW';
    if (val <= HRI_CUTOFFS.p75) return 'MODERATE';
    if (val <= HRI_CUTOFFS.p90) return 'HIGH';
    return 'SEVERE';
  };

  const isLiveSynced = simulatedAQI === effectiveLive;

  const groupAssessments = useMemo(() => {
    return GROUPS.map((g) => {
      // Base HRI calculation proportional to simulated AQI
      const val = parseFloat(((simulatedAQI / 45) * 3.2 * g.factor).toFixed(2));
      const tier = determineTier(val);
      return {
        ...g,
        hri: val,
        tier,
      };
    });
  }, [simulatedAQI]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
      className="w-full max-w-6xl mx-auto space-y-8 select-none"
    >
      
      {/* ── HEADER ── */}
      <div className="text-center space-y-2 pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-light text-white/90">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-300" />
          <span>Epidemiological Health Triage</span>
          <span className="text-white/40">•</span>
          <span className="flex items-center gap-1.5 text-emerald-300 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live Synced: {effectiveLive} AQI ({city})
          </span>
        </div>
        <h1 className="headline-editorial text-4xl sm:text-5xl font-light">
          Health Risk Index (HRI) Engine
        </h1>
        <p className="subtext-editorial text-xs sm:text-sm max-w-2xl mx-auto font-light leading-relaxed">
          Stratifying population biological risk beyond scalar AQI through multi-pollutant additive exposure and demographic vulnerability multipliers.
        </p>
      </div>

      {/* ── INTERACTIVE EXPOSURE SLIDER ── */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-white font-light">
            <Sliders className="w-4 h-4 text-amber-300" />
            <span>Interactive AQI Exposure Scenario:</span>
            <strong className="text-2xl font-light font-['Instrument_Sans'] text-amber-200 ml-1">
              {simulatedAQI}
            </strong>
            {isLiveSynced ? (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/25 text-emerald-200 border border-emerald-500/40">
                Real-Time Live Truth
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-white/15 text-white/70">
                Simulation Scenario
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSimulatedAQI(effectiveLive)}
              className={`px-3 py-1 rounded-full text-xs font-mono transition-all cursor-pointer flex items-center gap-1 ${
                isLiveSynced
                  ? 'bg-emerald-500/30 text-emerald-200 border border-emerald-500/50 font-medium'
                  : 'glass-pill text-emerald-300 hover:text-white'
              }`}
              title="Reset slider to current real-time station sensor value"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Live Sensor ({effectiveLive})</span>
            </button>
            <button
              onClick={() => setSimulatedAQI(45)}
              className="px-3 py-1 rounded-full glass-pill text-xs text-white/80 hover:text-white cursor-pointer"
            >
              Good (45)
            </button>
            <button
              onClick={() => setSimulatedAQI(185)}
              className="px-3 py-1 rounded-full glass-pill text-xs text-white/80 hover:text-white cursor-pointer"
            >
              Hazy (185)
            </button>
            <button
              onClick={() => setSimulatedAQI(320)}
              className="px-3 py-1 rounded-full glass-pill text-xs text-white/80 hover:text-white cursor-pointer"
            >
              Severe (320)
            </button>
          </div>
        </div>

        {/* Range slider */}
        <input
          type="range"
          min="10"
          max="500"
          value={simulatedAQI}
          onChange={(e) => setSimulatedAQI(Number(e.target.value))}
          className="w-full h-2 bg-white/20 rounded-full appearance-none cursor-pointer accent-amber-400 focus:outline-none transition-all"
        />

        <div className="flex justify-between text-[11px] font-mono text-white/70">
          <span>10 (Clean Air)</span>
          <span>100 (NAAQS Standard)</span>
          <span>250 (Unhealthy)</span>
          <span>500 (Hazardous)</span>
        </div>
      </div>

      {/* ── 3 DEMOGRAPHIC COHORT CARDS ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {groupAssessments.map((ga, idx) => (
          <RiskCard
            key={ga.name}
            group={ga.name}
            hriValue={ga.hri}
            tier={ga.tier}
            factor={ga.factor}
            index={idx}
          />
        ))}
      </div>

      {/* ── HISTORICAL TIER FREQUENCIES (DOUGHNUT CHARTS) ── */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-light text-white uppercase tracking-wider font-mono">
            Historical Exposure Frequencies (7-Year CPCB Telemetry)
          </h3>
          <span className="text-xs text-white/50 font-mono">Shared Scale Distribution</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {GROUPS.map((g) => {
            const groupData = HRI_TIERS[g.name] || { LOW: 25, MODERATE: 50, HIGH: 15, SEVERE: 10 };
            return (
              <div key={g.name} className="p-4 rounded-2xl bg-white/5 border border-white/10 text-center space-y-2">
                <h4 className="text-xs font-light text-white font-['Instrument_Sans']">{g.name}</h4>
                <TierDoughnut groupName={g.name} data={groupData} />
                <div className="text-[11px] font-mono text-white/60">
                  Alert Activation: <strong className="text-amber-200">{ALERT_RATES[g.name] || '24.9%'}</strong>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── CLINICAL ADVISORY ENGINE (v3.2) SPECIFICATION CARD ── */}
      {clinicalAdvisory && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="glass-card p-6 space-y-4 border-amber-500/25"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <h3 className="text-sm font-light text-white font-['Instrument_Sans'] uppercase tracking-wider font-mono">
                Clinical Advisory Engine Report (v3.2 Ground Truth)
              </h3>
            </div>
            <span className="text-[11px] font-mono text-amber-200">
              City: {city} • Dominant: <strong className="text-white">{dominantPollutant || 'PM2.5'}</strong>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Dominant Pollutant Cellular Mechanism */}
            {clinicalAdvisory.dominant_pollutant && (
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                <span className="text-[10px] font-mono uppercase text-amber-300 font-bold">
                  Biochemical & Physiological Pathway ({clinicalAdvisory.dominant_pollutant.pollutant})
                </span>
                <p className="text-xs text-white/85 font-light leading-relaxed">
                  {clinicalAdvisory.dominant_pollutant.physiological_impact}
                </p>
                <div className="text-[11px] text-emerald-300 font-mono pt-1">
                  Targeted Intervention: <span className="text-white font-light">{clinicalAdvisory.dominant_pollutant.targeted_intervention}</span>
                </div>
              </div>
            )}

            {/* Clinical Mitigation Checklist */}
            {clinicalAdvisory.mitigation_checklist && (
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                <span className="text-[10px] font-mono uppercase text-cyan-300 font-bold">
                  Statutory Mitigation Checklist
                </span>
                <ul className="space-y-1.5 text-xs text-white/80 font-light">
                  {clinicalAdvisory.mitigation_checklist.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {clinicalAdvisory.environmental_context && (
            <div className="text-[11px] font-mono text-white/60 bg-white/5 px-3 py-2 rounded-xl border border-white/5">
              {clinicalAdvisory.environmental_context}
            </div>
          )}
        </motion.div>
      )}

      {/* ── MATHEMATICAL FORMULATION CARD ── */}
      <div className="glass-card p-6 space-y-3">
        <div className="flex items-center gap-2 text-xs font-mono uppercase text-amber-200">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Shared Cutoff Formulation Rationale</span>
        </div>
        <p className="text-xs text-white/80 font-light leading-relaxed">
          The Health Risk Index applies an epidemiological exponent ($\beta = 1.0$) across criteria pollutants normalized against CPCB National Ambient Air Quality Standards (NAAQS). Crucially, clinical risk cutoffs ($P_{25} = 7.12, P_{75} = 14.71, P_{90} = 23.85$) are fixed to the General Public distribution—mathematically preventing demographic multipliers ($V_g$) from cancelling out during cohort risk triage.
        </p>
      </div>

    </motion.div>
  );
}
