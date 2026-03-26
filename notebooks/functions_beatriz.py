Setting initial thought.

STEP_ORDER so "errors" - processes that don't follow the step order - can be found and classified.

import polars as pl

STEP_ORDER = {"start": 0, "step_1": 1, "step_2": 2, "step_3": 3, "confirm": 4}
STEP_NAMES = {v: k for k, v in STEP_ORDER.items()}
REQUIRED_STEPS = set(STEP_ORDER.keys())
STEPS = ["start", "step_1", "step_2", "step_3", "confirm"]

df = (
    pl.read_csv(config["output_data"]["file5"])
    .with_columns([
        pl.col("date_time").str.to_datetime().alias("date_time"),
        pl.col("process_step").replace(STEP_ORDER).alias("step_rank"),
    ])
    .sort(["visit_id", "date_time"])
    .with_columns([
        pl.col("step_rank").shift(1).over("visit_id").alias("prev_step_rank"),
        pl.col("process_step").shift(1).over("visit_id").alias("prev_step_name"),
    ])
    .with_columns([
        (pl.col("step_rank") == pl.col("prev_step_rank")).alias("is_repetition"),
        (pl.col("step_rank") < pl.col("prev_step_rank")).alias("is_regression"),
    ])
    .with_columns(
        (pl.col("is_repetition") | pl.col("is_regression")).alias("is_error")
    )
)

def classify_visit(steps, step_ranks, had_error, n_regressions):
    steps = list(steps)
    step_ranks = list(step_ranks)

    # Invalid: sequence violation — a later step appears before an earlier one
    for i in range(len(STEPS) - 1):
        if STEPS[i] in steps and STEPS[i+1] in steps:
            if steps.index(STEPS[i+1]) < steps.index(STEPS[i]):
                return "invalid"

    # Incomplete: never reached confirm or missing steps
    if not REQUIRED_STEPS.issubset(set(steps)):
        return "incomplete"

    # Smooth: all steps, correct order, no errors
    if not had_error:
        return "smooth"

    # Lumpy: completed but with errors — distinguish type
    if n_regressions > 0:
        return "lumpy_regression"
    return "lumpy_repetition"

visit_agg = (
    df.group_by("visit_id").agg([
        pl.col("process_step").alias("steps_list"),
        pl.col("step_rank").alias("step_ranks_list"),
        pl.col("date_time").min().alias("visit_start"),
        pl.col("date_time").max().alias("visit_end"),
        pl.col("step_rank").max().alias("max_step_reached"),
        pl.col("is_error").any().alias("had_error"),
        pl.col("is_repetition").sum().alias("n_repetitions"),
        pl.col("is_regression").sum().alias("n_regressions"),
        pl.col("Variation").first().alias("variation"),
        pl.col("client_id").first().alias("client_id"),
        pl.col("visitor_id").first().alias("visitor_id"),
    ])
    .with_columns([
        (pl.col("visit_end") - pl.col("visit_start"))
            .dt.total_seconds()
            .alias("visit_duration_seconds"),
        pl.struct(["steps_list", "step_ranks_list", "had_error", "n_regressions"])
          .map_elements(
              lambda r: classify_visit(
                  r["steps_list"],
                  r["step_ranks_list"],
                  r["had_error"],
                  r["n_regressions"]
              ),
              return_dtype=pl.String
          )
          .alias("completion_type"),
    ])
    .with_columns(
        # dropped_at_step only meaningful for incomplete visits
        pl.when(pl.col("completion_type") == "incomplete")
            .then(pl.col("max_step_reached").cast(pl.String)
                    .replace({str(k): v for k, v in STEP_NAMES.items()}))
            .otherwise(pl.lit(None))
            .alias("dropped_at_step")
    )
)

print(
    visit_agg
    .group_by(["variation", "completion_type"])
    .agg(pl.len().alias("n_visits"))
    .sort(["variation", "completion_type"])



Attempting to find error's per step. Trying different strategies.

error_per_step = (
    df
    .filter(pl.col("is_error"))
    .group_by(["Variation", "process_step"])
    .agg([
        pl.len().alias("n_errors"),
        pl.col("is_repetition").sum().alias("n_repetitions"),
        pl.col("is_regression").sum().alias("n_regressions"),
    ])
    .join(
        df.group_by("Variation").agg(pl.len().alias("total_rows")),
        on="Variation"
    )
    .with_columns(
        (pl.col("n_errors") / pl.col("total_rows") * 100).round(2).alias("error_rate_%")
    )
    .sort(["Variation", "process_step"])
    .select(["Variation", "process_step", "n_errors", "n_repetitions", "n_regressions", "error_rate_%"])
)

print(error_per_step)

error_per_step.write_csv("transition_errors_per_step.csv")

---
Finding Errors per step Transition. This goes further than "per step" announcing right away where the error ended up at. May be relevant or not.

 # Errors per step transition — ranked buggiest to least buggy per group. Added ERROR RATE.
import polars as pl

pl.Config.set_tbl_rows(1000)
pl.Config.set_tbl_cols(100)

transition_errors = (
    df
    .filter(pl.col("is_error"))
    .with_columns(
        (pl.col("prev_step_name") + " -> " + pl.col("process_step")).alias("transition")
    )
    .group_by(["Variation", "transition"])
    .agg([
        pl.len().alias("n_errors"),
        pl.col("is_repetition").sum().alias("n_repetitions"),
        pl.col("is_regression").sum().alias("n_regressions"),
    ])
    .join(
        df.group_by("Variation").agg(pl.len().alias("total_rows")),
        on="Variation"
    )
    .with_columns(
        (pl.col("n_errors") / pl.col("total_rows")).alias("error_rate")
    )
    .sort(["Variation", "n_errors"], descending=[False, True])
)

# Buggiest transition per group
buggiest_per_group = (
    transition_errors
    .group_by("Variation")
    .agg(pl.all().sort_by("n_errors", descending=True).first())
    .sort("Variation")
)

print("=== Buggiest Transitions by Variation ===")
print(transition_errors)

print("\n=== Buggiest Transition Per Group ===")
print(buggiest_per_group.select(["Variation", "transition", "n_errors", "n_repetitions", "n_regressions", "error_rate"]))

---
Z-test:

import numpy as np

ALPHA = 0.05

# --- Numbers ---
test_visits    = visit_agg_demo.filter(pl.col("variation") == "Test")
control_visits = visit_agg_demo.filter(pl.col("variation") == "Control")

test_total    = len(test_visits)
control_total = len(control_visits)

test_errors    = test_visits["had_error"].cast(pl.Int32).sum()
control_errors = control_visits["had_error"].cast(pl.Int32).sum()

p_test    = test_errors / test_total
p_control = control_errors / control_total
p_pool    = (test_errors + control_errors) / (test_total + control_total)
se        = np.sqrt(p_pool * (1 - p_pool) * (1/test_total + 1/control_total))
z_stat    = (p_test - p_control) / se
p_value   = 0.5 * np.exp(-0.717 * z_stat - 0.416 * z_stat**2)