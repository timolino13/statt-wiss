from pathlib import Path

import polars as pl
from polars import DataFrame

from helpers import find_outliers, check_assumptions, load_and_aggregate_logs

def analyze(df_music: DataFrame, df_no_music: DataFrame) -> None:
    """Print outliers and run assumption checks for Success_Count and Error_Rate."""
    print("\n--- Finding Outliers ---")
    out_sc_music = find_outliers(df_music, "Success_Count")
    out_sc_no = find_outliers(df_no_music, "Success_Count")
    print("Outliers music by Success_Count")
    print(out_sc_music["Subject_ID"])
    print("Outliers no_music by Success_Count")
    print(out_sc_no["Subject_ID"])

    out_e_music = find_outliers(df_music, "Error_Rate")
    out_e_no = find_outliers(df_no_music, "Error_Rate")
    print("\nOutliers music by Error_Rate")
    print(out_e_music["Subject_ID"])
    print("Outliers no_music by Error_Rate")
    print(out_e_no["Subject_ID"])

    # H1: Success_Count (music > no_music)
    scores_music = df_music["Success_Count"]
    scores_no_music = df_no_music["Success_Count"]
    print("\n--- Assumptions Check H1 ---")
    check_assumptions(scores_music, scores_no_music, "greater")

    # H2: Error_Rate (music > no_music)
    error_rate_music = df_music["Error_Rate"]
    error_rate_no_music = df_no_music["Error_Rate"]
    print("\n--- Assumptions Check H2 ---")
    check_assumptions(error_rate_music, error_rate_no_music, "greater")


def main() -> None:
    log_folder = Path(__file__).resolve().parent.parent / "logs"

    df = load_and_aggregate_logs(log_folder)

    group_a = "Group A (NM->M)"
    group_b = "Group B (M->NM)"

    # First test per group: Group A -> No Music, Group B -> Music
    df_p1_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "Music"))
    df_p1_no_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "No Music"))
    analyze(df_p1_music, df_p1_no_music)

    # Second test per group: Group A -> Music, Group B -> No Music
    # df_p2_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "Music"))
    # df_p2_no_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "No Music"))
    # analyze(df_p2_music, df_p2_no_music)


if __name__ == "__main__":
    main()