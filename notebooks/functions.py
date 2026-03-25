"""
Reusable functions for A/B Testing client funnel analysis, demographics, and duration KPIs.

Sections:
1. Loading Data
2. Data Wrangling & Cleaning
3. Data Checking
4. Data Analysis / KPI Transformations
5. Data Visualization
"""

from __future__ import annotations
from typing import Iterable, Sequence
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest

# -----------------------------------------------------------------------------
# 1. Loading Data
# -----------------------------------------------------------------------------

def load_csv(path: str, drop_columns: Sequence[str] | None = None) -> pd.DataFrame:
    """
    Load CSV and optionally drop columns.

    Example:
    df = load_csv('data.csv', drop_columns=['Unnamed: 0'])
    """
    df = pd.read_csv(path)
    if drop_columns:
        df = df.drop(columns=drop_columns)
    return df

def save_csv(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame to CSV."""
    df.to_csv(path, index=False)

# -----------------------------------------------------------------------------
# 2. Data Wrangling & Cleaning
# -----------------------------------------------------------------------------

def drop_missing(df: pd.DataFrame, subset: Sequence[str] | None = None) -> pd.DataFrame:
    """Drop rows with missing values in specified columns (all if None)."""
    return df.dropna(subset=subset).copy()

def drop_duplicates(df: pd.DataFrame, subset: Sequence[str] | None = None) -> pd.DataFrame:
    """Remove duplicate rows."""
    return df.drop_duplicates(subset=subset).copy()
    
def sort_by_columns(df: pd.DataFrame, columns: Sequence[str], ascending: bool | Sequence[bool] = True) -> pd.DataFrame:
    """Sort DataFrame by columns."""
    return df.sort_values(columns, ascending=ascending).reset_index(drop=True)

def map_steps(df: pd.DataFrame, step_col: str = "process_step", new_col: str = "step") -> pd.DataFrame:
    """
    Map process steps to integer codes.
    Example mapping: {'start':0, 'step_1':1, ..., 'confirm':4}
    """
    df = df.copy()
    step_mapping = {step: i for i, step in enumerate(df[step_col].unique())}
    df[new_col] = df[step_col].map(step_mapping)
    return df

def add_next_step_diff(df: pd.DataFrame, visit_col: str = "visit_id", step_col: str = "step") -> pd.DataFrame:
    """Add next step and difference between steps."""
    df = df.copy()
    df['next_step'] = df.groupby(visit_col)[step_col].shift(-1)
    df['step_diff'] = df['next_step'] - df[step_col]
    return df

def filter_last_confirm(df: pd.DataFrame, step_col: str = "process_step") -> pd.DataFrame:
    """Keep all non-confirm steps and only last confirm per sequence."""
    df = df.copy()
    df['next_step_helper'] = df.groupby('visit_id')[step_col].shift(-1)
    df = df[(df[step_col] != 'confirm') | ((df[step_col] == 'confirm') & (df['next_step_helper'] != 'confirm'))]
    df = df.drop(columns=['next_step_helper']).reset_index(drop=True)
    return df

# -----------------------------------------------------------------------------
# 3. Data Checking
# -----------------------------------------------------------------------------

def check_funnel_complete(df: pd.DataFrame, funnel: Sequence[str] = ('start','step_1','step_2','step_3','confirm')) -> pd.DataFrame:
    """
    Check if a visit contains the complete funnel sequence.
    Returns DataFrame with columns: visit_id, completed_process (True/False)

    Example:
    check_funnel_complete(df_control)
    """
    def has_complete_funnel(visit_df: pd.DataFrame) -> bool:
        steps = visit_df.sort_values('date_time')['process_step'].tolist()
        funnel_index = 0
        for step in steps:
            if step == funnel[funnel_index]:
                funnel_index += 1
                if funnel_index == len(funnel):
                    return True
        return False

    return df.groupby('visit_id').apply(has_complete_funnel).reset_index(name='completed_process')

def proportions_z_test(count: Sequence[int], nobs: Sequence[int], alpha: float = 0.05) -> tuple[float, float, str]:
    """
    Compute z-test for two proportions.

    Returns: z_stat, p_value, result_str
    Example:
    proportions_z_test([100,120], [200,250])
    """
    z_stat, p_value = proportions_ztest(count, nobs)
    result = "Reject null hypothesis" if p_value <= alpha else "Fail to reject null hypothesis"
    return z_stat, p_value, result

# -----------------------------------------------------------------------------
# 4. Data Analysis / KPI Transformations
# -----------------------------------------------------------------------------

def compute_step_kpi(df: pd.DataFrame, variation_col: str = "Variation") -> pd.DataFrame:
    """
    Compute total rows per step and count of consecutive step completions.
    Returns DataFrame with pct_step per group.
    """
    df = df.copy()
    df_no_confirm = df[df['process_step'] != 'confirm']
    grouped = df_no_confirm.groupby('process_step').agg(
        total=('process_step', 'size'),
        count_step=('step_diff', lambda x: (x == 1).sum())
    )
    grouped['pct'] = (grouped['count_step'] / grouped['total'] * 100).round(0)
    return grouped.reset_index()

def merge_kpi_steps(control_df: pd.DataFrame, test_df: pd.DataFrame, step_col: str = "process_step") -> pd.DataFrame:
    """Merge KPI steps for control and test datasets."""
    return control_df.merge(test_df, on=step_col, suffixes=('_Control','_Test'))

# -----------------------------------------------------------------------------
# 5. Data Visualization
# -----------------------------------------------------------------------------

def plot_step_completion(df: pd.DataFrame, step_col: str = "process_step", pct_col: str = "pct", group_col: str = "group",
                         title: str = "Completion rate per step", ylim: tuple = (60,100), save_path: str | None = None):
    """Line plot showing completion rate per step."""
    plt.figure(figsize=(8,5))
    custom_palette = {"Control":"#333333","Test":"#C20029"}
    sns.lineplot(data=df, x=step_col, y=pct_col, hue=group_col, marker="o", palette=custom_palette)
    for i, row in df.iterrows():
        plt.text(row[step_col], row[pct_col]+2, f"{row[pct_col]}%", ha='center', va='bottom')
    plt.title(title)
    plt.xlabel("Steps")
    plt.ylabel("% steps achieved")
    plt.ylim(*ylim)
    plt.grid(True, linestyle='--', alpha=0.5)
    sns.despine()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def plot_kpi_bar(df: pd.DataFrame, x_col: str, y_col: str, hue_col: str | None = None,
                 title: str = "KPI by group", xlabel: str | None = None, ylabel: str | None = None,
                 palette: dict | None = None, save_path: str | None = None):
    """Simple bar plot to compare a metric across groups."""
    plt.figure(figsize=(8,5))
    sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col, palette=palette)
    plt.title(title)
    plt.xlabel(xlabel or x_col)
    plt.ylabel(ylabel or y_col)
    sns.despine()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def plot_kpi_box(df: pd.DataFrame, x_col: str, y_col: str, hue_col: str | None = None,
                 title: str = "Distribution by group", xlabel: str | None = None, ylabel: str | None = None,
                 palette: dict | None = None, save_path: str | None = None):
    """Boxplot to visualize distribution and outliers of a KPI."""
    plt.figure(figsize=(8,5))
    sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col, palette=palette)
    plt.title(title)
    plt.xlabel(xlabel or x_col)
    plt.ylabel(ylabel or y_col)
    sns.despine()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def plot_distribution(df: pd.DataFrame, col: str, bins: int = 20,
                      title: str = "Distribution", xlabel: str | None = None, ylabel: str = "Frequency",
                      save_path: str | None = None):
    """Histogram to visualize distribution of a numeric column."""
    plt.figure(figsize=(8,5))
    sns.histplot(df[col], bins=bins, kde=True)
    plt.title(title)
    plt.xlabel(xlabel or col)
    plt.ylabel(ylabel)
    sns.despine()
    if save_path:
        plt.savefig(save_path)
    plt.show()