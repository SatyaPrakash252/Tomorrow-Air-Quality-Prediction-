"""
advisories.py
─────────────
Versioned Clinical NLG Advisory Engine and Structured Health Risk Schemas.
Translates multi-pollutant concentrations and TreeSHAP attribution into
clinically rigorous, demographic-specific public health advisories based on
CPCB NAQI guidelines and WHO 2021 Air Quality Criteria.

Includes:
- Strict Pydantic schemas with auto-repair fallback
- Demographic cohort action plans (General Public, Children/Elderly, Respiratory Patients)
- Dominant pollutant physiological impact attribution
- Actionable indoor/outdoor mitigation protocols
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ValidationError
import logging

logger = logging.getLogger(__name__)

# ── CPCB Breakpoints and WHO Clinical Baselines ──────────────────────────
POLLUTANT_CLINICAL_PROFILES = {
    "PM2.5": {
        "full_name": "Fine Particulate Matter (PM2.5)",
        "mechanism": "Penetrates deep into alveolar air sacs and systemic circulation, inducing oxidative stress, microvascular endothelial dysfunction, and acute bronchospasm.",
        "primary_risks": ["Acute asthma exacerbation", "Cardiovascular ischemic stress", "Decreased peak expiratory flow"],
        "remedy": "True HEPA (H13) filtration, N95/FFP2 respirator masks with snug facial seal, minimize heavy cardiovascular exertion."
    },
    "PM10": {
        "full_name": "Coarse Particulate Matter (PM10)",
        "mechanism": "Deposits in the upper tracheobronchial tree, triggering mucociliary irritation, persistent coughing, and chronic bronchitis flare-ups.",
        "primary_risks": ["Nasopharyngeal irritation", "Chronic bronchitis flares", "Sinus mucosal congestion"],
        "remedy": "Wet mopping indoors, closed windows, protective barrier masks outdoors."
    },
    "NO2": {
        "full_name": "Nitrogen Dioxide (NO2)",
        "mechanism": "Combustion byproduct causing severe airway hyper-responsiveness, bronchial mucosal inflammation, and heightened allergen sensitivity.",
        "primary_risks": ["Bronchial spasm in asthmatics", "Childhood wheezing", "Increased vulnerability to viral respiratory tract infections"],
        "remedy": "Avoid major arterial roadways during peak traffic hours; ensure cross-ventilation only when outdoor traffic diminishes."
    },
    "SO2": {
        "full_name": "Sulphur Dioxide (SO2)",
        "mechanism": "Water-soluble gas causing rapid reflex bronchoconstriction within 5 minutes of exposure in hyper-reactive airways.",
        "primary_risks": ["Sudden chest tightness in asthmatics", "Reflex bronchoconstriction", "Severe ocular stinging"],
        "remedy": "Remain indoors in sealed rooms; asthmatic individuals should carry rescue short-acting beta-agonists (SABA)."
    },
    "O3": {
        "full_name": "Ground-Level Ozone (O3)",
        "mechanism": "Strong photochemical oxidant inducing airway epithelial cellular necrosis, chest discomfort upon deep inspiration, and reduced vital capacity.",
        "primary_risks": ["Painful deep inhalation", "Airway epithelial damage", "Exercise-induced wheeze"],
        "remedy": "Schedule outdoor activities during early morning before photochemical sunlight reactions peak in the mid-afternoon."
    },
    "CO": {
        "full_name": "Carbon Monoxide (CO)",
        "mechanism": "Binds hemoglobin with 200x greater affinity than oxygen, forming carboxyhemoglobin and reducing systemic tissue oxygen delivery.",
        "primary_risks": ["Hypoxia in coronary artery disease patients", "Cephalea (headache)", "Dizziness and cognitive fatigue"],
        "remedy": "Ensure ventilation near combustion sources; eliminate indoor smoking and biomass burning."
    }
}

# ── Pydantic Structured Output Schemas ──────────────────────────────────
class CohortGuidance(BaseModel):
    cohort: str = Field(..., description="Target demographic cohort")
    vulnerability_multiplier: float = Field(..., description="Susceptibility risk multiplier")
    tier: str = Field(..., description="Assigned risk tier: LOW, MODERATE, HIGH, SEVERE")
    hri_score: float = Field(..., description="Calculated Health Risk Index value")
    summary: str = Field(..., description="Clinical executive takeaway for patient/guardian")
    action_items: List[str] = Field(default_factory=list, description="Concrete clinical precautions")
    emergency_symptoms: List[str] = Field(default_factory=list, description="Red flag symptoms requiring medical triage")

class DominantFactorClinicalNote(BaseModel):
    pollutant: str = Field(..., description="Dominant contributing pollutant")
    concentration: Optional[float] = Field(None, description="Current or forecast concentration value")
    physiological_impact: str = Field(..., description="Pathophysiological mechanism")
    targeted_intervention: str = Field(..., description="Targeted remediation intervention")

class ClinicalAdvisoryOutput(BaseModel):
    city: str
    assessment_tier: str
    dominant_pollutant: DominantFactorClinicalNote
    cohort_plans: List[CohortGuidance]
    environmental_context: str
    mitigation_checklist: List[str]
    generated_at: str
    schema_version: str = "v3.2-clinical"


# ── Advisory Generation Engine ──────────────────────────────────────────
class ClinicalAdvisoryEngine:
    """
    Produces deterministic, clinically valid advisories with strict schemas
    and automatic self-repair on schema errors.
    """

    @staticmethod
    def identify_dominant_pollutant(pollutant_values: Dict[str, float]) -> str:
        """Find pollutant with highest ratio relative to CPCB safety limit."""
        safety_limits = {"PM2.5": 30.0, "PM10": 50.0, "NO2": 40.0, "SO2": 40.0, "CO": 1.0, "O3": 50.0}
        highest_ratio = -1.0
        dominant = "PM2.5"
        for p, lim in safety_limits.items():
            val = pollutant_values.get(p)
            if val is not None and val > 0:
                ratio = val / lim
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    dominant = p
        return dominant

    @classmethod
    def generate_advisory(
        cls,
        city: str,
        aqi: float,
        pollutant_values: Optional[Dict[str, float]] = None,
        cutoffs: Optional[Dict[str, float]] = None,
        top_shap_factors: Optional[List[Dict[str, Any]]] = None
    ) -> ClinicalAdvisoryOutput:
        """
        Generate structured clinical advisory for a city based on live values.
        """
        from datetime import datetime, timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        now_str = datetime.now(ist).isoformat()

        cutoffs = cutoffs or {"p25": 7.12, "p75": 14.12, "p90": 23.59}
        pollutants = pollutant_values or {}

        # If pollutant concentrations not provided, infer from AQI approximation
        if not pollutants or all(v == 0 for v in pollutants.values()):
            pollutants = {
                "PM2.5": max(15.0, aqi * 0.55),
                "PM10": max(25.0, aqi * 0.90),
                "NO2": max(10.0, aqi * 0.22),
                "SO2": max(5.0, aqi * 0.08),
                "CO": max(0.5, aqi * 0.01),
                "O3": max(15.0, aqi * 0.18),
            }

        # Check SHAP factors to identify primary driver if available
        dominant_p = "PM2.5"
        if top_shap_factors and len(top_shap_factors) > 0:
            top_name = str(top_shap_factors[0].get("factor", "")).upper()
            for cand in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]:
                if cand in top_name:
                    dominant_p = cand
                    break
        else:
            dominant_p = cls.identify_dominant_pollutant(pollutants)

        prof = POLLUTANT_CLINICAL_PROFILES.get(dominant_p, POLLUTANT_CLINICAL_PROFILES["PM2.5"])

        # Base HRI calculation
        limits = {"PM2.5": 30.0, "PM10": 50.0, "NO2": 40.0, "SO2": 40.0, "CO": 1.0, "O3": 50.0}
        base_hri = sum(pollutants.get(k, 0.0) / lim for k, lim in limits.items())
        base_hri = max(2.5, base_hri)

        # Determine Tier
        def get_tier(val: float) -> str:
            if val <= cutoffs.get("p25", 7.12):
                return "LOW"
            elif val <= cutoffs.get("p75", 14.12):
                return "MODERATE"
            elif val <= cutoffs.get("p90", 23.59):
                return "HIGH"
            return "SEVERE"

        overall_tier = get_tier(base_hri)

        # Build cohort plans
        cohort_configs = [
            ("General Public", 1.0),
            ("Children & Elderly", 1.3),
            ("Respiratory Patients", 1.6),
        ]

        cohort_plans = []
        for cohort_name, factor in cohort_configs:
            group_hri = round(base_hri * factor, 2)
            group_tier = get_tier(group_hri)

            if group_tier == "LOW":
                summary = "Ambient air quality is within safe physiological limits. Regular daily activities permitted."
                actions = ["Continue regular outdoor exercise and recreational routines", "Maintain standard natural cross-ventilation in homes"]
                red_flags = ["Unexpected shortness of breath during light walks"]
            elif group_tier == "MODERATE":
                summary = f"Air pollution elevated ({dominant_p} dominant). Sensitive physiology may experience mild airway irritation."
                actions = [
                    "Avoid prolonged strenuous endurance activities near heavy traffic corridors",
                    "Close windows during morning inversion peaks (6:00 AM - 9:00 AM)",
                    "Maintain hydration to facilitate mucosal particulate clearance"
                ]
                red_flags = ["Persistent throat dryness", "Dry cough lasting > 1 hour", "Mild wheezing"]
            elif group_tier == "HIGH":
                summary = f"High pulmonary risk due to {dominant_p} accumulation. Significant systemic inflammatory burden."
                actions = [
                    "Wear well-fitted N95/FFP2 particulate respirators for any outdoor transit",
                    "Children, pregnant women, and elderly individuals should suspend outdoor playtime/exercise",
                    "Operate HEPA room air cleaners in sleep areas",
                    "Respiratory patients must keep prescribed bronchodilators within immediate reach"
                ]
                red_flags = ["Audible expiratory wheeze", "Chest tightness or retrosternal discomfort", "Dyspnea on minimal exertion"]
            else:  # SEVERE
                summary = f"EMERGENCY HEALTH ALERT: Dangerous bio-accumulation of {dominant_p}. Widespread acute cardiorespiratory risks."
                actions = [
                    "STRICT QUARANTINE: Avoid all discretionary outdoor exposure",
                    "Seal building envelopes (doors/windows) using weatherstripping",
                    "Continuous indoor HEPA filtration on high fan setting",
                    "Patients with asthma/COPD must initiate preventive action plans under pulmonologist guidance"
                ]
                red_flags = ["Cyanosis (bluish tint around lips/nails)", "Inability to speak in full sentences due to breathlessness", "Stridor or severe chest pain"]

            cohort_plans.append(CohortGuidance(
                cohort=cohort_name,
                vulnerability_multiplier=factor,
                tier=group_tier,
                hri_score=group_hri,
                summary=summary,
                action_items=actions,
                emergency_symptoms=red_flags
            ))

        dom_note = DominantFactorClinicalNote(
            pollutant=dominant_p,
            concentration=round(float(pollutants.get(dominant_p, 0.0)), 1),
            physiological_impact=prof["mechanism"],
            targeted_intervention=prof["remedy"]
        )

        env_context = f"{city} atmospheric monitoring indicates primary burden from {prof['full_name']}. Estimated CPCB AQI is {round(aqi)}."
        checklist = [
            f"Equip N95 respirator when outdoors if tier is HIGH or SEVERE",
            f"Address dominant pollutant: {prof['remedy']}",
            "Monitor vulnerable family members for sudden onset respiratory distress",
            "Consult local health department if symptomatic"
        ]

        try:
            return ClinicalAdvisoryOutput(
                city=city,
                assessment_tier=overall_tier,
                dominant_pollutant=dom_note,
                cohort_plans=cohort_plans,
                environmental_context=env_context,
                mitigation_checklist=checklist,
                generated_at=now_str
            )
        except ValidationError as ve:
            logger.error(f"Advisory schema validation failed, executing auto-repair: {ve}")
            return cls._auto_repair(city, overall_tier, dom_note, cohort_plans, now_str)

    @classmethod
    def _auto_repair(cls, city: str, tier: str, dom: DominantFactorClinicalNote, plans: List[CohortGuidance], now_str: str) -> ClinicalAdvisoryOutput:
        """Fallback auto-repair constructor ensuring 100% schema compliance."""
        return ClinicalAdvisoryOutput(
            city=str(city),
            assessment_tier=tier or "MODERATE",
            dominant_pollutant=dom,
            cohort_plans=plans or [],
            environmental_context="Automated baseline clinical advisory generated under fallback recovery mode.",
            mitigation_checklist=["Limit outdoor exertion", "Monitor vulnerable individuals"],
            generated_at=now_str
        )
