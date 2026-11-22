# VayuDrishti: Open Questions, Audit Discrepancies & Panel Honest Disclosures

**Academic Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Date:** September / October 2026  
**Document Purpose:** Transparently document technical discrepancies against earlier exploratory notes, empirical limitations, and items requiring explicit student team follow-up.

---

## 1. Pipeline Discrepancies vs. Early Exploratory Notes

| Component / Metric | Early Walkthrough / Informal Note Claim | Verified Ground Truth (`FACTS.md`) | Honest Technical Reason & Resolution |
| :--- | :--- | :--- | :--- |
| **Model Selection (LSTM)** | Informally assumed LSTM would improve multi-day memory. | Standalone LSTM ($\text{RMSE} = 21.68$) and Tri-Ensemble ($\text{RMSE} = 18.55$) performed worse than the tree ensemble ($\text{RMSE} = 16.64$). | Deep recurrent networks overfit on 12,042 tabular daily samples with strong tabular lag autocorrelations. Tree ensembles handle abrupt meteorological shifts much better. **Resolution:** Proposed architecture is the Dual Stacking Ensemble (RF + XGBoost); LSTM is openly documented as evaluated-and-excluded. |
| **Prediction Interval Coverage** | Assumed 90% confidence interval would uniformly cover $\ge 90\%$ in all cities. | Delhi ($87.64\%$) and Mumbai ($88.56\%$) fall slightly below $90.0\%$, though overall is $90.01\%$. | Winter inversion episodes in Delhi cause extreme non-Gaussian tail spikes, while Mumbai experiences maritime boundary layer shifts. **Resolution:** Reported plainly without artificial widening. |
| **Statistical Significance** | An earlier slide informally mentioned $p < 0.01$ across all tests. | Paired Student's $t$-test achieves $t = -3.722, p = 0.0002 < 0.01$; Wilcoxon achieves $W = 1,263,583.0, p = 3.003 \times 10^{-5} < 0.01$. | Earlier runs on smaller slices had $t$-test around $p = 0.027$. On the full held-out test set ($N=2,368$), both tests reach statistical significance ($p < 0.01$). |
| **Cross-City Generalization** | Informally hoped regional models could generalize pan-India with $R^2 > 0.80$. | Leave-One-City-Out (LOCO) mean $R^2 = 0.7054$; Chennai collapses to $R^2 = 0.5155$. | Atmospheric chemistry, local industrial point sources, and coastal microclimates cannot be transferred purely via inland features. **Resolution:** Justifies Two-Tier architecture (Tier 1: Trained ML for 5 metros; Tier 2: Copernicus CAMS atmospheric modeling for 33 live-only cities). |
| **Health Risk Multipliers** | Could be mistaken for clinically measured patient parameters. | Design assumptions based on physiological literature ($1.0, 1.3, 1.6$). | Multipliers reflect relative biological vulnerability (reduced lung capacity, developing airways), not calibrated dose-response curves. **Resolution:** Labelled explicitly as advisory risk design assumptions with full sensitivity analysis. |

---

## 2. Items Requiring Manual Student Action (University Administrative Policy)

The following deliverables and requirements cannot be synthesized or falsified by an AI agent and must be physically performed by the four project members:

1. **Individual Contribution Form:**
   - Appendix of the thesis and Presentation Backup slides contain blanks for the four team members (Satyaprakash Rout, Likuna Swain, Ch Saipriya Patra, Arpeet Barik) to allocate their personal workload percentages and module signatures.
2. **Official Plagiarism Check (Turnitin / DrillBit):**
   - The team must submit `Project_Report.docx` to the CGU central library / departmental coordinator to generate the official university plagiarism certificate (< 15%). We have provided a strict local n-gram overlap precheck in `thesis/plagiarism_precheck.md`.
3. **Physical Signatures:**
   - Bonafide Certificate, Approval Certificate, and Declaration signature and date lines must be signed in blue ink by the students, Faculty Guide (Prof. Soumya Sahoo), HOD, and External Examiners.
4. **Printing & Soft Binding:**
   - 6 total copies (4 students + 2 guide/department) soft-bound with colored spine and white front cover per department guidelines by 05-10-2026.
5. **Formal Conference Manuscript Submission:**
   - The team, with Prof. Soumya Sahoo's written endorsement, must submit `paper/manuscript.pdf` to one of the 5 verified IEEE/Springer venues listed in `paper/venue_notes.md` and archive the communication acknowledgement.
