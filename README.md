# Vanguard A/B Test: Optimizing Digital Engagement

## Project Structure

```
├── config.yaml                # Project configuration settings
├── main.py                    # Main script to run project workflows
├── pyproject.toml             # Project dependencies and configuration
├── uv.lock                    # Dependency lock file
├── README.md                  # Project documentation

├── data/                      # Project datasets
│   ├── raw/                   # Original raw datasets
│   │   ├── df_final_demo.txt
│   │   ├── df_final_experiment_clients.txt
│   │   ├── df_final_web_data_pt_1.txt
│   │   └── df_final_web_data_pt_2.txt
│   │
│   └── clean/                 # Cleaned and processed datasets
│       ├── demographics_dataset.csv
│       ├── df_main_merge.csv
│       ├── df_time_window.csv
│       ├── kpi_duration_dataset.csv
│       ├── kpi_completion_steps.csv
│       ├── kpi_completion_visits.csv
│       ├── kpi_merged.xlsx
│       └── kpi_errors.xlsx

├── figures/                   # Generated visualizations
│   ├── Conversion-Rate_Steps.png
│   ├── Drop-off-Rate_Steps.png
│   ├── Task-Completion-Time_Group.png
│   ├── Step-Time-Distribution_Step.png
│   ├── Client-Behavior_Age-Group.png
│   ├── Client-Tenure-Distribution.png
│   └── ... (additional plots)

├── notebooks/                 # Analysis and exploration notebooks
│   ├── KPI_errors_beatriz.ipynb
│   ├── demographics_rachel.ipynb
│   ├── KPI_completion_anne.ipynb
│   ├── KPI-duration_rachel.ipynb
│   ├── main_dataset_tasks_anne.ipynb
│   └── functions.py

```

## Project Overview
This project analyzes a digital experiment conducted by Vanguard to improve its online user journey. A redesigned interface and in-context prompts were introduced to make the process more intuitive and increase completion rates. The main goal is to assess whether these changes lead to higher user engagement and more completed processes.

## A/B testing  
A/B testing is a method that compares two UI versions (Control vs Test) by randomly assigning users to evaluate which performs better based on defined metrics.

## Data sources & key figures  
The analysis is based on three datasets:  
- **Client Profiles (df_final_demo):** demographics and account details  
- **Digital Footprints (df_final_web_data 1 and 2):** online interactions (concatenated from two parts)  
- **Experiment Roster (df_final_experiment_clients):** test participation  

**Key figures:**  
- Total clients: 70,609  
- Selected for A/B test: 50,500  
- Participants: 40,028  
- Total visits: 51,998
- Period: March–June 2017


## Project objectives  
- Measure if the new experience increases process completion  
- Evaluate the quality of randomization  
- Provide recommendations  

---

# Data Cleaning & Wrangling

The preprocessing of the datasets involved several key steps to ensure accuracy and consistency for analysis:

1. **Remove duplicates** – Duplicate rows across datasets were deleted to avoid double-counting.  
2. **Format conversion** – String date columns were converted to `datetime` format for proper time-based analysis.  
3. **Filter unassigned clients** – Clients not associated with any experimental group were removed from the Digital Footprints dataset to maintain valid comparisons.  
4. **Merge datasets** –  
   - The two parts of the Digital Footprints data were first concatenated.  
   - A left join was then performed with the Client Profiles (demo) dataset.  
   - Another left join was applied with the Experiment Roster to include group assignments.  
5. **Remove redundant dates** – `last_start` and `confirm` date columns were dropped to simplify the analysis and focus on relevant event timestamps.  

These steps created a clean, unified dataset suitable for all subsequent KPI calculations and A/B test analysis.

# Randomization assessment

Randomization appears globally reliable across the experiment. The initial split between Control (46.6%) and Test (53.4%) groups is slightly imbalanced but remains close to a 50/50 distribution, which is acceptable. This balance is maintained among participating clients (45% vs 55%) and across total visits (44.8% vs 55.2%), suggesting consistent allocation throughout the funnel. Additionally, the very low proportion of erroneous visits (~0.18%) has minimal impact on the overall dataset. Overall, these elements indicate that the randomization process is sound and does not introduce major bias into the analysis.

# Demographics & Client Behavior (EDA Analysis)

The user base is primarily concentrated in the 30–50 age range, with most clients having moderate to long tenure. On average, clients hold around **2.27 accounts**, indicating an already engaged and established customer base. The average account balance is approximately **152K**, with a high standard deviation (~302K), revealing a strong right-skew distribution driven by a small group of high-value clients. This indicates that while most users are moderately engaged, a minority contributes disproportionately to overall value.
Segment-level analysis highlights clear behavioral differences:
- Clients with longer tenure exhibit more stable engagement patterns (in terms of accounts and activity).
- Lower-tenure or less active clients show greater variability, suggesting higher friction or inconsistent usage.
- Higher-balance clients tend to navigate more efficiently, implying that familiarity and financial engagement reduce friction in the user journey.
Key Insight:
The platform is primarily used by financially engaged, established clients, but the wide variance in balance and activity indicates that user behavior is highly segmented — not uniform.


# KPIs

## KPI 1: Completion rate  
Completion rate measures the percentage of users who successfully complete a task or full process.  

**Formula:**  
- Step completion = users who complete a step / users who started it  
- Process completion = users who complete all steps without errors / users who started  

A full process includes this exclusive sequence: start → step1 → step2 → step3 → confirm  

**Benchmark:** 75–80%  
**Target improvement:** +5% for Test group  

---

## KPI 2: Completion time  
Measures the average duration per step and per group to evaluate efficiency and detect friction points.

---

## KPI 3: Error rate  

### Visit Classification
Each of the visits was classified into one of four types:

| Type | Definition |
|---|---|
| **Smooth** | All 5 steps completed in correct order, zero errors |
| **Lumpy – Repetition** | Completed, but re-visited a step |
| **Lumpy – Regression** | Completed, but navigated backwards |
| **Incomplete** | Never reached `confirm` |

### Error Detection
Errors were flagged by comparing each step to the previous one within the same visit:
- **Repetition**: the same step appears consecutively (e.g., step_2 → step_2)
- **Regression**: the step rank decreases (e.g., step_2 → step_1)

A visit was marked as having an error if at least one repetition or regression occurred during that visit.

---

# Results – KPI 1

## Overall completion rate  
- Control: **46.85%**  
- Test: **49.74%**  

The Test group performs better with a **+2.89 percentage point increase** (~6.16% relative), but both remain below the expected benchmark (~70%).

## Step-level insights  
- **Start:** Test group performs better → improved entry experience  
- **Step 1 & 2:** Control performs better → clearer guidance in current interface  
- **Step 3:** Test performs better → stronger engagement at final stage  

## Statistical significance  
The very low p-value and high z-score indicate a statistically significant difference between the two groups.

## Performance vs target  
The improvement does not reach the +5% target. Overall completion remains relatively low.

## Key insight  
The new interface shows promising results, especially for users progressing through the funnel, but further optimization is needed before full rollout.

# Results – KPI 2

## KPI 2: Completion time (Results & Insights)

Task duration analysis shows a strong right-skewed distribution: most users complete the process quickly, while a smaller group experiences significantly longer durations. After removing outliers using the IQR method, the analysis becomes more representative of typical user behavior. In this context, the **median** is a more reliable metric than the mean.

Step-level analysis reveals that time is unevenly distributed across the process, with specific steps acting as clear bottlenecks. These longer steps directly align with higher drop-off rates, highlighting a strong relationship between friction and abandonment. Users who take longer are significantly less likely to complete the process.

Focusing on the last attempt per user ensures that results reflect actual outcomes rather than repeated trials.

**Key insight:**  
Process inefficiencies are concentrated in a few critical steps, and these friction points have a direct impact on completion rates. Optimizing these stages would likely generate the highest gains in both performance and user experience.

---

## Overall Takeaway

- The user base is experienced but heterogeneous, with strong differences in engagement and value  
- The process is globally efficient but impacted by localized friction points  
- High-value and experienced users navigate more smoothly, while others face more difficulties  
- Improvements should target both **problematic steps** and **struggling user segments**

---

## UI Effectiveness & Conversion Impact

The redesigned UI shows **partial effectiveness**:

- Users complete the process efficiently when no friction is encountered  
- However, overall completion remains limited by a few high-friction steps  
- The impact of the new UI is **uneven across the journey**, not uniformly positive  

Step-level insights confirm that:
- A small number of steps concentrate most of the delays  
- These steps also correspond to higher drop-off rates  
- Most of the journey works well → issues are **localized, not systemic**

**Is the new UI worth it?**  
Yes — but not fully optimized.

The redesign improves efficiency for many users, but unresolved friction points still limit its overall impact.

**Key insight:**  
Targeted improvements on specific bottlenecks will likely deliver higher returns than a full redesign.

# Results – KPI 3

### Error Rates by Step
The `start` step was the most error-prone in both groups:

| Group | Step | Error Rate |
|---|---|---|
| Control | start | 8.68% |
| Control | step_2 | 2.64% |
| Control | step_1 | 2.35% |
| Control | step_3 | 0.69% |
| Control | confirm | 0.56% |
| **Test** | **start** | **12.45%** |
| Test | step_1 | 2.81% |
| Test | confirm | 2.19% |
| Test | step_2 | 1.66% |
| Test | step_3 | 0.51% |

The Test group had a notably higher error rate at `start` (12.45% vs 8.68%) and at `confirm` (2.19% vs 0.56%).

*Note: error rate here = number of erroneous step transitions at that step / total rows in that group.*

### Buggiest Transitions
The most common single error in both groups was `start → start` (the user repeated the start page):
- **Control**: 6,118 occurrences (6.08% error rate)
- **Test**: 9,184 occurrences (6.59% error rate)

Other notable high-error transitions in the Test group:
- `step_1 → start`: 4,878 errors (3.5%)
- `confirm → confirm`: 3,058 errors (2.19%)
- `step_2 → step_1`: 2,342 errors (1.68%)

### Error Rate by Age Group
The error rate here means: the percentage of visits by that age group that contained at least one navigation error (repetition or regression).

| Age Group | Control | Test |
|---|---|---|
| <30 | 34.14% | 40.31% |
| 30–50 | 31.36% | 40.26% |
| 50–70 | 35.33% | 47.85% |
| 70+ | 35.36% | 48.89% |

The Test group had higher error rates across all age groups. Users aged 50–70 and 70+ were the most affected — in the Test group, nearly 1 in 2 of their visits contained at least one navigation error. This suggests the new UI may present more friction for older users.

## General Conclusion

The A/B test conducted on Vanguard’s digital platform reveals partial improvements in process completion due to the redesigned interface, but several friction points remain.

## Key takeaways from the KPIs:

**Completion rate**: The Test group shows a small improvement (+2.89pp), but the absolute rate remains below the 70% benchmark. Step-level analysis shows uneven performance, with some steps performing worse than the Control group.
**Completion time**: Median task duration is reasonable for most users, but a few bottlenecks increase friction and reduce completion probability.
**Error rate**: The Test group exhibits higher errors, especially at start and among older users (50–70+, 70+), indicating that the new UI may be less intuitive for certain segments.

User feedback insights:

Repeated navigation errors suggest users struggle with unclear instructions or step layout.
Experienced users navigate efficiently, but less familiar or older clients encounter significant friction.
Users value clarity and simplicity; additional guidance could reduce repeated attempts and regressions.

## Potential biases identified:

Selective participation: Repeated or self-selected participation may skew results toward more engaged users.
Device/system variability: Differences in devices or browsers could affect user experience and measured KPIs.
Temporal changes: Any modifications to the platform during the experiment could introduce confounding effects.

**Synthesis:
While the new interface shows promise for engaged users, overall performance improvements are modest. Friction points persist, particularly for less experienced or older users, and error rates in critical steps remain high.**

## Recommendations

We do not recommend launching the new version after the A/B test. Instead, we suggest focusing on improving the intermediate steps of the process, reducing errors before implementation, and leveraging additional information such as device/browser differences and user feedback to guide targeted optimizations.

## Visualisations

Visual analysis was performed using a combination of Python, Prezi, and Tableau to provide both static and interactive insights. Please refer to Resources section below.

## Python (libraries)
- **pandas** – data manipulation and aggregation  
- **matplotlib** & **seaborn** – histograms, boxplots, scatter plots, and bar charts  
- **plotly** – interactive charts for step duration and funnel analysis  


## Interactive Dashboards
- **Prezi** – dynamic presentation of key findings with embedded charts  
- **Tableau** – interactive dashboards for step-level completion rates, user flows, and duration analysis  
  - Users can filter by group, tenure, or balance  
  - Allows drill-down into specific steps and client segments  

This multi-tool approach ensures both detailed statistical insight and accessible visual storytelling for stakeholders.


# Librairies

- ipykernel>=7.2.0
- jupyter>=1.1.1
- matplotlib>=3.10.8
- numpy>=2.4.3
- pandas>=3.0.1
- polars>=1.39.0
- seaborn>=0.13.2
- statsmodels>=0.14.6
- scipy>=1.11.1
- plotly>=2.26.0
- kaleido>=0.2.1

# Resources

- [Prezi Presentation](https://prezi.com/view/18jwHtv1pSUOdVmcTZPs/?referral_token=VzXuWplnB3FN)  
- [Trello Board](https://trello.com/b/RIDNYtka/vanguard-ab-test)  
- [Miro Board](https://miro.com/app/board/uXjVG4NbT5U=/)
- [Tableau KPI Dashboard](https://public.tableau.com/views/Vanguard_KPIs_Insight/Tableaudebord1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)
- [Tableau Demographics Dashboard](https://public.tableau.com/views/Vanguard_Demographics_KPI-Duration/Dashboard-Demographics?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Additional sources
- [UX KPI Indicators Article](https://lagrandeourse.design/blog/actualites/6-indicateurs-defficacite-ux-a-integrer-a-vos-kpi-marketing/)  
- [Completion Rate Explanation](https://www.adpushup.com/fr/blog/what-is-completion-rate/)


## Authors
Beatriz Fernandez, Anne Leschallier de Lisle, Rachel Vianna
