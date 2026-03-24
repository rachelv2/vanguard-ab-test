# Vanguard A/B Test: Optimizing Digital Engagement

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

A full process includes: start → step1 → step2 → step3 → confirm  

**Benchmark:** 75–80%  
**Target improvement:** +5% for Test group  

---

## KPI 2: Completion time  
Measures the average duration per step and per group to evaluate efficiency and detect friction points.

---

## KPI 3: Error rate  
(To be completed)

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

(To be completed)

# General conclusion

(To be completed)

# Recommendations

(To be completed)

## Visualisations

Visual analysis was performed using a combination of Python, Prezi, and Tableau to provide both static and interactive insights. Please refer to Resources section.

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

# Resources

- [Prezi Presentation](https://prezi.com/view/18jwHtv1pSUOdVmcTZPs/?referral_token=VzXuWplnB3FN)  
- [Trello Board](https://trello.com/b/RIDNYtka/vanguard-ab-test)  
- [Miro Board](https://miro.com/app/board/uXjVG4NbT5U=/)
- [Tableau Dashboard](https://public.tableau.com/shared/SG3BSNRSS?:display_count=n&:origin=viz_share_link)


## Additional sources
- [UX KPI Indicators Article](https://lagrandeourse.design/blog/actualites/6-indicateurs-defficacite-ux-a-integrer-a-vos-kpi-marketing/)  
- [Completion Rate Explanation](https://www.adpushup.com/fr/blog/what-is-completion-rate/)


## Authors
Rachel Vianna, Anne Leschallier de Lisle, Beatriz Fernandez
