import polars as pl
from polars import DataFrame

from helpers import load_and_aggregate_logs, check_assumptions, find_outliers

log_folder = "./logs"
df = load_and_aggregate_logs(log_folder)

def analyze(df_condition_1: DataFrame, df_condition_2: DataFrame):
    print("--- Finding Outliers ---")
    print("Outliers music by Success_Count")
    print(find_outliers(df_condition_1, "Success_Count")["Subject_ID"])
    print("Outliers no_music by Success_Count")
    print(find_outliers(df_condition_2, "Success_Count")["Subject_ID"])

    print("\nOutliers music by Error_Rate")
    print(find_outliers(df_condition_1, "Error_Rate")["Subject_ID"])
    print("Outliers no_music by Error_Rate")
    print(find_outliers(df_condition_2, "Error_Rate")["Subject_ID"])

    # Check H1
    # Separate the groups
    scores_music = df_condition_1["Success_Count"]
    scores_no_music = df_condition_2["Success_Count"]

    # Check Assumptions
    print("\n--- Assumptions Check H1 ---")
    check_assumptions(scores_music, scores_no_music, "greater")

    # Check H2
    # Separate the groups
    error_rate_music = df_condition_1["Error_Rate"]
    error_rate_no_music = df_condition_2["Error_Rate"]

    # Check Assumptions
    print("\n--- Assumptions Check H2 ---")
    check_assumptions(error_rate_music, error_rate_no_music, "greater")

# Only consider first test per group: Group A -> No Music, Group B -> Music
df_p1 = df.filter(
    (
        (pl.col("Group") == "Group A (NM->M)")
        & (pl.col("Condition") == "No Music")
    )
    | (
        (pl.col("Group") == "Group B (M->NM)")
        & (pl.col("Condition") == "Music")
    )
)
df_p1_music = df_p1.filter(pl.col("Condition") == "Music")
df_p1_no_music = df_p1.filter(pl.col("Condition") == "No Music")

analyze(df_p1_music, df_p1_no_music)

# Only consider second test per group: Group A -> Music, Group B -> No Music
df_p2 = df.filter(
    (
        (pl.col("Group") == "Group A (NM->M)")
        & (pl.col("Condition") == "Music")
    )
    | (
        (pl.col("Group") == "Group B (M->NM)")
        & (pl.col("Condition") == "No Music")
    )
)
df_p2_music = df_p1.filter(pl.col("Condition") == "Music")
df_p2_no_music = df_p1.filter(pl.col("Condition") == "No Music")

analyze(df_p2_music, df_p2_no_music)