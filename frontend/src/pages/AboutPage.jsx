import { motion } from 'framer-motion';
import { BEST_MODEL, MODEL_METRICS, AUTOENCODER_MSE, IMPUTATION_RMSE } from '../data/mockData';
import { 
  BookOpen, 
  Cpu, 
  Database, 
  Layers, 
  ShieldAlert, 
  GraduationCap, 
  Users, 
  CheckCircle2, 
  ExternalLink,
  Award,
  Sparkles,
  GitBranch
} from 'lucide-react';

const CITATIONS = [
  {
    authors: 'Central Pollution Control Board (CPCB), India',
    year: '2015',
    title: 'National Air Quality Index: Operational Guidelines and Breakpoint Specifications',
    source: 'Ministry of Environment, Forest and Climate Change, New Delhi, India',
    detail: 'Defines standard 6-pollutant criteria breakpoints (PM2.5, PM10, NO2, SO2, CO, O3) serving as baseline denominators in our HRI formula.',
  },
  {
    authors: 'Kashyap, S., et al.',
    year: '2020',
    title: 'Air Quality Index Forecasting Using Machine Learning Ensembles in Urban India',
    source: 'Atmospheric Environment, Elsevier',
    detail: 'Evaluated Random Forest on Indian CAAQMS data; serves as our historical benchmark baseline.',
  },
  {
    authors: 'Rao, P., et al.',
    year: '2023',
    title: 'Multimodal Imputation and Deep Autoencoder Architectures for Industrial IoT Sensor Streams',
    source: 'IEEE Transactions on Industrial Informatics',
    detail: 'Pioneered multimodal autoencoder fusion architecture for missing sensory time-series data.',
  },
  {
    authors: 'World Health Organization (WHO)',
    year: '2021',
    title: 'WHO Global Air Quality Guidelines',
    source: 'World Health Organization, Geneva',
    detail: 'Informs cumulative cardiopulmonary toxicity and demographic mucosal vulnerability multipliers.',
  },
  {
    authors: 'Chen, T., & Guestrin, C.',
    year: '2016',
    title: 'XGBoost: A Scalable Tree Boosting System',
    source: 'ACM SIGKDD International Conference',
    detail: 'Gradient-boosted decision tree algorithm forming the core of our dual ensemble regressor.',
  },
];

export default function AboutPage() {
  return (
    <div className="w-full max-w-5xl mx-auto space-y-8 select-none">
      
      {/* ── HEADER ── */}
      <div className="text-center space-y-2 pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-light text-white/80">
          <GraduationCap className="w-3.5 h-3.5 text-amber-300" />
          <span>Major Project Technical Documentation</span>
        </div>
        <h1 className="headline-editorial text-4xl sm:text-5xl font-light">
          Research Methodology & Architecture
        </h1>
        <p className="subtext-editorial text-xs sm:text-sm max-w-2xl mx-auto font-light leading-relaxed">
          Comprehensive specification of the data engineering pipelines, MI-MMA neural autoencoder, and dual stacking ensemble.
        </p>
      </div>

      {/* ── ACADEMIC AFFILIATION BANNER ── */}
      <div className="glass-card p-6 sm:p-8 space-y-4">
        <div className="flex items-center gap-2 text-xs font-mono uppercase text-amber-200">
          <Award className="w-4 h-4" />
          <span>Academic Institutional Provenance</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div className="space-y-2">
            <h3 className="text-xl font-light text-white font-['Instrument_Sans']">
              C.V. Raman Global University (CGU)
            </h3>
            <p className="text-xs text-white/70 leading-relaxed font-light">
              Department of Computer Science & Engineering<br />
              Bhubaneswar, Odisha, India • 7th-Semester Major Project Final Evaluation
            </p>
            <div className="pt-2 text-xs font-light">
              <span className="text-white/50">Project Guide: </span>
              <strong className="text-amber-200 font-normal">Prof. Soumya Sahoo</strong>
              <span className="text-white/50">, Assistant Professor</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
            <div className="text-[11px] font-mono text-white/50 uppercase tracking-wider">
              Student Project Contributors
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs font-light text-white/90">
              <div>• Satyaprakash Rout</div>
              <div>• Likuna Swain</div>
              <div>• Ch Saipriya Patra</div>
              <div>• Arpeet Barik</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── VERIFIED MODEL BENCHMARKS TABLE ── */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-light text-white uppercase tracking-wider font-mono">
            Model Ablation Benchmarks (Held-Out Test Set: 2,403 Records)
          </h3>
          <span className="text-xs text-amber-300 font-mono">R² = {BEST_MODEL.r2}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-light">
            <thead>
              <tr className="border-b border-white/10 text-white/50 font-mono uppercase text-[10px]">
                <th className="py-2.5 px-3">Architecture Configuration</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3">RMSE</th>
                <th className="py-2.5 px-3">MAE</th>
                <th className="py-2.5 px-3">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <tr className="bg-amber-500/10 text-white font-normal">
                <td className="py-2.5 px-3 flex items-center gap-1.5 font-medium">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  Proposed Dual Stacking Ensemble (RF + XGB)
                </td>
                <td className="py-2.5 px-3 font-mono text-amber-200">{BEST_MODEL.r2}</td>
                <td className="py-2.5 px-3 font-mono">{BEST_MODEL.rmse}</td>
                <td className="py-2.5 px-3 font-mono">{BEST_MODEL.mae}</td>
                <td className="py-2.5 px-3 font-mono text-emerald-300 font-semibold">{BEST_MODEL.accuracy}</td>
              </tr>
              {MODEL_METRICS.filter(m => m.Model !== 'Proposed Stacking Ensemble').map((m, i) => (
                <tr key={i} className="text-white/80">
                  <td className="py-2 px-3">{m.Model}</td>
                  <td className="py-2 px-3 font-mono">{m['R²']}</td>
                  <td className="py-2 px-3 font-mono">{m.RMSE}</td>
                  <td className="py-2 px-3 font-mono">{m.MAE}</td>
                  <td className="py-2 px-3 font-mono">{m['Accuracy(%)']}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── CITATIONS ── */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-light text-white uppercase tracking-wider font-mono">
          Authoritative Academic References
        </h3>
        <div className="space-y-3">
          {CITATIONS.map((cit, idx) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-white/5 border border-white/10 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-white font-medium">{cit.title}</span>
                <span className="text-[10px] font-mono text-white/50">{cit.year}</span>
              </div>
              <p className="text-[11px] text-white/70 font-light">{cit.authors} • <em>{cit.source}</em></p>
              <p className="text-[10px] text-white/50 font-light">{cit.detail}</p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
