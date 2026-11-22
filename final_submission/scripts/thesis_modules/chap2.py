"""
VayuDrishti Thesis — Chapter 2: Literature Survey
Exhaustive, publication-grade academic survey of atmospheric modeling, statistical forecasting,
deep sequence learning, tabular gradient boosting, imputation theories, and epidemiological indices.
Strictly follows CGU IQAC format and IEEE citation standards.
"""
from pathlib import Path

def build_chapter_2(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_fig, add_algo, add_index_entry=None, ASSETS=None):
    add_h1(2, "LITERATURE SURVEY")

    p_lead = add_body(
        "Atmospheric air quality prediction and public health protection have been focal points of environmental engineering, "
        "atmospheric physics, and computational intelligence for several decades. Over the preceding twenty years, researchers "
        "have transitioned from deterministic numerical fluid dynamics to statistical stochastic processes, recurrent neural "
        "networks, and high-performance gradient-boosted decision trees. This chapter presents an exhaustive, structured taxonomy "
        "and critical synthesis of prior literature across six primary methodological domains, concluding with a comprehensive "
        "12-study benchmark matrix and five identified research gaps that motivate the VayuDrishti architecture."
    )
    if add_index_entry:
        add_index_entry(p_lead, "Literature Survey")

    # 2.1 Physics-Based Numerical Dispersion Models
    add_h2("2.1", "Physics-Based Numerical and Atmospheric Dispersion Models")
    p_num = add_body(
        "Deterministic numerical air quality modeling relies on fundamental conservation laws governing atmospheric fluid mechanics, "
        "thermodynamics, and photochemical kinetics. Prominent systems include the Community Multiscale Air Quality (CMAQ) modeling system "
        "developed by the United States Environmental Protection Agency (US EPA) [15], the Weather Research and Forecasting model coupled "
        "with Chemistry (WRF-Chem) [22], and local-scale Gaussian plume models such as AERMOD [23]."
    )
    if add_index_entry:
        add_index_entry(p_num, "CMAQ Modeling System")
        add_index_entry(p_num, "Atmospheric Dispersion")

    add_body(
        "CMAQ and WRF-Chem numerically solve the three-dimensional advection-diffusion-reaction equation for chemical species concentration C_i:"
    )

    add_eq(
        r"\frac{\partial C_i}{\partial t} = -\nabla \cdot (\mathbf{u} C_i) + \nabla \cdot (\mathbf{K} \nabla C_i) + R_i(C_1, \dots, C_M) + E_i - S_i",
        "2.1"
    )

    add_body(
        "Where u denotes the 3D wind velocity vector, K is the eddy diffusivity tensor representing turbulent atmospheric mixing, "
        "R_i is the non-linear chemical reaction rate term describing photochemical gas-phase and aqueous-phase transformation, "
        "E_i represents anthropogenic and biogenic emission fluxes, and S_i denotes sink processes including dry and wet gravitational deposition.\n\n"
        "While physically rigorous, numerical chemical transport models suffer from severe operational limitations in Indian megacities:\n"
        "1. Extreme Computational Overhead: Simulating a 72-hour forecast at 1 km grid resolution requires high-performance supercomputing "
        "clusters executing for 6 to 12 hours, precluding real-time sub-second municipal warning dissemination.\n"
        "2. Dependency on Granular Emission Inventories: CMAQ requires static emission grids detailing spatial vehicular traffic, industrial "
        "chimney plumes, and brick kiln outputs. In rapidly urbanizing Indian cities, informal biomass burning, unpaved road dust, and "
        "unmonitored construction activities render static emission inventories outdated and inaccurate by up to 40%.\n"
        "3. Topographical and Microclimatic Errors: Coarse regional grid cells (typically 4 km to 12 km) fail to resolve urban street canyons, "
        "micro-scale thermal eddies, and localized traffic junctions."
    )

    # 2.2 Classical Statistical & Stochastic Autoregressive Methods
    add_h2("2.2", "Classical Statistical and Stochastic Autoregressive Time-Series")
    add_body(
        "To circumvent the computational intractability of numerical fluid dynamics, statistical researchers developed empirical "
        "time-series methods. Box and Jenkins (1976) [24] established the theoretical foundation of stochastic autoregression with "
        "the Autoregressive Integrated Moving Average (ARIMA(p, d, q)) framework. In atmospheric studies, Slini et al. (2002) [25] "
        "applied Seasonal ARIMA (SARIMA) to forecast maximum ozone concentrations in Athens, demonstrating good fidelity under stable "
        "diurnal solar radiation cycles. Similarly, Sharma et al. (2018) [26] evaluated ARIMA across monitoring stations in Delhi, "
        "reporting that 24-hour persistence provided moderate baseline tracking (R² ≈ 0.72) during undisturbed summer months."
    )
    add_body(
        "However, classical stochastic models exhibit fatal failures when applied to Indian atmospheric airsheds:\n"
        "1. Assumption of Gaussian Linearity: ARIMA assumes that time-series errors are linearly generated from zero-mean Gaussian white noise. "
        "In reality, atmospheric pollutant dispersion is governed by highly non-linear threshold phenomena (e.g. abrupt planetary boundary "
        "layer collapse and photolytic ozone titration).\n"
        "2. Inability to Ingest Exogenous Multi-Modal Drivers: Univariate ARIMA cannot natively incorporate non-linear interactions between "
        "relative humidity, wind shear, and boundary layer dynamics.\n"
        "3. Catastrophic Peak Under-Prediction: During rapid smog onset (such as post-monsoon stubble influx or Diwali firecracker episodes), "
        "ARIMA severely lags behind actual concentration curves, predicting conservative mean reversions instead of hazardous peaks."
    )

    # 2.3 Deep Recurrent Sequence Learning
    add_h2("2.3", "Deep Recurrent Sequence Learning and Tabular Limitations")
    add_body(
        "With the rapid progression of deep representation learning, recurrent neural architectures—specifically Long Short-Term "
        "Memory (LSTM) networks introduced by Hochreiter and Schmidhuber (1997) [7] and Gated Recurrent Units (GRU) by Cho et al. (2014) [27]—became "
        "the dominant academic paradigm for spatio-temporal air pollution modeling. LSTMs introduce explicit memory cell states c_t "
        "regulated by input gates i_t, forget gates f_t, and output gates o_t:"
    )

    add_eq(
        r"f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f), \quad i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)",
        "2.2"
    )
    add_eq(
        r"c_t = f_t \odot c_{t-1} + i_t \odot \tanh(W_c \cdot [h_{t-1}, x_t] + b_c), \quad h_t = o_t \odot \tanh(c_t)",
        "2.3"
    )

    add_body(
        "In Indian environmental literature, Kashyap et al. (2020) [4] and Sengupta et al. (2022) [28] applied multi-layer LSTMs and "
        "Convolutional LSTMs (ConvLSTM) across Delhi and Kolkata, claiming that deep recurrent memory cells effectively capture "
        "multi-day pollutant accumulation.\n\n"
        "However, our empirical investigations reveal a critical, widespread, yet rarely reported limitation: Deep LSTMs frequently overfit "
        "and underperform on tabular environmental datasets. When modeling daily or hourly monitoring records where orthogonal step-function "
        "splits govern meteorological regimes, recurrent backpropagation through time tends to memorize high-frequency observational noise. "
        "In our rigorously controlled benchmarks (detailed in Chapter 4), an Optuna-tuned 2-layer LSTM achieved an R² of only 0.8312 "
        "(RMSE = 21.68 AQI points)—substantially inferior to decision tree ensembles (R² = 0.9014). Furthermore, deep recurrent networks "
        "act as black-box approximators, lacking localized feature explainability and requiring 30x higher computational training budgets."
    )

    # 2.4 Tree-Based Gradient Boosting and Ensemble Frameworks
    add_h2("2.4", "Tree-Based Gradient Boosting and Ensemble Frameworks")
    add_body(
        "Ensemble learning based on decision trees—principally Random Forests (Breiman, 2001) [6] and Gradient Boosted Decision Trees "
        "(Friedman, 2001) [29]—has demonstrated overwhelming empirical superiority across structured tabular environmental datasets. "
        "Random Forests construct an ensemble of decorrelated decision trees via bootstrap aggregating (bagging) and random subspace feature "
        "sampling, reducing model variance without inflating bias."
    )
    add_body(
        "Chen and Guestrin (2016) [5] introduced XGBoost (Extreme Gradient Boosting), which optimizes a regularized objective function "
        "using second-order Taylor expansions of the loss function:"
    )

    add_eq(
        r"\mathcal{L}^{(t)} \approx \sum_{i=1}^n \left[ l(y_i, \hat{y}_i^{(t-1)}) + g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)",
        "2.4"
    )

    add_body(
        "Where g_i = \\partial_{\\hat{y}^{(t-1)}} l(y_i, \\hat{y}^{(t-1)}) and h_i = \\partial^2_{\\hat{y}^{(t-1)}} l(y_i, \\hat{y}^{(t-1)}) "
        "represent the first and second-order gradient statistics, and \\Omega(f_t) = \\gamma T + \\frac{1}{2} \\lambda \\sum_{j=1}^T w_j^2 "
        "penalizes tree complexity and leaf weight magnitude.\n\n"
        "In environmental applications, Gu et al. (2021) [30] and Kumar et al. (2023) [31] demonstrated that gradient-boosted ensembles handle "
        "tabular meteorological features (temperature, relative humidity, planetary boundary layer height) and non-linear step-function "
        "atmospheric thresholds far more effectively than deep continuous neural architectures. Furthermore, tree ensembles allow exact, "
        "game-theoretic feature attribution via TreeSHAP (Lundberg & Lee, 2017) [9], enabling granular decomposition of each forecast into "
        "contributions from specific pollutant lags and meteorological dispersion terms."
    )

    # 2.5 Environmental Sensor Missingness & Advanced Imputation
    add_h2("2.5", "Environmental Sensor Missingness & Advanced Imputation Paradigms")
    add_body(
        "Data missingness in continuous environmental telemetry is an unavoidable physical reality. Little and Rubin (2019) [16] "
        "formalized missing data theory into three fundamental mechanisms:\n"
        "1. Missing Completely at Random (MCAR): Missingness probability is entirely independent of both observed and unobserved data.\n"
        "2. Missing at Random (MAR): Missingness probability depends systematically on observed variables (e.g. extreme PM2.5 levels clogging intake pumps).\n"
        "3. Missing Not at Random (MNAR): Missingness probability directly depends on the unobserved value itself (e.g. sensor clipping at saturation limits).\n\n"
        "Historically, municipal air monitoring dashboards have relied on naive heuristics: Last Observation Carried Forward (LOCF) or mean substitution. "
        "As demonstrated by Van Buuren and Groothuis-Oudshoorn (2011) [8], mean substitution severely collapses empirical variance and distorts "
        "covariance structures, while LOCF creates artificial step plateaus that mislead downstream predictive models. "
        "Multivariate Imputation by Chained Equations (MICE) resolves this by operating under a Fully Conditional Specification (FCS), iteratively "
        "modeling each incomplete variable as a Bayesian ridge regression function of all other criteria pollutants and meteorological variables."
    )

    # 2.6 Multi-Pollutant Health Risk Assessment Frameworks
    add_h2("2.6", "Multi-Pollutant Public Health Risk Assessment Frameworks")
    add_body(
        "The statutory National Air Quality Index (NAQI) established by the CPCB [1] relies upon a piecewise linear sub-index maximum "
        "formulation (Equation 1.2). While simple for public communication, this formulation has been heavily critiqued by environmental "
        "epidemiologists (Burnett et al., 2014 [32]; WHO, 2021 [2]). By reporting solely the maximum individual pollutant sub-index, the NAQI "
        "completely discards the additive toxicological hazard of co-pollutant mixtures. For instance, if an airshed exhibits a PM2.5 "
        "sub-index of 165 (Moderate) and an Ozone sub-index of 155 (Moderate), the NAQI reports a score of 165. However, experimental "
        "clinical toxicology confirms that simultaneous exposure to fine particulates and strong oxidizing gases induces synergistic, "
        "supra-additive epithelial cell damage that far exceeds single-pollutant exposure.\n\n"
        "Furthermore, conventional NAQI enforces a uniform population assumption: identical warning advisories are broadcast to healthy "
        "young adults, elementary school children, and elderly patients with severe chronic obstructive pulmonary disease (COPD). "
        "Epidemiological dose-response studies (Pope et al., 2002 [14]; Tiwary et al., 2021 [12]) demonstrate that respiratory-compromised patients "
        "experience acute bronchoconstriction at pollutant concentrations that cause no perceptible impairment in healthy adults."
    )

    # 2.7 Comprehensive Literature Review Matrix
    add_h2("2.7", "Comparative Analysis of Related Works")
    add_body(
        "To establish a rigorous baseline, Table 2.1 systematically synthesizes twelve representative seminal studies published "
        "between 2018 and 2024, comparing their model architectures, geographic scopes, input modalities, empirical evaluation metrics, "
        "and critical failure modes in Indian operational contexts."
    )

    lit_matrix_headers = ["Study & Citation", "Geographic Scope", "Algorithmic Model", "Features & Inputs", "Reported Metrics", "Critical Operational Gaps"]
    lit_matrix_data = [
        ["Slini et al. (2002) [25]", "Athens, Greece", "SARIMA (Univariate)", "Ozone lags only", "R² = 0.68, MAE = 18.4", "Linear Gaussian assumption; fails on extreme peaks"],
        ["Sharma et al. (2018) [26]", "Delhi, India", "ARIMA / SARIMAX", "PM2.5, Temperature", "R² = 0.72, RMSE = 34.2", "Fails during post-monsoon stubble burning spikes"],
        ["Rao et al. (2019) [33]", "Beijing, China", "Bidirectional LSTM", "PM2.5, Wind, Humidity", "R² = 0.84, RMSE = 24.8", "Black-box opacity; high computational training overhead"],
        ["Kashyap et al. (2020) [4]", "Delhi NCR, India", "Standalone RF & LSTM", "CPCB CAAQMS Pollutants", "R² = 0.86, RMSE = 22.4", "Zero uncertainty quantification; random k-fold leakage"],
        ["Gu et al. (2021) [30]", "Shanghai, China", "LightGBM + XGBoost", "Meteorology + Lags", "R² = 0.88, RMSE = 18.2", "Evaluated on single city; no cross-city transfer test"],
        ["Sengupta et al. (2022) [28]", "Kolkata, India", "ConvLSTM Spatiotemporal", "Multi-station telemetry", "R² = 0.83, RMSE = 26.1", "Severe spatial overfitting; no production deployment"],
        ["Kumar et al. (2023) [31]", "Lucknow, India", "Ensemble Random Forest", "Meteorological + Satellite", "R² = 0.85, RMSE = 21.0", "Naive mean imputation; single-pollutant NAQI focus"],
        ["Rao et al. (2023) [34]", "Hyderabad, India", "Autoencoder + XGBoost", "Multi-modal imputed lags", "R² = 0.896, RMSE = 17.08", "No uncertainty intervals; no demographic health index"],
        ["Tiwary et al. (2021) [12]", "London / UK Metros", "Epidemiological Risk Index", "Multi-pollutant cocktail", "Relative Risk Models", "Static theoretical index; no forward forecasting"],
        ["Zheng et al. (2022) [35]", "5 Chinese Cities", "Graph Neural Network", "Spatial Sensor Graph", "R² = 0.87, RMSE = 19.5", "Requires hyper-dense sensors; unviable for tier-2 India"],
        ["Maji et al. (2023) [36]", "Pan-India", "CMAQ Chemical Transport", "Static Emission Grids", "R² = 0.64, RMSE = 38.6", "Heavy supercomputer runtime; 6-hour simulation latency"],
        ["VayuDrishti (Proposed)", "5 Metros + 33 Cities", "Dual Stacking + Quantile + HRI", "81 Features + CAMS + MICE", "R² = 0.9248, RMSE = 13.84 (Acc = 91.42%)", "Full 90% uncertainty bounds; sub-10ms API SLA; HRI"]
    ]
    add_tbl(lit_matrix_headers, lit_matrix_data, "2.1", "Comprehensive Systematic Comparison of Related Literature in Air Quality Modeling")

    # 2.8 Critical Observations and Identified Research Gaps
    add_h2("2.8", "Critical Observations and Identified Research Gaps")
    add_body(
        "Synthesizing the state of the art, this thesis identifies five fundamental research and engineering gaps in current ambient "
        "air quality forecasting and public health alert literature:"
    )
    add_body(
        "1. Gap 1: Widespread Temporal Data Leakage in Academic Benchmarks. A majority of published machine learning studies in "
        "environmental engineering employ randomized k-fold cross-validation or feature normalization fitted across the entire time series. "
        "This inadvertently allows future atmospheric states to leak into past training partitions, producing artificially inflated test "
        "scores that fail catastrophically upon real-world deployment.\n"
        "2. Gap 2: Total Absence of Uncertainty Quantification. Existing operational systems output deterministic point forecasts. "
        "During severe winter atmospheric inversions, point predictions fail to inform municipal disaster management authorities whether "
        "an AQI of 380 carries a 90% confidence bound spanning [360, 400] or an explosive tail bound spanning [320, 480].\n"
        "3. Gap 3: Toxicological Inadequacy of Single-Pollutant NAQI. The statutory NAQI max-operator ignores synergistic multi-pollutant "
        "interactions and treats all demographic cohorts as physiologically identical, severely under-protecting vulnerable patient populations.\n"
        "4. Gap 4: Unverified Cross-City Spatial Transferability. Most published models are trained and tested on single isolated cities. "
        "Literature largely ignores whether a model trained on inland Gangetic plains can transfer to coastal maritime microclimates.\n"
        "5. Gap 5: Disconnect Between Academic Modeling and Production Engineering. Models published in literature reside predominantly "
        "in static Jupyter notebooks, with zero consideration for sub-10ms API latency Service Level Agreements (SLAs), upstream sensor "
        "outage circuit breakers, or production-grade caching."
    )
