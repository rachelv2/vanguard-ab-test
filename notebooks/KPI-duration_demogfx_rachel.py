"""Reusable analysis functions from Rachel's demographics and duration KPI notebooks.

This module groups together the notebook logic that lends itself well to
refactoring into reusable functions, especially for:
- client demographic segmentation
- active-client filtering
- last-attempt / visit-window preparation
- task duration KPIs
- step-level timing KPIs
- funnel conversion and drop-off analysis
- outlier removal for visit duration analysis

The functions are written to be notebook-friendly: they return DataFrames or
Series that can be displayed directly and can also be chained into plots.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Demographics notebook helpers
# -----------------------------------------------------------------------------

def filter_active_clients(
    df_demo: pd.DataFrame,
    df_time_window: pd.DataFrame,
    client_col: str = "client_id",
) -> pd.DataFrame:
    """Keep only demographic rows for clients who used the online process.

    Parameters
    ----------
    df_demo : pd.DataFrame
        Demographic dataset containing one row per client.
    df_time_window : pd.DataFrame
        Process dataset containing at least the client identifier.
    client_col : str, default "client_id"
        Name of the client identifier column shared by both datasets.

    Returns
    -------
    pd.DataFrame
        Filtered copy of the demographic dataset.
    """
    active_clients = df_time_window[client_col].dropna().unique()
    return df_demo[df_demo[client_col].isin(active_clients)].copy()



def clean_gender_labels(
    df: pd.DataFrame,
    gender_col: str = "gendr",
    mapping: dict | None = None,
) -> pd.DataFrame:
    """Standardize abbreviated gender labels.

    Defaults:
    - M -> Male
    - F -> Female
    - U -> Other/Unknown
    """
    if mapping is None:
        mapping = {"M": "Male", "F": "Female", "U": "Other/Unknown"}

    df = df.copy()
    df[gender_col] = df[gender_col].replace(mapping)
    return df



def add_binned_group(
    df: pd.DataFrame,
    source_col: str,
    bins: Sequence[float],
    labels: Sequence[str],
    new_col: str,
    right: bool = True,
) -> pd.DataFrame:
    """Add a categorical banded column using pandas.cut."""
    df = df.copy()
    df[new_col] = pd.cut(df[source_col], bins=bins, labels=labels, right=right)
    return df



def add_activity_metric(
    df: pd.DataFrame,
    calls_col: str = "calls_6_mnth",
    logons_col: str = "logons_6_mnth",
    new_col: str = "activity",
) -> pd.DataFrame:
    """Create a simple engagement metric as calls + logons over 6 months."""
    df = df.copy()
    df[new_col] = df[calls_col].fillna(0) + df[logons_col].fillna(0)
    return df



def segment_client_by_age(
    age: float,
    young_cutoff: int = 30,
    adult_cutoff: int = 60,
) -> str:
    """Return an age-based client segment label for a single age value."""
    if pd.isna(age):
        return "Unknown"
    if age < young_cutoff:
        return "Young"
    if age < adult_cutoff:
        return "Adults"
    return "Senior"



def add_client_segment(
    df: pd.DataFrame,
    age_col: str = "clnt_age",
    new_col: str = "segment_client",
) -> pd.DataFrame:
    """Add age-based client segment labels to a dataframe."""
    df = df.copy()
    df[new_col] = df[age_col].apply(segment_client_by_age)
    return df



def summarize_client_behavior_by_group(
    df: pd.DataFrame,
    group_col: str = "age_group",
    client_col: str = "client_id",
    metrics: Iterable[str] = ("bal", "activity", "clnt_tenure_yr"),
) -> pd.DataFrame:
    """Aggregate client count and mean behavior metrics by a grouping column."""
    agg_dict = {client_col: "count", **{metric: "mean" for metric in metrics}}
    summary = (
        df.groupby(group_col)
        .agg(agg_dict)
        .rename(columns={client_col: "num_clients"})
    )
    return summary



def normalize_columns(
    df: pd.DataFrame,
    columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Normalize selected numeric columns by dividing each by its own max value."""
    df = df.copy()
    if columns is None:
        columns = list(df.select_dtypes(include=np.number).columns)

    for col in columns:
        max_val = df[col].max()
        if pd.notna(max_val) and max_val != 0:
            df[col] = df[col] / max_val
    return df


# -----------------------------------------------------------------------------
# KPI duration notebook helpers
# -----------------------------------------------------------------------------

def prepare_web_data(
    df_web: pd.DataFrame,
    datetime_col: str = "date_time",
) -> pd.DataFrame:
    """Ensure the web event timestamp column is parsed as datetime."""
    df_web = df_web.copy()
    df_web[datetime_col] = pd.to_datetime(df_web[datetime_col])
    return df_web



def drop_missing_demographics(df_demo: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with any missing values from the demographics dataframe."""
    return df_demo.dropna().copy()



def drop_missing_variation(
    df_experiment: pd.DataFrame,
    variation_col: str = "variation",
) -> pd.DataFrame:
    """Keep only experiment rows where the A/B test variation is known."""
    return df_experiment.dropna(subset=[variation_col]).copy()



def extract_last_attempt_window(
    df_web: pd.DataFrame,
    client_col: str = "client_id",
    visit_col: str = "visit_id",
    step_col: str = "process_step",
    datetime_col: str = "date_time",
    start_step: str = "start",
) -> pd.DataFrame:
    """Keep only the final attempt for each client, from the last start onward.

    This reproduces the notebook logic used to identify the client's latest
    recorded start event and then keep only rows from that visit and timestamp
    onward.
    """
    df_web = prepare_web_data(df_web, datetime_col=datetime_col)

    starts = df_web[df_web[step_col] == start_step].copy()
    last_starts = (
        starts.groupby(client_col, as_index=False)[datetime_col]
        .max()
        .rename(columns={datetime_col: "last_start_time"})
    )

    last_start_visits = (
        df_web[df_web[step_col] == start_step]
        .merge(last_starts, on=client_col, how="inner")
    )

    last_start_visits = last_start_visits[
        last_start_visits[datetime_col] == last_start_visits["last_start_time"]
    ][[client_col, visit_col, "last_start_time"]].drop_duplicates()

    df_web_last_attempt = df_web.merge(
        last_start_visits,
        on=[client_col, visit_col],
        how="inner",
    )

    df_web_last_attempt = df_web_last_attempt[
        df_web_last_attempt[datetime_col] >= df_web_last_attempt["last_start_time"]
    ].copy()

    return df_web_last_attempt.sort_values([client_col, visit_col, datetime_col])



def build_visit_window(
    df_web: pd.DataFrame,
    visit_col: str = "visit_id",
    step_col: str = "process_step",
    datetime_col: str = "date_time",
    start_step: str = "start",
    confirm_step: str = "confirm",
) -> pd.DataFrame:
    """Keep event rows that occur between the first start and last confirm.

    Only visits containing both a start and a confirm are retained.
    """
    df_web = prepare_web_data(df_web, datetime_col=datetime_col)

    first_start = (
        df_web[df_web[step_col] == start_step]
        .groupby(visit_col, as_index=False)[datetime_col]
        .min()
        .rename(columns={datetime_col: "first_start_time"})
    )

    last_confirm = (
        df_web[df_web[step_col] == confirm_step]
        .groupby(visit_col, as_index=False)[datetime_col]
        .max()
        .rename(columns={datetime_col: "last_confirm_time"})
    )

    visit_limits = first_start.merge(last_confirm, on=visit_col, how="inner")

    df_visit_window = df_web.merge(visit_limits, on=visit_col, how="inner")
    df_visit_window = df_visit_window[
        (df_visit_window[datetime_col] >= df_visit_window["first_start_time"])
        & (df_visit_window[datetime_col] <= df_visit_window["last_confirm_time"])
    ].copy()

    return df_visit_window.sort_values([visit_col, datetime_col]).reset_index(drop=True)



def add_task_time_per_visit(
    df_time_window: pd.DataFrame,
    visit_col: str = "visit_id",
    client_col: str = "client_id",
    variation_col: str = "Variation",
    start_time_col: str = "first_start_time",
    end_time_col: str = "last_confirm_time",
) -> pd.DataFrame:
    """Create one row per visit with task duration in seconds and minutes."""
    df = df_time_window.copy()
    df[start_time_col] = pd.to_datetime(df[start_time_col])
    df[end_time_col] = pd.to_datetime(df[end_time_col])

    df["task_time_seconds"] = (df[end_time_col] - df[start_time_col]).dt.total_seconds()

    df_visit_time = (
        df.groupby(visit_col)
        .agg(
            client_id=(client_col, "first"),
            Variation=(variation_col, "first"),
            task_time_seconds=("task_time_seconds", "first"),
        )
        .reset_index()
    )
    df_visit_time["task_time_minutes"] = df_visit_time["task_time_seconds"] / 60
    return df_visit_time



def summarize_task_time_by_variation(
    df_visit_time: pd.DataFrame,
    variation_col: str = "Variation",
    minutes_col: str = "task_time_minutes",
) -> pd.DataFrame:
    """Return mean, median, and count of task time by A/B test group."""
    return df_visit_time.groupby(variation_col)[minutes_col].agg(["mean", "median", "count"])



def count_visits_and_unique_clients(
    df_visit_time: pd.DataFrame,
    variation_col: str = "Variation",
    visit_col: str = "visit_id",
    client_col: str = "client_id",
) -> pd.DataFrame:
    """Compare number of visits and number of unique clients by variation."""
    return (
        df_visit_time.groupby(variation_col)
        .agg(visits=(visit_col, "count"), unique_clients=(client_col, "nunique"))
        .reset_index()
    )



def compute_step_times(
    df_time_window: pd.DataFrame,
    visit_col: str = "visit_id",
    datetime_col: str = "date_time",
) -> pd.DataFrame:
    """Add elapsed seconds between consecutive events within each visit."""
    df = df_time_window.sort_values([visit_col, datetime_col]).copy()
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    df["step_time_seconds"] = (
        df.groupby(visit_col)[datetime_col].diff().dt.total_seconds()
    )
    return df



def summarize_step_kpis(
    df_steps: pd.DataFrame,
    variation_col: str = "Variation",
    step_col: str = "process_step",
    step_time_col: str = "step_time_seconds",
) -> pd.DataFrame:
    """Aggregate mean, median, and count of time spent on each process step."""
    step_kpi = (
        df_steps.dropna(subset=[step_time_col])
        .groupby([variation_col, step_col])
        .agg(
            mean_time_sec=(step_time_col, "mean"),
            median_time_sec=(step_time_col, "median"),
            count=(step_time_col, "count"),
        )
        .reset_index()
    )
    step_kpi["mean_time_min"] = step_kpi["mean_time_sec"] / 60
    step_kpi["median_time_min"] = step_kpi["median_time_sec"] / 60
    return step_kpi



def build_funnel_counts(
    df_time_window: pd.DataFrame,
    step_order: Sequence[str] = ("start", "step_1", "step_2", "step_3", "confirm"),
    visit_col: str = "visit_id",
    variation_col: str = "Variation",
    step_col: str = "process_step",
) -> pd.DataFrame:
    """Count how many visits reached each funnel step by variation."""
    funnel = (
        df_time_window.groupby([visit_col, variation_col, step_col])
        .size()
        .unstack(fill_value=0)
    )

    funnel = (funnel > 0).astype(int)

    for step in step_order:
        if step not in funnel.columns:
            funnel[step] = 0

    funnel = funnel[list(step_order)]
    step_counts = funnel.groupby(variation_col)[list(step_order)].sum()
    return step_counts



def calculate_dropoff_summary(
    step_counts: pd.DataFrame,
    step_order: Sequence[str] = ("start", "step_1", "step_2", "step_3", "confirm"),
) -> pd.DataFrame:
    """Calculate conversion and drop-off rates between consecutive funnel steps."""
    dropoff_summary = step_counts.copy()

    for i in range(len(step_order) - 1):
        current_step = step_order[i]
        next_step = step_order[i + 1]
        conversion_col = f"{current_step}_to_{next_step}_conversion"
        dropoff_col = f"{current_step}_to_{next_step}_dropoff"

        dropoff_summary[conversion_col] = (
            step_counts[next_step] / step_counts[current_step]
        )
        dropoff_summary[dropoff_col] = 1 - dropoff_summary[conversion_col]

    return dropoff_summary



def remove_iqr_outliers(
    df: pd.DataFrame,
    column: str,
    multiplier: float = 1.5,
) -> pd.DataFrame:
    """Remove outliers from a numeric column using the IQR rule."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()


# -----------------------------------------------------------------------------
# Example pipeline helpers
# -----------------------------------------------------------------------------

def prepare_demographics_analysis(
    df_demo: pd.DataFrame,
    df_time_window: pd.DataFrame,
) -> pd.DataFrame:
    """One-step preparation for the demographics notebook's main analysis table."""
    df = filter_active_clients(df_demo, df_time_window)
    df = clean_gender_labels(df)
    df = add_binned_group(
        df,
        source_col="clnt_age",
        bins=[0, 30, 50, 70, 100],
        labels=["<30", "30-50", "50-70", "70+"],
        new_col="age_group",
    )
    df = add_binned_group(
        df,
        source_col="clnt_tenure_yr",
        bins=[0, 5, 10, 20, 50],
        labels=["0-5 yrs", "5-10 yrs", "10-20 yrs", "20+ yrs"],
        new_col="tenure_group",
    )
    df = add_activity_metric(df)
    df = add_client_segment(df)
    return df



def prepare_duration_kpis(df_time_window: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Convenience pipeline returning core KPI tables.

    Returns
    -------
    tuple
        (df_visit_time, summary_by_variation, step_kpi, dropoff_summary)
    """
    df_visit_time = add_task_time_per_visit(df_time_window)
    summary_by_variation = summarize_task_time_by_variation(df_visit_time)

    df_steps = compute_step_times(df_time_window)
    step_kpi = summarize_step_kpis(df_steps)

    step_counts = build_funnel_counts(df_time_window)
    dropoff_summary = calculate_dropoff_summary(step_counts)

    return df_visit_time, summary_by_variation, step_kpi, dropoff_summary
