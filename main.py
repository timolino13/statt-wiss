import glob
import os

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
from polars import Series
from scipy import stats

def load_and_aggregate_logs(log_folder_path):
    """
    Reads all CSV logs in the folder, aggregates hits/errors,
    and returns a summary DataFrame.
    """
    aggregated_data = []

    # Get list of all files in the folder
    file_paths = glob.glob(os.path.join(log_folder_path, "*"))

    for file_path in file_paths:
        filename = os.path.basename(file_path)

        # --- 1. Parse Filename ---
        # Splitting "1_m.csv" -> "1", "m"
        name_no_ext = os.path.splitext(filename)[0]
        parts = name_no_ext.split('_')

        subject_id = parts[0]  # Handles IDs with underscores if any
        condition_code = parts[-1]  # 'm' or 'b'

        # Map codes to readable labels
        condition_map = {'m': 'Music', 'b': 'No Music'}
        condition = condition_map.get(condition_code, 'Unknown')

        # --- 2. Load Data with Polars ---
        try:
            df = pl.read_csv(file_path)

            # --- 3. Aggregate Data ---
            # Count True for Success, False for Error
            # Adjust column name "shape_hit" and values if they differ in your raw files
            success_count = df.filter(pl.col("shape_hit") == True).height
            error_count = df.filter(pl.col("shape_hit") == False).height

            aggregated_data.append({
                "Subject_ID": subject_id,
                "Condition": condition,
                "Success_Count": success_count,
                "Error_Count": error_count
            })

        except Exception as e:
            print(f"Error reading {filename}: {e}")

    return pl.DataFrame(aggregated_data)

def tukys_fences(df_col: Series):
    q1 = df_col.quantile(0.25)
    q3 = df_col.quantile(0.75)
    iqr = q3 - q1
    return q1 - iqr * 1.5, q3 + iqr * 1.5

log_folder = "./logs"
df = load_and_aggregate_logs(log_folder)

df_no_music = df.filter(pl.col("Condition") == "No Music")
success_no_music = df_no_music["Success_Count"]
df_music = df.filter(pl.col("Condition") == "Music")
success_music = df_music["Success_Count"]

order = ["No Music", "Music"]

# Visualization
sns.boxplot(
    data=df,
    x="Condition",
    y="Success_Count",
    order=order,
    showfliers=True
)

# Overlay individual subject points for context
sns.stripplot(
    data=df,
    x="Condition",
    y="Success_Count",
    order=order,
    color="black",
    size=6,
    jitter=True,
    alpha=0.7
)

plt.title("Distribution of Successful Clicks: With vs Without Music", fontsize=14)
plt.ylabel("Number of Successful Clicks")
plt.xlabel("Condition")
plt.tight_layout()
plt.show()

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

sns.pointplot(
    data=df,
    x="Condition",
    y="Success_Count",
    hue="Subject_ID",
    palette="viridis",
    markers="o",
    dodge=False
)

plt.title("Impact of Music on Click Success (Within-Subject)", fontsize=14)
plt.ylabel("Number of Successful Clicks")
plt.xlabel("Condition")

# Move legend outside if it blocks data
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Subject ID")
plt.tight_layout()

plt.show()

# Test for normality
shapiro_no_music = stats.shapiro(success_no_music)
shapiro_music = stats.shapiro(success_music)

print("Shapiro Wilk")
print(f"No Music p-value: {shapiro_no_music.pvalue}")
print(f"No Music p-value: {shapiro_music.pvalue}")

# Test for variance equality
levene = stats.levene(success_no_music, success_music)

print("Levene")
print(f"Levene p-value: {levene.pvalue}")

# Descriptive statistics
print("Descriptive statistics")
print(f"No Music mean: {success_no_music.mean()}, std: {success_no_music.std()}, fences: {tukys_fences(success_no_music)}")
print(f"Music mean: {success_music.mean()}, std: {success_music.std()}, fences: {tukys_fences(success_music)}")

# Related t-test
t_test_rel = stats.ttest_rel(success_no_music, success_music)
print("Related T-Test")
print(f"T-Test p-value: {t_test_rel.pvalue}")