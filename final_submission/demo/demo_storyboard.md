# VayuDrishti: 3-Minute Live Demonstration Storyboard

**Platform Name:** VayuDrishti (वायुदृष्टि)  
**Live URL:** `http://localhost:5173` (Frontend) | `http://127.0.0.1:8000` (Backend API)  
**Target Duration:** Exactly 3 Minutes (180 Seconds)  
**Demonstrators:** Satyaprakash Rout (Lead), Likuna Swain, Ch Saipriya Patra, Arpeet Barik  
**Recorded Artifact:** `final_submission/demo/vayudrishti_live_demo.webp`

---

## Storyboard Overview & Scene Breakdown

```text
+-----------------------------------------------------------------------------------+
| Scene 1: 0:00 - 0:35 | Landing Overview & 38-City Live National Telemetry         |
| Scene 2: 0:35 - 1:15 | 72-Hour Multi-Horizon Forecast & Uncertainty Quantile Bands|
| Scene 3: 1:15 - 1:55 | Demographic Health Risk Simulator & Vulnerability Toggles  |
| Scene 4: 1:55 - 2:30 | Real-Time Triage Alert Center & Upstream Circuit Breaker   |
| Scene 5: 2:30 - 3:00 | Research Ledger, API Documentation & Production SLAs       |
+-----------------------------------------------------------------------------------+
```

---

## Detailed Scene Walkthrough

### SCENE 1: National Telemetry & Landing Dashboard (0:00 – 0:35)
- **Visual:** Browser displays the VayuDrishti landing dashboard (`/`). High-contrast dark-mode interface with live AQI status cards across Delhi, Mumbai, Bengaluru, Chennai, Hyderabad, and Bhubaneswar.
- **Action:**
  1. Cursor hovers over national metric cards showing current test $R^2 = 0.8997$, RMSE $= 16.78$, and sub-10ms API latency.
  2. Cursor clicks on the city search box and highlights Delhi (AQI: Severe/Very Poor).
- **Audio Cue:** *"Welcome to the live demonstration of VayuDrishti. Here on the main overview, the platform ingests live telemetry from CPCB CAAQMS stations and Copernicus CAMS global atmospheric reanalysis across 38 Indian cities..."*
- **Key Visual Asset:** `final_submission/demo/landing_hero.png`

---

### SCENE 2: Multi-Horizon Forecasting & Uncertainty Quantification (0:35 – 1:15)
- **Visual:** City Forecast Dashboard (`/forecast`) with Delhi active.
- **Action:**
  1. Demonstrator toggles between the 24-hour, 48-hour, and 72-hour forecast horizon tabs.
  2. Demonstrator points to the smooth forecast trajectory line plotted alongside the shaded **90% confidence interval band** ($\hat{y}_{0.05}$ to $\hat{y}_{0.95}$).
  3. Cursor hovers over a forecast node at $+48\,\text{hours}$, displaying the tooltip: `Median AQI: 312, 90% Range: [284 - 346]`.
  4. Scroll down to show criteria pollutant breakdown (PM2.5: $184\,\mu\text{g/m}^3$, PM10: $276\,\mu\text{g/m}^3$, NO2: $64\,\mu\text{g/m}^3$) and TreeSHAP feature importance rankings.
- **Audio Cue:** *"Unlike static single-point estimators, VayuDrishti models temporal decay and atmospheric uncertainty. The shaded band shows our pinball-loss calibrated 90% prediction intervals, maintaining an empirical coverage of 90.01% on held-out test data..."*
- **Key Visual Asset:** `final_submission/demo/pollutant_breakdown.png`

---

### SCENE 3: Demographic Health Risk Simulator (1:15 – 1:55)
- **Visual:** Health Risk Index Page (`/risk`).
- **Action:**
  1. Demonstrator switches active city to **Bhubaneswar** (`AQI = 118`, Moderate).
  2. Demonstrator navigates to the **Real-Time Atmospheric Exposure Simulator** slider.
  3. Demonstrator drags the exposure slider upwards from 118 to 215.
  4. Watch real-time card updates:
     - **General Public ($\beta=1.0$):** Rises to `HRI = 58.2` (Tier 3: High Risk).
     - **Children & Elderly ($\beta=1.3$):** Rises to `HRI = 75.7` (Tier 4: Severe Hazard).
     - **Respiratory Patients ($\beta=1.6$):** Hits `HRI = 93.1` (Tier 4: Severe Hazard, red flashing border).
  5. The clinical advisory panel updates immediately, issuing targeted recommendations: *'Immediate bronchodilator readiness; discontinue all outdoor physical education classes.'*
- **Audio Cue:** *"This is the core public health breakthrough: our continuous, non-linear Health Risk Index. Watch how adjusting the exposure level impacts different demographic groups. While a healthy adult experiences Moderate strain, an asthmatic patient is immediately escalated to Severe Medical Hazard..."*
- **Key Visual Asset:** `final_submission/demo/health_risk_index.png`

---

### SCENE 4: Real-Time Alert Center & Circuit Breaker Resilience (1:55 – 2:30)
- **Visual:** Alert Center Dashboard (`/alerts`).
- **Action:**
  1. Filter alerts by severity: All, Critical/Severe, High Risk.
  2. Open an active alert card for Delhi NCR: displays predicted peak time (06:00 AM next morning), dominant pollutant ($\text{PM}_{2.5}$ concentration $210\,\mu\text{g/m}^3$), and recommended municipal mitigation (anti-smog water guns, heavy vehicle diversion).
  3. Briefly open terminal or browser developer network tab: show API response latency of `/forecast` at **2.41 ms** with zero 500 errors.
- **Audio Cue:** *"The Alert Center provides automated municipal decision support up to 72 hours ahead. Behind the scenes, if ground sensors fail, our upstream circuit breaker seamlessly switches to Copernicus atmospheric telemetry in 42 milliseconds, guaranteeing zero downtime..."*
- **Key Visual Asset:** `final_submission/demo/alert_center.png`

---

### SCENE 5: Research Ledger, API Documentation & Wrap-Up (2:30 – 3:00)
- **Visual:** Research & Methodology View (`/about`) and Swagger API Docs (`/docs`).
- **Action:**
  1. Show the live benchmark comparison table verifying test metrics ($R^2 = 0.8997$, MICE RMSE $= 2.14$, Autoencoder MSE $= 0.0084$).
  2. Show formal citations linking CPCB, WHO 2021, and IEEE publications.
  3. Switch to `http://127.0.0.1:8000/docs` displaying the 9 interactive FastAPI endpoints.
- **Audio Cue:** *"Every single number displayed on this dashboard is backed by our single-source-of-truth ground truth ledger. VayuDrishti is fully functional, fully tested with 14 passing automated test suites, and ready for municipal evaluation. Thank you."*
- **Key Visual Asset:** `final_submission/demo/research_and_models.png`

---

## Technical Fallback Plan for Panel Presentation

| Failure Mode | Automated Detection | Fallback Action During Live Presentation |
| :--- | :--- | :--- |
| **Local Port Conflict (5173 / 8000)** | Application fails to bind | Run `./final_submission/run_all.ps1` to re-verify ports and launch on alternate ports. |
| **External Internet Dropout** | External CAAQMS / CAMS API times out | Circuit breaker automatically switches to cached local telemetry and offline mock engine; UI displays yellow 'Offline Resilient Mode' badge. |
| **Browser Rendering Crash** | Browser tab freezes | Open the pre-recorded 300 DPI artifact screenshots in `final_submission/demo/` or play `final_submission/demo/vayudrishti_live_demo.webp`. |
