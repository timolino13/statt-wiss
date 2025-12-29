from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

from helpers import check_assumptions, load_and_aggregate_logs

def main():
    log_folder = Path(__file__).resolve().parent.parent / "logs"
    # --- Execution ---
    df = load_and_aggregate_logs(log_folder)

    # Sort for better plotting order
    df = df.sort("Condition")

    sns.pointplot(
        data=df,
        x="Condition",
        y="Success_Count",
        hue="Subject_ID",
        palette="viridis",
        markers="o",
        dodge=False
    )

    plt.title("Impact of Music on Click Success", fontsize=14)
    plt.ylabel("Number of Successful Clicks")
    plt.xlabel("Condition")
    plt.show()

    # --- 1. VISUALIZE THE INTERACTION ORDER ---
    plt.figure(figsize=(8, 6))

    # This plot shows the "X" if learning dominates
    sns.pointplot(
        data=df,
        x="Condition",
        y="Success_Count",
        hue="Group",
        markers=["o", "s"],
        linestyles=["-", "--"],
        errorbar=None  # Turn off confidence intervals for clarity on individual trends
    )

    plt.title("Interaction Plot: Music vs. Learning Effect")
    plt.ylabel("Success Count")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

    # --- 2. STATISTICAL CHECK (Mixed Design) ---
    # We compare the DIFFERENCE scores between the two groups.
    # Diff = Music - No Music
    # If Music works, BOTH groups should have a positive difference (or same direction).
    # If it's just learning, Group A will be Positive, Group B will be Negative.

    df_music = df.filter(pl.col("Condition") == "Music")
    df_nm = df.filter(pl.col("Condition") == "No Music")

    # Join to get paired data
    df_paired = df_music.join(df_nm, on="Subject_ID", suffix="_NM")

    # Calculate Music Effect for each person
    df_paired = df_paired.with_columns(
        (pl.col("Success_Count") - pl.col("Success_Count_NM")).alias("Music_Effect")
    )

    # Separate by Group
    group_a_diffs = df_paired.filter(pl.col("Group") == "Group A (NM->M)")["Music_Effect"]
    group_b_diffs = df_paired.filter(pl.col("Group") == "Group B (M->NM)")["Music_Effect"]

    # If these two means are significantly different, you have a strong Order Effect.
    print(f"Interaction Test (Order Effect)")
    check_assumptions(group_a_diffs, group_b_diffs, 'two-sided')

if __name__ == "__main__":
    main()