import { motion } from 'framer-motion';
import { getTierColor } from '../data/mockData';
import { 
  Users, 
  Baby, 
  HeartPulse, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert,
  Flame,
  ArrowUpRight
} from 'lucide-react';

const GROUP_CONFIG = {
  'General Public': {
    icon: Users,
    badgeText: 'Standard Cohort (Vg = 1.0)',
  },
  'Children/Elderly': {
    icon: Baby,
    badgeText: 'Pediatric / Geriatric (Vg = 1.3)',
  },
  'Respiratory Patients': {
    icon: HeartPulse,
    badgeText: 'Cardiopulmonary Vulnerable (Vg = 1.6)',
  }
};

const TIER_CONFIG = {
  LOW: {
    guidance: 'Ambient air poses minimal clinical hazard. Normal outdoor exercise and ventilation advised.',
    badgeBg: 'bg-emerald-500/20 text-emerald-200 border-emerald-500/30',
  },
  MODERATE: {
    guidance: 'Sensitive individuals should limit strenuous outdoor exertion. Monitor respiratory symptoms.',
    badgeBg: 'bg-amber-500/20 text-amber-200 border-amber-500/30',
  },
  HIGH: {
    guidance: 'Significant biological stress. Wear certified N95 masks outdoors and keep residential windows closed.',
    badgeBg: 'bg-orange-500/20 text-orange-200 border-orange-500/30',
  },
  SEVERE: {
    guidance: 'Public Health Emergency. Avoid ALL outdoor exposure. Run HEPA air purifiers continuously.',
    badgeBg: 'bg-rose-500/25 text-rose-200 border-rose-500/40',
  }
};

export default function RiskCard({ group, hriValue, tier, factor, index = 0 }) {
  const groupInfo = GROUP_CONFIG[group] || GROUP_CONFIG['General Public'];
  const GroupIcon = groupInfo.icon;
  const tierInfo = TIER_CONFIG[tier] || TIER_CONFIG['MODERATE'];
  const isSevere = tier === 'SEVERE';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={`glass-card p-5 relative overflow-hidden transition-all duration-300 ${
        isSevere ? 'border-rose-400/40 shadow-xl' : 'glass-card-hover'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-white">
            <GroupIcon className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-light text-white font-['Instrument_Sans']">
              {group}
            </h4>
            <span className="text-[10px] text-white/60 font-mono">
              {groupInfo.badgeText}
            </span>
          </div>
        </div>

        {/* Tier Badge */}
        <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold uppercase border ${tierInfo.badgeBg}`}>
          {tier}
        </span>
      </div>

      {/* HRI Value display */}
      <div className="my-3 flex items-baseline gap-2">
        <span className="text-3xl font-extralight text-white font-['Instrument_Sans']">
          {hriValue}
        </span>
        <span className="text-xs text-white/50 font-mono">
          HRI Exposure Score
        </span>
      </div>

      {/* Clinical Guidance Text */}
      <p className="text-xs text-white/80 font-light leading-relaxed pt-2 border-t border-white/10">
        {tierInfo.guidance}
      </p>
    </motion.div>
  );
}
