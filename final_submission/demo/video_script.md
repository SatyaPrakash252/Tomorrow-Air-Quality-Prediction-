# VayuDrishti: 3-Minute Demonstration Video Script & Voiceover

**Title:** VayuDrishti — Live System Demonstration  
**Target Duration:** 180 Seconds (03:00)  
**Pacing:** Clear, professional, academic cadence (~130 words per minute)  
**Voiceover Narrator:** Satyaprakash Rout (Lead) with Saipriya Patra (Clinical Segment)  
**Accompanying Video Recording:** `final_submission/demo/vayudrishti_live_demo.webp`

---

## Synchronized Audio-Visual Script

### [00:00 – 00:35] Scene 1: Introduction & National Telemetry Dashboard
**Visual:** Browser opens to `http://localhost:5173`. High-resolution dark-mode UI loads smoothly. National AQI telemetry cards light up across 38 cities. Cursor pans over Delhi, Mumbai, and Bhubaneswar.

**Voiceover (Satyaprakash):**  
*(Time: 00:00 - 00:35 | Word Count: 74)*  
> "Welcome to VayuDrishti—an AI-driven air quality forecasting and public health risk alert platform engineered for Indian metropolitan cities.
>
> What you are seeing is our live production dashboard running on React 19 and FastAPI. The platform ingests real-time ground-level CAAQMS telemetry alongside Copernicus atmospheric numerical models across 38 Indian cities.
>
> With an overall test R-squared of 0.8997 and sub-10-millisecond API response times, VayuDrishti transitions environmental protection from passive monitoring to forward-looking defense."

---

### [00:35 – 01:15] Scene 2: 72-Hour Multi-Horizon Forecast & Uncertainty Quantification
**Visual:** Click into the 'City Forecast' view. Select Delhi. The forecast trajectory line renders dynamically with shaded 90% confidence interval bands across 24h, 48h, and 72h horizons. Hovering over a +48h node reveals prediction bounds. Scroll down to show criteria pollutant breakdown.

**Voiceover (Satyaprakash):**  
*(Time: 00:35 - 01:15 | Word Count: 88)*  
> "Let us examine Delhi. Traditional portals only report what happened yesterday. VayuDrishti forecasts air quality up to 72 hours into the future using an Optuna-tuned Stacking Ensemble of XGBoost and Random Forest.
>
> Notice the shaded blue envelope surrounding the forecast line. This represents our pinball-loss calibrated 90% prediction intervals. In held-out empirical testing across 2,368 days, this interval achieved 90.01% coverage, giving municipal planners an honest measure of atmospheric volatility.
>
> Below, we break down individual criteria pollutants and show TreeSHAP explainability scores, proving that meteorological lag and ventilation index drive these forecasts."

---

### [01:15 – 01:55] Scene 3: Health Risk Index & Demographic Exposure Simulator
**Visual:** Switch to 'Health Risk Index' tab. Select Bhubaneswar. The AQI is currently 118 (Moderate). Navigate to the interactive Atmospheric Exposure Simulator slider. Drag the exposure slider from 118 to 215. The risk cards for Children, Elderly, and Respiratory Patients turn amber and red in real time.

**Voiceover (Saipriya):**  
*(Time: 01:15 - 01:55 | Word Count: 91)*  
> "I am Saipriya Patra, presenting our Health Risk Index.
>
> Traditional NAQI relies solely on the worst single pollutant, ignoring toxic cocktail effects and treating all citizens as identical.
>
> Our HRI uses an exponential supra-additive formula with physiological vulnerability multipliers. Watch as I interact with the live exposure simulator: as ambient exposure increases to 215, healthy adults experience Moderate strain, but children and asthmatic patients are immediately escalated into High Risk and Severe Medical Hazard.
>
> The clinical advisory panel updates instantly, advising immediate bronchodilator readiness and classroom air filtration."

---

### [01:55 – 02:30] Scene 4: Real-Time Alert Center & Circuit Breaker Resilience
**Visual:** Click on 'Alert Center'. Filter through active alerts for Delhi and Northern industrial corridors. Open developer console or network tab showing `/forecast` calls returning in 2.4 milliseconds.

**Voiceover (Satyaprakash):**  
*(Time: 01:55 - 02:30 | Word Count: 79)*  
> "The Alert Center provides automated municipal decision support up to three days ahead, dispatching alerts stratified by demographic vulnerability.
>
> Crucially, our backend is built for extreme resilience. If primary CAAQMS sensors disconnect, an automated circuit breaker falls back to Copernicus global atmospheric telemetry in just 42 milliseconds.
>
> Under benchmark load testing with 50 concurrent requests, our FastAPI endpoints maintain an average latency of 2.41 milliseconds with zero dropped requests."

---

### [02:30 – 03:00] Scene 5: Research Ledger, Verification & Closing
**Visual:** Click 'Research & Models' tab. Scroll through the verified ground-truth metrics table and citations. Switch briefly to Swagger API docs at `http://127.0.0.1:8000/docs`. Return to landing overview.

**Voiceover (Satyaprakash):**  
*(Time: 02:30 - 03:00 | Word Count: 68)*  
> "Every metric you have seen today—from our MICE imputation RMSE of 2.14 to our test R-squared of 0.8997—is strictly tied to our verified ground-truth ledger and reproducible via a single shell script.
>
> With 14 automated Pytest test suites passing, VayuDrishti stands ready for deployment to protect vulnerable communities across urban India.
>
> Thank you for your time and attention."

---

## Production Recording Metadata
- **Resolution:** 1920 × 1080 (Full HD, 60fps)
- **Audio Codec:** AAC 48kHz, 16-bit Stereo
- **Video Format:** WebP / MP4
- **Local Recording Path:** `final_submission/demo/vayudrishti_live_demo.webp`
- **Total Speech Duration:** 2 minutes 58 seconds
- **Total Word Count:** 400 words
