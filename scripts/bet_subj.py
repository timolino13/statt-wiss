from pathlib import Path

import polars as pl
from polars import DataFrame

from helpers import find_outliers, check_assumptions, load_and_aggregate_logs

def analyze(df_music: DataFrame, df_no_music: DataFrame) -> None:
    """Print outliers and run assumption checks for Success_Count and Error_Rate."""

    print("\n=== Analysis Summary ===")
    print("\n--- Finding Outliers (Success_Count) ---")
    out_sc_music = find_outliers(df_music, "Success_Count")
    out_sc_no = find_outliers(df_no_music, "Success_Count")
    print(f"Music outliers (count={out_sc_music.height}): {out_sc_music["Subject_ID"].to_list()}")
    print(f"No Music outliers (count={out_sc_no.height}): {out_sc_no["Subject_ID"].to_list()}")

    print("\n--- Finding Outliers (Error_Rate) ---")
    out_e_music = find_outliers(df_music, "Error_Rate")
    out_e_no = find_outliers(df_no_music, "Error_Rate")
    print(f"Music outliers (count={out_e_music.height}): {out_e_music["Subject_ID"].to_list()}")
    print(f"No Music outliers (count={out_e_no.height}): {out_e_no["Subject_ID"].to_list()}")

    # H1: Success_Count (music > no_music)
    scores_music = df_music["Success_Count"]
    scores_no_music = df_no_music["Success_Count"]
    print("\n--- Assumptions Check H1: Success_Count (music > no_music) ---")
    check_assumptions(scores_music, scores_no_music, "greater")

    # H2: Error_Rate (music < no_music)
    error_rate_music = df_music["Error_Rate"]
    error_rate_no_music = df_no_music["Error_Rate"]
    print("\n--- Assumptions Check H2: Error_Rate (music < no_music) ---")
    check_assumptions(error_rate_music, error_rate_no_music, "less")


def main() -> None:
    log_folder = Path(__file__).resolve().parent.parent / "logs"

    df = load_and_aggregate_logs(log_folder)

    group_a = "Group A (NM->M)"
    group_b = "Group B (M->NM)"

    # First test per group: Group A -> No Music, Group B -> Music
    print("\n=== Test 1: Group A -> No Music, Group B -> Music ===")
    df_p1_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "Music"))
    df_p1_no_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "No Music"))
    print(f"Preparing to analyze: Music rows={df_p1_music.height}, No Music rows={df_p1_no_music.height}")

    def _mean_std(s: pl.Series):
       return round(s.mean(), 2), round(s.std(), 2)

    m_sc_mean, m_sc_std = _mean_std(df_p1_music["Success_Count"])
    n_sc_mean, n_sc_std = _mean_std(df_p1_no_music["Success_Count"])
    m_er_mean, m_er_std = _mean_std(df_p1_music["Error_Rate"])
    n_er_mean, n_er_std = _mean_std(df_p1_no_music["Error_Rate"])

    print(f"Music Success_Count mean={m_sc_mean}, std={m_sc_std}")
    print(f"No Music Success_Count mean={n_sc_mean}, std={n_sc_std}")
    print(f"Music Error_Rate mean={m_er_mean}, std={m_er_std}")
    print(f"No Music Error_Rate mean={n_er_mean}, std={n_er_std}")

    analyze(df_p1_music, df_p1_no_music)

    # Second test per group: Group A -> Music, Group B -> No Music
    print("\n=== Test 2: Group A -> Music, Group B -> No Music ===")
    df_p2_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "Music"))
    df_p2_no_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "No Music"))
    print(f"Preparing to analyze: Music rows={df_p2_music.height}, No Music rows={df_p2_no_music.height}")

    m2_sc_mean, m2_sc_std = _mean_std(df_p2_music["Success_Count"])
    n2_sc_mean, n2_sc_std = _mean_std(df_p2_no_music["Success_Count"])
    m2_er_mean, m2_er_std = _mean_std(df_p2_music["Error_Rate"])
    n2_er_mean, n2_er_std = _mean_std(df_p2_no_music["Error_Rate"])

    print(f"Music Success_Count mean={m2_sc_mean}, std={m2_sc_std}")
    print(f"No Music Success_Count mean={n2_sc_mean}, std={n2_sc_std}")
    print(f"Music Error_Rate mean={m2_er_mean}, std={m2_er_std}")
    print(f"No Music Error_Rate mean={n2_er_mean}, std={n2_er_std}")

    analyze(df_p2_music, df_p2_no_music)

if __name__ == "__main__":
    main()