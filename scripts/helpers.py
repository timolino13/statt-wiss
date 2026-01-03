import glob
import os
from typing import Literal

import numpy as np
import polars as pl
from polars import Series, DataFrame
from scipy import stats


def load_and_aggregate_logs(log_folder_path):
    aggregated_data = []
    file_paths = glob.glob(os.path.join(log_folder_path, "*.csv"))

    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            name_no_ext = os.path.splitext(filename)[0]
            parts = name_no_ext.split('_')

            # Extract Subject ID and Condition
            subject_id = int(parts[0])
            condition_code = parts[-1]
            condition = 'Music' if condition_code == 'm' else 'No Music'


            # Group A: 1-6 (NM -> M), Group B: 7-12 (M -> NM)
            group = "Group A (NM->M)" if subject_id <= 6 else "Group B (M->NM)"

            # Read CSV
            df = pl.read_csv(file_path)
            success = df.filter(pl.col("shape_hit") == True).height
            error = df.filter(pl.col("shape_hit") == False).height

            aggregated_data.append({
                "Subject_ID": subject_id,
                "Group": group,
                "Condition": condition,
                "Success_Count": success,
                "Error_Count": error,
                "Error_Rate": error / (success + error),
            })

        except Exception as e:
            print(f"Skipping {filename}: {e}")

    return pl.DataFrame(aggregated_data)

def cohens_d(s1: Series, s2: Series) -> float:
    """
    Compute Cohen\`s d for two independent samples using pooled standard deviation.
    Returns NaN if not enough data or pooled std is zero.
    """

    a = s1.to_numpy()
    b = s2.to_numpy()

    n1 = a.size
    n2 = b.size
    if n1 < 2 or n2 < 2:
        return float("nan")

    m1 = a.mean()
    m2 = b.mean()
    sd1 = a.std(ddof=1)
    sd2 = b.std(ddof=1)

    pooled = np.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    if pooled == 0:
        return float("nan")

    return (m1 - m2) / pooled

def check_assumptions(s1: Series, s2: Series, alternative: Literal["two-sided", "less", "greater"]):
    norm_m = stats.shapiro(s1)
    norm_nm = stats.shapiro(s2)
    levene = stats.levene(s1, s2)

    print(f"Normality s1 (p): {norm_m.pvalue:.4f}")
    print(f"Normality s2 (p): {norm_nm.pvalue:.4f}")
    print(f"Equal Variance (p): {levene.pvalue:.4f}")

    # 4. Perform the Test
    if norm_m.pvalue > 0.05 and norm_nm.pvalue > 0.05 and levene.pvalue > 0.05:
        print("\nNormality and equal variance, use Independent t-test:")
        res = stats.ttest_ind(s1, s2, alternative=alternative)
    else:
        print("\nNo Normality, use Mann-Whitney U test:")
        res = stats.mannwhitneyu(s1, s2, alternative=alternative)

    print(f"Statistics: {res.statistic:.4f}")
    print(f"Final p-value: {res.pvalue:.4f}")
    print(f"Cohen's d: {cohens_d(s1, s2):.4f}")


def find_outliers(df: DataFrame, col: str):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    iqr = Q3 - Q1

    lower_bound = Q1 - 1.5 * iqr
    upper_bound = Q3 + 1.5 * iqr

    return df.filter((pl.col(col) < lower_bound) | (pl.col(col) > upper_bound))

