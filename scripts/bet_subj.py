import datetime
from pathlib import Path

import polars as pl
from polars import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns

from helpers import find_outliers, check_assumptions, load_and_aggregate_logs

def _plot_box_and_hist(df_music: DataFrame, df_no_music: DataFrame) -> None:
    dfp = pl.concat([df_music.select(["Subject_ID", "Success_Count", "Error_Rate", "Condition"]),
                     df_no_music.select(["Subject_ID", "Success_Count", "Error_Rate", "Condition"])])

    # Boxplot: Success_Count
    plt.figure(figsize=(6, 4))
    sns.boxplot(x="Condition", y="Success_Count", data=dfp, palette="Set2", hue="Condition", width=0.5, whis=(0, 100))
    sns.stripplot(x="Condition", y="Success_Count", data=dfp, color="0.2", size=4, jitter=True)
    plt.title(f"Anzahl korrekt geklickter Formen")
    plt.ylabel("Anzahl korrekte Klicks")
    plt.tight_layout()
    plt.show()


    # Boxplot: Error_Rate
    plt.figure(figsize=(6, 4))
    sns.boxplot(x="Condition", y="Error_Rate", data=dfp, palette="Set2", hue="Condition", width=0.5, whis=(0, 100))
    sns.stripplot(x="Condition", y="Error_Rate", data=dfp, color="0.2", size=4, jitter=True)
    plt.title(f"Fehlerrate")
    plt.ylabel("Fehlerrate in %")
    plt.tight_layout()
    plt.show()


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


    _plot_box_and_hist(df_music, df_no_music)

def main() -> None:
    log_folder = Path(__file__).resolve().parent.parent / "logs"

    df = load_and_aggregate_logs(log_folder)

    group_a = "Group A (NM->M)"
    group_b = "Group B (M->NM)"

    # First test per group: Group A -> No Music, Group B -> Music
    print("\n=== Test 1: Group A -> No Music, Group B -> Music ===")
    df_p1_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "Music"))
    df_p1_no_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "No Music"))

    print(f"Music Success_Count: {df_p1_music["Success_Count"].describe()}")
    print(f"No Music Success_Count: {df_p1_no_music["Success_Count"].describe()}")
    print(f"Music Error_Rate: {df_p1_music["Error_Rate"].describe()}")
    print(f"No Music Error_Rate: {df_p1_no_music["Error_Rate"].describe()}")

    analyze(df_p1_music, df_p1_no_music)

    # Second test per group: Group A -> Music, Group B -> No Music
    print("\n=== Test 2: Group A -> Music, Group B -> No Music ===")
    df_p2_music = df.filter((pl.col("Group") == group_a) & (pl.col("Condition") == "Music"))
    df_p2_no_music = df.filter((pl.col("Group") == group_b) & (pl.col("Condition") == "No Music"))
    print(f"Preparing to analyze: Music rows={df_p2_music.height}, No Music rows={df_p2_no_music.height}")

    print(f"Music Success_Count: {df_p2_music["Success_Count"].describe()}")
    print(f"No Music Success_Count: {df_p2_no_music["Success_Count"].describe()}")
    print(f"Music Error_Rate: {df_p2_music["Error_Rate"].describe()}")
    print(f"No Music Error_Rate: {df_p2_no_music["Error_Rate"].describe()}")

    analyze(df_p2_music, df_p2_no_music)

if __name__ == "__main__":
    main()