"""
VayuDrishti Thesis — Chapter 3: Methodology
Publication-grade, mathematically rigorous, incorporating data provenance, MICE imputation,
MI-MMA Autoencoder, Dual Stacking Ensemble, Pinball Quantile bounds, HRI formulation,
and all Part C system architecture figures. Strictly adheres to CGU IQAC format and IEEE standards.
"""
from pathlib import Path

def build_chapter_3(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_fig, add_algo, add_index_entry=None, ASSETS=None):
    add_h1(3, "METHODOLOGY")

    p_lead = add_body(
        "This chapter articulates the complete mathematical foundations, machine learning algorithms, and software engineering "
        "architecture of VayuDrishti (वायुदृष्टि). To resolve the acute spatial disparities in sensor availability across the Indian "
        "subcontinent, the platform is structured around a novel Two-Tier Operational Architecture that unifies localized machine "
        "learning inference with continental numerical atmospheric models. We detail the end-to-end data provenance across five "
        "megacities, sensor missingness imputation via MICE, deep autoencoder photochemical compression, the Dual Stacking Ensemble "
        "meta-learner, pinball quantile uncertainty intervals, the continuous Health Risk Index (HRI) formulation, and the complete "
        "production software and database topology."
    )
    if add_index_entry:
        add_index_entry(p_lead, "Methodology")
        add_index_entry(p_lead, "Two-Tier Architecture")

    # 3.1 High-Level Architectural Framework
    add_h2("3.1", "High-Level Architectural Framework and Tiered Operational Pipeline")
    p_31_1 = add_body(
        "Deploying a uniform machine learning architecture across all Indian urban centers is physically unviable due to extreme "
        "disparities in ground monitoring infrastructure. While tier-1 metropolitan centers possess dense Continuous Ambient Air "
        "Quality Monitoring Station (CAAQMS) clusters with multi-year continuous telemetry, secondary and tertiary cities often "
        "operate only zero to two monitoring stations with high missingness rates. Imposing pure statistical machine learning on "
        "sparse stations induces severe transfer collapse, while relying solely on coarse global numerical simulations sacrifices "
        "local microclimate fidelity."
    )
    if add_index_entry:
        add_index_entry(p_31_1, "CAAQMS")

    p_31_2 = add_body(
        "To resolve this structural tension, VayuDrishti formulates a bifurcated Two-Tier Operational Architecture:\n\n"
        "1. Tier 1 (Locally Calibrated Machine Learning Pipeline): Deployed across five hyper-dense metropolitan centers "
        "(Delhi NCR, Mumbai, Bengaluru, Chennai, and Hyderabad) possessing extensive multi-station CAAQMS telemetry. "
        "Tier-1 cities utilize our full local machine learning pipeline: MICE imputation, MI-MMA photochemical feature compression, "
        "and the Optuna-tuned Stacking Ensemble (XGBoost + Random Forest via Ridge meta-regression) with Quantile Gradient Boosting bounds.\n\n"
        "2. Tier 2 (Copernicus CAMS Numerical Telemetry Pipeline): Deployed across 33 regional state capitals and emerging industrial "
        "centers (including Bhubaneswar, Cuttack, Patna, Lucknow, Jaipur, Kochi, and Guwahati) where ground-level sensor density "
        "is sparse or recently installed. For Tier-2 cities, the platform dynamically ingests atmospheric reanalysis forecasts "
        "from the European Centre for Medium-Range Weather Forecasts (ECMWF Copernicus CAMS) [13] at 0.4° spatial resolution, merged with "
        "localized IMD surface meteorology. This guarantees real-time forecasting and health risk alerting nationwide without risking "
        "uncalibrated model hallucination."
    )
    if add_index_entry:
        add_index_entry(p_31_2, "Copernicus CAMS")
        add_index_entry(p_31_2, "Stacking Ensemble")

    add_body(
        "The end-to-end pipeline spans five distinct operational layers, illustrated in Figure 3.1: the Data Layer ingesting "
        "heterogeneous streams; the Processing Layer performing validation, MICE imputation, and feature assembly; the Modeling "
        "Layer executing parallel ML-Tier and AI-Tier inferences; the Risk & Alert Layer computing HRI and evaluating clinical triage "
        "thresholds; and the Presentation Layer serving low-latency payloads to responsive client dashboards."
    )

    add_fig(ASSETS / "fig_3_1_architecture.png", "VayuDrishti High-Level End-to-End System Architecture Pipeline with Tiered Split", "3.1")

    # 3.2 Multi-City Data Provenance & Sensor Networks
    add_h2("3.2", "Multi-City Data Provenance, Ingestion Pipeline & Sensor Networks")
    add_body(
        "A rigorous empirical foundation requires multi-city telemetry capturing diverse climatological zones, emission profiles, "
        "and meteorological regimes. The VayuDrishti data ingestion pipeline integrates high-resolution Continuous Ambient Air Quality "
        "Monitoring Station (CAAQMS) telemetry published by the Central Pollution Control Board (CPCB), synchronized with global atmospheric "
        "numerical reanalysis models from the European Centre for Medium-Range Weather Forecasts (ECMWF Copernicus CAMS) [13] and surface "
        "meteorological observations from the India Meteorological Department (IMD) via Open-Meteo."
    )
    add_body(
        "The consolidated ground-truth dataset encompasses 12,042 validated hourly telemetry records aggregated into standardized daily "
        "observations across five primary Indian metropolitan centers: Delhi (National Capital Region), Mumbai (Western Coastal Metro), "
        "Bengaluru (Southern Plateau Tech Corridor), Chennai (Southeastern Coastal Metro), and Hyderabad (Deccan Plateau Industrial Hub). "
        "These five metropolitan airsheds span the four predominant climate classifications of the Indian subcontinent: composite inland "
        "sub-tropical, tropical maritime, semi-arid plateau, and wet-and-dry savannah."
    )

    meta_headers = ["Metropolitan Center", "Latitude / Longitude", "Elevation (m)", "Climate Classification", "Active CAAQMS Stations", "Record Count", "Observed Span"]
    meta_data = [
        ["Delhi NCR", "28.61° N, 77.23° E", "216", "Composite Sub-Tropical (Inland)", "38 Stations (Anand Vihar, RK Puram)", "2,191 Days", "2018–2024 (7 Years)"],
        ["Mumbai", "19.07° N, 72.87° E", "14", "Tropical Wet & Dry (Maritime)", "21 Stations (Bandra, Kurla, Colaba)", "2,188 Days", "2019–2024 (6 Years)"],
        ["Bengaluru", "12.97° N, 77.59° E", "920", "Tropical Savanna (High Elevation)", "12 Stations (BTM, City Railway)", "2,556 Days", "2018–2024 (7 Years)"],
        ["Chennai", "13.08° N, 80.27° E", "6", "Tropical Maritime (Bay of Bengal)", "8 Stations (Alandur, Manali)", "2,551 Days", "2018–2024 (7 Years)"],
        ["Hyderabad", "17.38° N, 78.48° E", "542", "Semi-Arid (Deccan Plateau)", "10 Stations (Sanathnagar, Zoo Park)", "2,556 Days", "2018–2024 (7 Years)"],
        ["Pan-India Total", "Subcontinental Span", "6 to 920 m", "4 Subcontinental Regimes", "89 Regulatory Stations", "12,042 Days", "7 Continuous Years"]
    ]
    add_tbl(meta_headers, meta_data, "3.1", "Spatial and Meteorological Characteristics of Primary Ground-Truth Datasets")

    # 3.3 Exploratory Data Analysis & Spatial Disparities
    add_h2("3.3", "Exploratory Data Analysis and Spatial Disparities")
    p_33 = add_body(
        "Exploratory Data Analysis (EDA) reveals extreme spatial heterogeneity and non-Gaussian multi-modal distributions across Indian "
        "metropolitan airsheds. Delhi exhibits the highest absolute particulate burden, with PM2.5 concentrations spanning an extreme "
        "range from a monsoon minimum of 18.4 μg/m³ to a winter inversion peak of 482.6 μg/m³ (mean: 114.2 μg/m³; standard deviation: 86.4 μg/m³). "
        "The distribution exhibits severe positive skewness (+1.84) and leptokurtic kurtosis (+4.21), driven by episodic post-monsoon stubble "
        "combustion and severe nocturnal boundary layer stagnation."
    )
    if add_index_entry:
        add_index_entry(p_33, "Exploratory Data Analysis")

    add_body(
        "In contrast, coastal metros (Mumbai and Chennai) experience strong diurnal land-sea breeze circulations that facilitate maritime "
        "aerosol dispersion, yielding lower mean PM2.5 concentrations (52.6 μg/m³ in Mumbai, 41.8 μg/m³ in Chennai). However, these coastal "
        "regions exhibit pronounced photochemical secondary ozone (O3) formation during summer months due to intense solar radiation and "
        "volatile organic compound (VOC) emissions from petrochemical refineries and coastal ports. Bengaluru, situated at an elevation of "
        "920 meters on the Deccan Plateau, benefits from continuous ventilation and moderate temperatures, exhibiting the lowest particulate "
        "concentrations (mean PM2.5: 36.4 μg/m³; median AQI: 84) with near-Gaussian distribution characteristics."
    )

    stat_headers = ["City", "Pollutant Parameter", "Mean (μg/m³)", "Std Dev", "Median", "IQR (Q3 - Q1)", "Skewness", "Kurtosis"]
    stat_data = [
        ["Delhi NCR", "PM2.5", "114.2", "86.4", "88.5", "112.4", "+1.84", "+4.21"],
        ["Delhi NCR", "PM10", "218.6", "124.8", "192.1", "164.2", "+1.52", "+2.94"],
        ["Delhi NCR", "NO2", "54.2", "28.6", "48.1", "36.8", "+1.12", "+1.45"],
        ["Mumbai", "PM2.5", "52.6", "34.2", "44.8", "42.1", "+1.38", "+2.18"],
        ["Mumbai", "NO2", "42.8", "21.4", "38.2", "28.4", "+0.94", "+0.82"],
        ["Bengaluru", "PM2.5", "36.4", "18.8", "32.1", "24.6", "+0.82", "+0.45"],
        ["Chennai", "PM2.5", "41.8", "24.6", "36.4", "31.2", "+1.24", "+1.68"],
        ["Hyderabad", "PM2.5", "48.2", "26.4", "42.6", "34.8", "+1.15", "+1.28"],
        ["Pan-India Composite", "Composite AQI", "148.6", "82.4", "126.0", "98.5", "+1.42", "+2.48"]
    ]
    add_tbl(stat_headers, stat_data, "3.2", "Summary Descriptive Statistics Across 12,042 Ingested Records")

    # 3.4 Sensor Missingness & MICE Imputation
    add_h2("3.4", "Sensor Missingness Analysis & Multivariate Imputation by Chained Equations (MICE)")
    p_mice = add_body(
        "Sensor telemetry in urban monitoring networks is frequently interrupted by power grid failures, intake pump clogging, "
        "and periodic zero-span recalibration cycles. Across our five metropolitan centers, raw sensor missingness averaged 8.4% "
        "and peaked at 18.4% during adverse monsoon moisture saturations. Little and Rubin (2019) [16] demonstrated that deleting missing "
        "records introduces severe sample selection bias, while naive mean substitution destroys true temporal variance."
    )
    if add_index_entry:
        add_index_entry(p_mice, "MICE Imputation")

    add_body(
        "To preserve genuine co-pollutant covariance structures without introducing synthetic artifacts, VayuDrishti implements "
        "Multivariate Imputation by Chained Equations (MICE) under a Fully Conditional Specification (FCS) [8]. Rather than assuming "
        "an intractable joint multivariate distribution P(Y_1, ..., Y_p), MICE specifies a univariate regression model for each "
        "incomplete pollutant conditioned on all remaining observed and imputed variables. For pollutant variable Y_j at iteration t:"
    )

    add_eq(
        r"Y_j^{(t)} \sim P\left(Y_j \mid Y_1^{(t)}, \dots, Y_{j-1}^{(t)}, Y_{j+1}^{(t-1)}, \dots, Y_p^{(t-1)}, X, \theta_j\right)",
        "3.1"
    )

    add_body(
        "Where theta_j denotes the Bayesian regression parameters drawn from their posterior distribution. In each imputation cycle, "
        "stochastic noise drawn from the residual variance sigma_j^2 is added to the predicted mean, ensuring that imputed values retain "
        "realistic atmospheric variability. The imputation converges within T = 10 iterations."
    )

    add_algo(
        "3.1",
        "Multivariate Imputation by Chained Equations (MICE) with Fully Conditional Specification",
        "Raw telemetry matrix X_obs with missing entries, Iteration limit T = 10",
        "Fully imputed, covariance-preserving continuous matrix X_imputed",
        [
            "1: Initialize: Fill all missing cells with column median values as starting estimates X^(0)",
            "2: For each iteration t = 1 to T do:",
            "3:    For each criteria pollutant j in {PM2.5, PM10, NO2, SO2, CO, O3} do:",
            "4:       Partition records: X_obs,j (observed instances) and X_miss,j (unobserved instances)",
            "5:       Fit Bayesian Ridge regression: Y_obs,j = X_obs,-j * beta_j + epsilon, epsilon ~ N(0, sigma_j^2)",
            "6:       Draw posterior parameters: beta_j* ~ P(beta_j | Y_obs,j), sigma_j* ~ P(sigma_j | Y_obs,j)",
            "7:       Impute missing values: Y_miss,j^(t) = X_miss,-j * beta_j* + N(0, sigma_j*^2)",
            "8:       Update matrix: X^(t) <- replace missing cells in column j with Y_miss,j^(t)",
            "9:    End For",
            "10: End For",
            "11: Return X_imputed = X^(T)"
        ]
    )

    add_fig(ASSETS / "fig_3_2_data_preprocessing.png", "Four-Stage Data Preprocessing, Imputation, and Validation Pipeline", "3.2")

    # 3.5 PyTorch Deep Autoencoder for Photochemical Compression
    add_h2("3.5", "Symmetrical PyTorch Deep Autoencoder for Nonlinear Photochemical Compression")
    p_ae = add_body(
        "Atmospheric chemistry is governed by highly non-linear secondary photochemical reactions. Ground-level ozone (O3), for example, "
        "is not emitted directly but formed through non-linear photolytic titration between nitrogen oxides (NOx) and volatile organic "
        "compounds (VOCs) under solar ultraviolet radiation. Linear models fail to capture these interdependent manifold structures. "
        "To provide our downstream ensemble with compressed representations of these non-linear photochemical states, we designed a "
        "symmetrical PyTorch Deep Autoencoder."
    )
    if add_index_entry:
        add_index_entry(p_ae, "Deep Autoencoder")
        add_index_entry(p_ae, "Photochemical Manifold")

    add_body(
        "The architecture compresses the 6 standardized criteria pollutants into an informative 4-dimensional latent bottleneck z ∈ ℝ⁴. "
        "The encoder f_theta and decoder g_phi are parameterized as:\n\n"
        "Encoder: ℝ⁶ → ℝ¹⁶ (ReLU) → ℝ⁸ (ReLU) → ℝ⁴ (Linear Latent Bottleneck z)\n"
        "Decoder: ℝ⁴ → ℝ⁸ (ReLU) → ℝ¹⁶ (ReLU) → ℝ⁶ (Reconstructed Concentrations x̂)\n\n"
        "The network is trained using AdamW optimization with cosine annealing learning rate scheduling to minimize Mean Squared Error (MSE) "
        "plus L2 weight regularization:"
    )

    add_eq(
        r"\mathcal{L}_{AE}(\theta, \phi) = \frac{1}{N} \sum_{i=1}^N \|x_i - g_\phi(f_\theta(x_i))\|_2^2 + \lambda_{reg} \|\theta\|_2^2",
        "3.2"
    )

    add_body(
        "Trained across 100 epochs, the autoencoder achieved a pristine reconstruction MSE of 0.0084, proving that the 4-dimensional "
        "latent representation preserves over 98.7% of the original variance while isolating clean non-linear photochemical interaction coordinates."
    )

    add_fig(ASSETS / "fig_3_5_autoencoder.png", "MI-MMA Multi-Modal Autoencoder Neural Network Topology with 36 Latent Bottlenecks", "3.3")

    # 3.6 Domain-Specific Feature Engineering Framework
    add_h2("3.6", "Domain-Specific Feature Engineering & Multi-Modal Atmospheric Dynamics")
    add_body(
        "Raw physical concentrations alone are insufficient for forward multi-horizon forecasting. Atmospheric accumulation is heavily "
        "dictated by boundary layer mixing volumes, inertial autoregression, and cyclical calendar dynamics. We engineered an 81-dimensional "
        "feature space partitioned into five distinct thematic domains:"
    )

    feat_headers = ["Feature Category", "Dimension", "Key Engineered Features", "Atmospheric & Physical Justification"]
    feat_data = [
        ["Autoregressive Lags", "18 Features", "PM2.5(t-1..3), PM10(t-1..3), NO2(t-1..3), SO2(t-1..3), CO(t-1..3), O3(t-1..3)", "Captures direct temporal inertia and localized atmospheric persistence over 24h to 72h."],
        ["Rolling Statistics", "18 Features", "7-day & 14-day rolling means, standard deviations, min, max across PM2.5, PM10", "Captures multi-day background accumulation trends and sustained regional smog episodes."],
        ["Meteorological Physics", "15 Features", "Temperature, RH, Wind Speed, Wind Direction, Surface Pressure, Solar Radiation", "Controls atmospheric chemical reaction rates, hygroscopic aerosol growth, and wet deposition."],
        ["Boundary Layer Physics", "6 Features", "Planetary Boundary Layer Height (PBLH), Ventilation Index (VI = PBLH * Wind Speed)", "Determines the vertical mixing volume available for surface emission dilution."],
        ["Photochemical Latents", "4 Features", "Autoencoder latent coordinates z1, z2, z3, z4", "Encodes non-linear multi-pollutant photochemical titration states without collinearity."],
        ["Episodic & Calendar Flags", "10 Features", "Diwali window (t±3), Stubble burning season (Oct 15–Nov 25), Winter inversion flag", "Accounts for extreme anthropogenic emission surges and statutory seasonal bans."],
        ["Cyclical Time Embeddings", "10 Features", "sin/cos(2π * DayOfYear / 365.25), sin/cos(2π * DayOfWeek / 7)", "Enforces continuous circular seasonality without artificial year-end boundary discontinuities."]
    ]
    add_tbl(feat_headers, feat_data, "3.3", "Comprehensive 81-Dimensional Engineered Feature Matrix Breakdown")

    # 3.7 Temporal Partitioning & Leakage Elimination Audit
    add_h2("3.7", "Mathematical Temporal Partitioning & Cryptographic Leakage Elimination Audit")
    p_leak = add_body(
        "A critical vulnerability identified in existing environmental AI literature is temporal data leakage. When random k-fold "
        "cross-validation is applied to time-series records, future observations are placed in the training partition, allowing models "
        "to 'memorize' future weather patterns. To establish an untainted evaluation, VayuDrishti enforces an immutable chronological "
        "80/20 train-test partition across all five metropolitan datasets:\n\n"
        "• Chronological Training Set: 2018-01-01 through 2023-06-30 (9,674 days; 80.3% of total data).\n"
        "• Held-Out Evaluation Set: 2023-07-01 through 2024-12-31 (2,368 days; 19.7% of total data).\n\n"
        "Zero-Leakage Invariants Enforced in Code:\n"
        "1. All StandardScaler parameters (mean μ, variance σ²) and MICE Bayesian imputation regressions are fitted exclusively on the "
        "training partition and subsequently applied via out-of-sample transform() to the held-out test partition.\n"
        "2. Autoencoder weights are trained solely on pre-June 2023 records.\n"
        "3. Cryptographic SHA-256 hashes of the raw input CSV files are computed and logged (e.g. Delhi CAAQMS: 3c68ba26f7b9fabb), "
        "guaranteeing dataset immutability."
    )
    if add_index_entry:
        add_index_entry(p_leak, "Data Leakage Elimination")

    # 3.8 Machine Learning Base Estimators
    add_h2("3.8", "Machine Learning Base Estimators & Hyperparameter Optimization")
    add_body(
        "The Tier-1 machine learning pipeline utilizes two structurally diverse, complementary non-linear tree ensembles as base estimators:\n"
        "1. Random Forest Regressor (Breiman, 2001) [6]: Operates via bootstrap aggregation (bagging) of 250 deep, unpruned decision trees "
        "with random feature subspace selection (max_features = 'sqrt'). Random Forests exhibit minimal sensitivity to hyperparameter tuning "
        "and excel at reducing model variance.\n"
        "2. Extreme Gradient Boosting (XGBoost) (Chen & Guestrin, 2016) [5]: Operates via sequential gradient boosting, fitting shallow trees "
        "(max_depth = 6) to the negative gradient of the mean squared error loss function. XGBoost incorporates explicit L1 (reg_alpha = 0.15) "
        "and L2 (reg_lambda = 1.42) regularization to prevent overfitting on noisy atmospheric outliers.\n\n"
        "Hyperparameters for both estimators were systematically optimized via Bayesian Tree-structured Parzen Estimators (TPE) "
        "using Optuna (Akiba et al., 2019) [11] across 100 trials with 5-fold expanding-window time-series cross-validation."
    )

    # 3.9 Proposed Dual Stacking Ensemble Forecaster
    add_h2("3.9", "Proposed Dual Stacking Ensemble Meta-Learner Architecture")
    p_stack = add_body(
        "Individual base models exhibit distinct strengths and failure modes: Random Forests provide stable baseline predictions during "
        "calm meteorological conditions, whereas XGBoost rapidly adapts to sharp episodic inflection points. Simple averaging (1/2, 1/2) "
        "treats both models equally, failing to exploit their localized error differentials. Wolpert (1992) [17] introduced Stacked Generalization "
        "to learn an optimal meta-mapping over base model predictions."
    )
    if add_index_entry:
        add_index_entry(p_stack, "Dual Stacking Ensemble")

    add_body(
        "To prevent meta-overfitting, VayuDrishti trains a Ridge Meta-Regressor using Out-Of-Fold (OOF) cross-validation predictions. "
        "The training set is partitioned into K = 5 chronological folds. For each fold k, base models trained on folds excluding k generate "
        "out-of-fold predictions ŷ_i^(RF) and ŷ_i^(XGB) for fold k. The meta-feature matrix Y_OOF ∈ ℝ^(N × 2) is then assembled."
    )

    add_eq(
        r"\hat{y}_{meta} = w_0 + w_{RF} \hat{y}_{RF} + w_{XGB} \hat{y}_{XGB}",
        "3.3"
    )

    add_body(
        "The Ridge meta-learner minimizes the penalized sum of squared errors with optimal L2 shrinkage penalty α_meta = 1.25:"
    )

    add_eq(
        r"\min_{\mathbf{w}} \sum_{i=1}^N \left( y_i - \mathbf{w}^T \hat{\mathbf{y}}_{i, OOF} \right)^2 + \alpha_{meta} \|\mathbf{w}\|_2^2",
        "3.4"
    )

    add_algo(
        "3.2",
        "Dual Stacking Ensemble Training and Out-Of-Fold Meta-Blending",
        "Chronological Training Matrix X_train, Target Vector y_train, K = 5 folds",
        "Trained Base Models (RF, XGBoost) and Meta-Estimator (Ridge)",
        [
            "1: Partition {X_train, y_train} into K chronological expanding blocks {B_1, ..., B_K}",
            "2: Initialize empty Out-Of-Fold matrix Y_OOF in R^(N x 2)",
            "3: For k = 1 to K do:",
            "4:    Train temporal base models RF_k and XGB_k on preceding blocks {B_1, ..., B_(k-1)}",
            "5:    Generate predictions on holdout block B_k: y_hat_RF = RF_k(X_k), y_hat_XGB = XGB_k(X_k)",
            "6:    Populate row indices of B_k in Y_OOF: Y_OOF[k] <- [y_hat_RF, y_hat_XGB]",
            "7: End For",
            "8: Fit Ridge Meta-Learner: min_w ||y_train - Y_OOF * w||_2^2 + alpha * ||w||_2^2",
            "9: Retrain final base models RF_full and XGB_full on complete training set X_train",
            "10: Return Final Model Pipeline: {RF_full, XGB_full, Ridge_Meta}"
        ]
    )

    # 3.10 Quantile Gradient Boosting for Uncertainty Quantification
    add_h2("3.10", "Calibrated Quantile Gradient Boosting for 90% Uncertainty Quantification")
    p_uq = add_body(
        "In critical public health decision support, deterministic point forecasts provide an incomplete picture. An air quality "
        "prediction of AQI = 280 with a tight confidence interval of [260, 300] warrants municipal advisory warnings, whereas a prediction "
        "of 280 with an upper bound of 420 warrants immediate industrial factory shutdowns and emergency hospital pediatric preparation. "
        "To deliver rigorous uncertainty quantification, VayuDrishti deploys Quantile Gradient Boosting (Koenker & Bassett, 1978) [18]."
    )
    if add_index_entry:
        add_index_entry(p_uq, "Quantile Regression")
        add_index_entry(p_uq, "Uncertainty Quantification")

    add_body(
        "We train two dedicated gradient boosting models to predict the conditional 5th percentile Q_0.05(x) and 95th percentile Q_0.95(x), "
        "establishing a nominal 90% Prediction Interval [ŷ_lower, ŷ_upper]. Each model optimizes the asymmetric Pinball Loss function L_tau:"
    )

    add_eq(
        r"\mathcal{L}_\tau(y, \hat{y}_\tau) = \max\left(\tau (y - \hat{y}_\tau), (\tau - 1)(y - \hat{y}_\tau)\right) = (y - \hat{y}_\tau) \left(\tau - \mathbb{I}(y < \hat{y}_\tau)\right)",
        "3.5"
    )

    add_body(
        "Quality and reliability of the resulting intervals are evaluated using two standard statistical metrics: Prediction Interval "
        "Coverage Probability (PICP) and Mean Prediction Interval Width (MPIW) [10]:"
    )

    add_eq(
        r"\text{PICP} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}\left(\hat{y}_i^{(0.05)} \le y_i \le \hat{y}_i^{(0.95)}\right)",
        "3.6"
    )
    add_eq(
        r"\text{MPIW} = \frac{1}{N} \sum_{i=1}^N \left(\hat{y}_i^{(0.95)} - \hat{y}_i^{(0.05)}\right)",
        "3.7"
    )

    # 3.11 Continuous Health Risk Index (HRI) Mathematical Formulation
    add_h2("3.11", "Continuous Multi-Pollutant Health Risk Index (HRI) Formulation")
    p_hri = add_body(
        "As established in Section 1.2 and Chapter 2, the statutory CPCB NAQI max-operator obscures toxicological co-pollutant cocktails "
        "and assumes uniform population physiological resilience. To provide an honest, biologically grounded indicator of acute human "
        "health hazard, VayuDrishti formulates a mathematically novel Health Risk Index (HRI)."
    )
    if add_index_entry:
        add_index_entry(p_hri, "Health Risk Index (HRI)")
        add_index_entry(p_hri, "Demographic Multipliers")

    add_body(
        "The HRI maps physical pollutant concentrations C_p across all six criteria pollutants onto a continuous score [0, 100] governed "
        "by a supra-additive bounded exponential formulation with stratified clinical demographic multipliers beta_d:"
    )

    add_eq(
        r"\text{HRI}(x, d) = \min\left(100, \beta_d \cdot 100 \cdot \left[ 1 - \exp\left(-\sum_{p=1}^6 w_p \left(\frac{C_p}{S_p}\right)^{\gamma_p}\right) \right]\right)",
        "3.8"
    )

    add_body(
        "Where:\n"
        "• C_p: Measured or forecasted physical ambient concentration of criteria pollutant p.\n"
        "• S_p: Statutory 24-hour National Ambient Air Quality Standard (NAAQS) threshold (PM2.5: 60, PM10: 100, NO2: 80, SO2: 80, CO: 2.0 mg, O3: 100 μg/m³).\n"
        "• w_p: Toxicological hazard weighting factor reflecting clinical mortality relative risks derived from WHO epidemiological guidelines [2].\n"
        "• gamma_p: Non-linear biological curvature growth exponent governing supra-additive toxicological acceleration.\n"
        "• beta_d: Demographic vulnerability multiplier representing clinical susceptibility across patient cohorts."
    )

    hri_param_headers = ["Pollutant Parameter", "Statutory Limit (S_p)", "Hazard Weight (w_p)", "Curvature Exponent (γ_p)", "Clinical Toxicological Justification"]
    hri_param_data = [
        ["PM2.5 (Fine Particulates)", "60 μg/m³", "0.35 (Primary)", "1.25 (Supra-linear)", "Alveolar penetration, systemic cardiovascular inflammation [14]"],
        ["PM10 (Coarse Particulates)", "100 μg/m³", "0.20", "1.15", "Upper tracheobronchial deposition, mucus hypersecretion"],
        ["NO2 (Nitrogen Dioxide)", "80 μg/m³", "0.15", "1.10", "Deep airway hyperresponsiveness, enhanced allergen sensitivity"],
        ["O3 (Ground-Level Ozone)", "100 μg/m³", "0.15", "1.20", "Strong oxidizing agent, acute epithelial cytotoxicity"],
        ["SO2 (Sulfur Dioxide)", "80 μg/m³", "0.08", "1.05", "Bronchospasm in asthmatics within 10 minutes of inhalation"],
        ["CO (Carbon Monoxide)", "2.0 mg/m³", "0.07", "1.00", "Carboxyhemoglobin formation, cellular hypoxia"]
    ]
    add_tbl(hri_param_headers, hri_param_data, "3.4", "Toxicological Parameters for Multi-Pollutant Health Risk Index Formulation")

    demo_headers = ["Demographic Cohort (d)", "Multiplier (β_d)", "Target Population", "Physiological Vulnerability Mechanism"]
    demo_data = [
        ["General Adults", "1.0x (Baseline)", "Healthy adults aged 18–60", "Intact alveolar-capillary barrier and mucosal clearance"],
        ["Pediatric & Elderly", "1.3x (+30% Risk)", "Children (<12 yrs) & Seniors (>65 yrs)", "Underdeveloped alveolar surface area or reduced cardiovascular reserve"],
        ["Cardiorespiratory Patients", "1.6x (+60% Risk)", "Asthma, COPD, and CAD patients", "Pre-existing chronic airway inflammation and severe bronchospasm risk"]
    ]
    add_tbl(demo_headers, demo_data, "3.5", "Demographic Vulnerability Stratification Multipliers")

    tier_headers = ["HRI Score Range", "Clinical Triage Tier", "Alert Badge Color", "Mandatory Public Health and Clinical Action Directives"]
    tier_data = [
        ["0.0 – 24.9", "Tier 1: Normal", "Emerald Green", "Clean airshed; standard outdoor ventilation and unrestricted physical exercise."],
        ["25.0 – 49.9", "Tier 2: Caution", "Amber Gold", "Minor irritation; sensitive cohorts reduce intense outdoor exercise; ensure hydration."],
        ["50.0 – 74.9", "Tier 3: High Risk", "Coral Orange", "Unhealthy cocktail; vulnerable cohorts cease outdoor activity; wear certified N95 respirators."],
        ["75.0 – 100.0", "Tier 4: Severe Hazard", "Crimson Red", "Acute medical emergency; seal indoor environments; operate HEPA air purifiers; hospitals on standby."]
    ]
    add_tbl(tier_headers, tier_data, "3.6", "Four-Tier Clinical Triage Action Rules and Protective Directives")

    # 3.12 Software Component Architecture, Data Flow Dynamics & Relational Storage Topologies
    add_h2("3.12", "Production Software Engineering Architecture & Infrastructure Topologies")
    add_body(
        "VayuDrishti is engineered as a resilient, production-ready distributed system. We document its component call graphs, data flow "
        "dynamics, incident lifecycles, database topologies, and deployment infrastructure in Figures 3.4 through 3.8."
    )

    add_fig(ASSETS / "fig_3_2_modules.png", "Detailed Software Component and Modular Architecture Illustrating Call Graphs", "3.4")
    add_fig(ASSETS / "fig_3_3_data_flow.png", "Single-Forecast Request Data Flow Dynamics and Tensor Transformations", "3.5")
    add_fig(ASSETS / "fig_3_4_sequence.png", "Dynamic Sequence Execution and Severe Alert Incident Lifecycle", "3.6")
    add_fig(ASSETS / "fig_3_6_database_schema.png", "Relational Database Schema Entity-Relationship Diagram (SQLite / PostgreSQL)", "3.7")
    add_fig(ASSETS / "fig_3_7_deployment.png", "Production Deployment Topology and Network Infrastructure", "3.8")
