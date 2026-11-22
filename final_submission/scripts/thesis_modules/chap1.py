"""
VayuDrishti Thesis — Chapter 1: Introduction
Authoritative, publication-grade academic text strictly adhering to CGU IQAC format and IEEE standards.
"""

def build_chapter_1(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_p, add_index_entry=None):
    add_h1(1, "INTRODUCTION")

    # 1.1 Context and Public Health Crisis
    add_h2("1.1", "Context and Public Health Crisis of Air Pollution in India")
    p1 = add_body(
        "Ambient air pollution has emerged as one of the most catastrophic environmental and public health "
        "crises confronting modern urban India. Rapid industrialization, unprecedented vehicular density expansion, "
        "unregulated infrastructural construction, agricultural biomass combustion, and persistent meteorological "
        "inversions have transformed the Indo-Gangetic Plains and major metropolitan airsheds into globally recognized "
        "hotspots of toxic atmospheric particulate accumulation. According to comprehensive epidemiological assessments "
        "published by the India State-Level Disease Burden Initiative in The Lancet Planetary Health [3], ambient particulate "
        "matter (PM2.5 and PM10) exposure was responsible for approximately 1.67 million premature deaths in India in 2019 "
        "alone, accounting for 17.8% of total nationwide mortality. Furthermore, economic output losses attributed to lost "
        "labor productivity and healthcare expenditures exceeded $36.8 billion, representing approximately 1.36% of India's "
        "Gross Domestic Product."
    )
    if add_index_entry:
        add_index_entry(p1, "Air Pollution Crisis")
        add_index_entry(p1, "Particulate Matter (PM2.5)")

    p2 = add_body(
        "Unlike Western European or North American airsheds where atmospheric pollution is predominantly driven by steady "
        "vehicular fossil fuel emissions, Indian urban centers experience extreme seasonal and episodic volatility. During the "
        "post-monsoon and winter transitions (October through January), severe meteorological stagnation occurs: planetary "
        "boundary layer heights (PBLH) collapse from typical daytime heights of 1,500–2,000 meters down to 100–300 meters, trapping "
        "surface emissions beneath dense temperature inversion caps. Concurrently, regional agricultural stubble burning across "
        "Punjab, Haryana, and Western Uttar Pradesh injects massive plumes of fine carbonaceous soot into the regional atmosphere. "
        "Coupled with festive firecracker discharges and localized domestic biomass burning, ambient concentrations of fine particulate "
        "matter (PM2.5) routinely surpass 400 to 600 μg/m³—exceeding World Health Organization (WHO) 24-hour safe limits (15 μg/m³) [2] "
        "by more than thirty to forty fold."
    )
    if add_index_entry:
        add_index_entry(p2, "Planetary Boundary Layer Height (PBLH)")
        add_index_entry(p2, "Temperature Inversion")

    add_body(
        "The physiological impact of chronic inhalation of this atmospheric cocktail is severe and multi-systemic. Fine particulate "
        "matter with an aerodynamic diameter smaller than 2.5 micrometers (PM2.5) penetrates past the ciliated mucosal defenses of "
        "the upper respiratory tract, depositing directly within pulmonary alveoli. From the alveolar membrane, ultra-fine particulates "
        "translocate into the systemic bloodstream, inducing systemic vascular endothelial inflammation, oxidative cellular stress, "
        "accelerated atherosclerosis, and elevated risks of acute myocardial infarction, ischemic stroke, and lung cancer [14]. In developing "
        "children, chronic exposure permanently reduces maximal forced expiratory volume (FEV1), while in elderly citizens with pre-existing "
        "cardiopulmonary conditions, sudden smog episodes trigger acute respiratory distress and fatal exacerbations."
    )

    # 1.2 Statutory Framework and NAQI
    add_h2("1.2", "Statutory Framework and the National Air Quality Index (NAQI)")
    p3 = add_body(
        "To establish a standardized statutory framework for environmental monitoring, the Ministry of Environment, Forest and "
        "Climate Change (MoEFCC) enacted the Air (Prevention and Control of Pollution) Act in 1981, empowering the Central Pollution "
        "Control Board (CPCB) to establish ambient regulatory limits. Under the revised National Ambient Air Quality Standards (NAAQS) "
        "notified in November 2009, statutory limits were established for twelve environmental contaminants across industrial, "
        "residential, and ecologically sensitive zones. For operational air quality communications, the CPCB designated six primary "
        "criteria pollutants for continuous automated monitoring: Particulate Matter ≤ 2.5 μm (PM2.5), Particulate Matter ≤ 10 μm "
        "(PM10), Nitrogen Dioxide (NO2), Sulfur Dioxide (SO2), Carbon Monoxide (CO), and Ozone (O3) [1]."
    )
    if add_index_entry:
        add_index_entry(p3, "National Ambient Air Quality Standards (NAAQS)")
        add_index_entry(p3, "Central Pollution Control Board (CPCB)")
        add_index_entry(p3, "National Air Quality Index (NAQI)")

    naaqs_headers = ["Pollutant", "Averaging Period", "Industrial/Residential (μg/m³)", "Ecologically Sensitive (μg/m³)", "Analytical Reference Method"]
    naaqs_data = [
        ["PM2.5", "24 Hours", "60", "60", "Beta Attenuation / TEOM"],
        ["PM10", "24 Hours", "100", "100", "Gravimetric / TOEM"],
        ["NO2", "24 Hours", "80", "80", "Chemiluminescence"],
        ["SO2", "24 Hours", "80", "80", "Ultraviolet Fluorescence"],
        ["CO", "8 Hours", "2.0 (mg/m³)", "2.0 (mg/m³)", "Non-Dispersive Infrared (NDIR)"],
        ["O3", "8 Hours", "100", "100", "UV Photometric Absorption"],
    ]
    add_tbl(naaqs_headers, naaqs_data, "1.1", "National Ambient Air Quality Standards (NAAQS) for 6 Criteria Pollutants")

    add_body(
        "In October 2014, the Government of India formally launched the National Air Quality Index (NAQI) under the 'One Number, "
        "One Colour, One Description' dissemination philosophy [1]. The NAQI converts multi-pollutant physical concentrations into an "
        "intuitive dimensionless integer score ranging from 0 to 500, partitioned into six public health categories: Good (0–50), "
        "Satisfactory (51–100), Moderate (101–200), Poor (201–300), Very Poor (301–400), and Severe (401–500). The mathematical "
        "formulation calculates a sub-index for each monitored pollutant using a piecewise linear interpolation function:"
    )

    add_eq(r"I_p = \frac{I_{HI} - I_{LO}}{B_{HI} - B_{LO}} (C_p - B_{LO}) + I_{LO}", "1.1")

    add_body(
        "Where C_p denotes the measured ambient concentration of pollutant p, B_HI and B_LO represent the upper and lower concentration "
        "breakpoints corresponding to the target index category, and I_HI and I_LO denote the corresponding index score limits. "
        "Once individual sub-indices are derived, the composite National Air Quality Index is assigned by taking the mathematical maximum "
        "across all available criteria sub-indices:"
    )

    add_eq(r"\text{NAQI} = \max_{p \in \mathcal{P}} \{I_p\}", "1.2")

    naqi_headers = ["AQI Category", "Index Range", "PM2.5 (24h)", "PM10 (24h)", "NO2 (24h)", "O3 (8h)", "Associated Health Statement"]
    naqi_data = [
        ["Good", "0 – 50", "0 – 30", "0 – 50", "0 – 40", "0 – 50", "Minimal health impact; clean pristine airshed."],
        ["Satisfactory", "51 – 100", "31 – 60", "51 – 100", "41 – 80", "51 – 100", "Minor breathing discomfort to sensitive individuals."],
        ["Moderate", "101 – 200", "61 – 90", "101 – 250", "81 – 180", "101 – 168", "Breathing discomfort to asthmatics, children, and elderly."],
        ["Poor", "201 – 300", "91 – 120", "251 – 350", "181 – 280", "169 – 208", "Breathing discomfort to most people on prolonged exposure."],
        ["Very Poor", "301 – 400", "121 – 250", "351 – 430", "281 – 400", "209 – 748", "Respiratory illness on prolonged exposure; severe effects."],
        ["Severe", "401 – 500", "250+", "430+", "400+", "748+", "Affects healthy people; serious impacts on respiratory patients."]
    ]
    add_tbl(naqi_headers, naqi_data, "1.2", "CPCB National Air Quality Index (NAQI) Breakpoint Sub-Indices")

    # 1.3 CAAQMS Sensor Networks & Vulnerabilities
    add_h2("1.3", "CAAQMS Sensor Networks and Inherent Operational Vulnerabilities")
    add_body(
        "To operationalize statutory air quality monitoring, the CPCB in collaboration with State Pollution Control Boards (SPCBs) "
        "has deployed the Continuous Ambient Air Quality Monitoring Station (CAAQMS) network. These state-of-the-art automated shelters "
        "house regulatory-grade reference analyzers—such as beta-attenuation monitors, pulsed UV fluorescence analyzers, and gas "
        "chemiluminescence detectors—transmitting automated hourly telemetry packets to central servers. However, real-world field "
        "deployment across Indian metropolitan regions reveals four persistent operational failure points:"
    )
    add_body(
        "1. High Missing Telemetry Rates: Ground-level CAAQMS stations suffer from persistent data missingness, averaging 8.4% across criteria "
        "pollutants and surging above 18.4% during unannounced power grid interruptions, sensor recalibration cycles, and air sampling pump "
        "clogging. Standard municipal portals rely on naive forward-fill (LOCF) or mean substitution, which fundamentally distorts "
        "temporal volatility.\n"
        "2. Physical Sensor Drift and Stagnation: Prolonged exposure to extreme particulate burdens causes optical lens fouling and baseline "
        "photometer drift. Sensors frequently enter 'frozen states' where stale numeric telemetry is continuously broadcast for 6 to 12 hours "
        "without triggering diagnostic alarms.\n"
        "3. High Capital and Maintenance Constraints: Regulatory-grade CAAQMS installations require capital investments of ₹1.2 to ₹1.8 Crore "
        "($150,000–$220,000 USD) per station with substantial recurring air conditioning and consumable filter costs. Consequently, Indian "
        "cities possess extremely sparse spatial sensor density: Delhi possesses approximately 40 operational stations for 30 million residents, "
        "while tier-2 state capitals like Bhubaneswar and Cuttack rely on only 2 to 4 stations.\n"
        "4. Ingestion Latency and Upstream Failures: Network outages between regional SPCB field modems and central CPCB ingestion servers "
        "frequently introduce 2 to 6 hour propagation delays, rendering real-time citizen warnings ineffective."
    )

    # 1.4 Mathematical Problem Statement
    add_h2("1.4", "Mathematical Problem Statement")
    add_body(
        "Let a metropolitan airshed be monitored at discrete hourly timestamps t ∈ {1, 2, …, T}. At each time step t, a vector of "
        "criteria pollutant concentrations x_t ∈ ℝ⁶ is recorded, where x_t = [PM2.5, PM10, NO2, SO2, CO, O3]ᵀ, alongside an aligned "
        "vector of meteorological surface observations m_t ∈ ℝᴹ comprising temperature, relative humidity, wind speed, wind direction, "
        "surface pressure, solar radiation, and planetary boundary layer height (PBLH). Due to physical sensor degradation and transmission "
        "outages, the observed pollutant matrix X_obs contains missing elements denoted by binary indicator matrix M ∈ {0, 1}^(T × 6)."
    )
    add_body(
        "The forward multi-horizon forecasting problem is defined as learning an optimal parameter mapping θ that maps historical "
        "imputed observations over a lookback window of L days onto future composite Air Quality Index values y_{t+h} across discrete "
        "forward prediction horizons h ∈ {24, 48, 72} hours:"
    )

    add_eq(r"\hat{y}_{t+h} = f_\theta\left(\{x_{t-\tau}, m_{t-\tau}\}_{\tau=0}^{L-1}\right), \quad h \in \{24, 48, 72\}", "1.3")

    add_body(
        "Concurrently, the system must quantify atmospheric epistemic and aleatoric uncertainty by learning conditional quantile functions "
        "Q_τ(y_{t+h} | x_t, m_t) at lower τ = 0.05 and upper τ = 0.95 quantile thresholds, such that the empirical Prediction Interval "
        "Coverage Probability (PICP) satisfies nominal 90% confidence:"
    )

    add_eq(r"P\left(\hat{y}_{t+h}^{(0.05)} \le y_{t+h} \le \hat{y}_{t+h}^{(0.95)}\right) \ge 0.90", "1.4")

    add_body(
        "Finally, given multi-pollutant concentration vector x_{t+h} and demographic vulnerability profile d ∈ {General Adults, "
        "Children/Elderly, Cardiorespiratory Patients}, the objective is to evaluate a continuous Health Risk Index HRI ∈ [0, 100] "
        "governed by non-linear supra-additive biological interaction rules."
    )

    # 1.5 Research Objectives & Scope
    add_h2("1.5", "Research Objectives and Scope")
    add_body(
        "To resolve the operational challenges and toxicological limitations of current environmental systems, this major project "
        "formulates four binding scientific and technological objectives:"
    )
    add_body(
        "• Objective 1: Construct a verified, leakage-free data foundation across five primary Indian metropolitan cities (Delhi, Mumbai, "
        "Bengaluru, Chennai, Hyderabad), integrating MICE multivariate imputation and a Deep Autoencoder photochemical compression "
        "pipeline to resolve sensor missingness.\n"
        "• Objective 2: Design and optimize an Optuna-tuned Stacking Ensemble (Random Forest + XGBoost via Ridge meta-regression) for 24h, "
        "48h, and 72h forward AQI forecasting, incorporating pinball-loss calibrated quantile regressors to deliver verified 90% prediction intervals.\n"
        "• Objective 3: Formulate and validate a mathematically sound Health Risk Index (HRI) based on bounded supra-additive exponential "
        "multi-pollutant formulations, incorporating demographic vulnerability multipliers (1.0x, 1.3x, 1.6x) and four-tier triage action rules.\n"
        "• Objective 4: Build, benchmark, and deploy a production-grade asynchronous platform (FastAPI + React 19 + Redis) serving 38 Indian "
        "cities with sub-10ms inference latency, verified circuit-breaker fault tolerance, and comprehensive automated test suites."
    )

    # 1.6 Major Scientific & Engineering Contributions
    add_h2("1.6", "Major Scientific and Engineering Contributions")
    add_body(
        "The primary contributions of this thesis are summarized as follows:"
    )
    add_body(
        "1. Master Ground-Truth Multi-City Data Asset: Consolidation of 12,042 validated hourly telemetry records across five diverse Indian "
        "airsheds with strict chronological train-test isolation and a mathematically audited leakage-free preprocessing pipeline.\n"
        "2. Empirically Superior Stacking Ensemble: Delivery of an Optuna-optimized Dual Stacking Ensemble achieving Test R² = 0.9248, "
        "RMSE = 13.84 AQI points, MAE = 9.12, and continuous regression accuracy of 91.42% (baseline un-tuned R² = 0.9014, RMSE = 16.64), "
        "with formal parametric and non-parametric hypothesis testing confirming statistical significance (p = 0.0002).\n"
        "3. Calibrated Conformal Uncertainty Intervals: Implementation of pinball quantile gradient boosting achieving 90.01% empirical coverage "
        "across 2,368 held-out test days with a sharp average interval width of 43.91 AQI points.\n"
        "4. Novel Health Risk Index (HRI) Modeling: Formulation of an exponential multi-pollutant risk index with demographic stratification "
        "that resolves the toxicological distortions of traditional CPCB NAQI.\n"
        "5. Sub-10ms Production-Ready Platform: Full-stack implementation delivering 2.41 ms average inference latency under 50 concurrent "
        "virtual users, 42 ms circuit breaker fallback to Copernicus CAMS, and 14 passing automated Pytest verification modules."
    )

    # 1.7 Thesis Organization
    add_h2("1.7", "Structural Organization of the Thesis")
    p_org = add_body(
        "The remainder of this project report is organized as follows in accordance with the C.V. Raman Global University (CGU) IQAC guidelines:\n\n"
        "• Chapter 2 (Literature Survey) provides an exhaustive review of physical dispersion models, classical stochastic time-series, "
        "deep sequence learning, gradient boosted decision trees, environmental missingness imputation, and multi-pollutant risk indices, "
        "concluding with a 12-study benchmark matrix and five identified research gaps.\n"
        "• Chapter 3 (Methodology) presents the end-to-end VayuDrishti architecture, multi-city data provenance, MICE imputation, "
        "MI-MMA autoencoder neural compression, the Dual Stacking Ensemble, quantile uncertainty quantification, the HRI clinical engine, "
        "and complete system architecture diagrams.\n"
        "• Chapter 4 (Results and Discussion) delivers extensive empirical benchmarks, ablation studies, inferential hypothesis testing, "
        "multi-horizon degradation, LOCO spatial transferability, TreeSHAP explainability, 5 metropolitan case studies, and 30-day live tracking.\n"
        "• Chapter 5 (Conclusion) summarizes scientific findings, provides honest disclosures of system limitations, outlines public policy "
        "implications, and articulates the Stage-2 (8th Semester) technical roadmap.\n"
        "• References and Appendices provide IEEE formatted citations, mathematical notation glossaries, hyperparameter grids, automated test "
        "matrices, and department evaluation rubrics compliance."
    )
    if add_index_entry:
        add_index_entry(p_org, "Structural Organization")
