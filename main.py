import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob


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


# --- Main Script ---

# 1. Load Data
log_folder = "./logs"  # Ensure this matches your folder name
df = load_and_aggregate_logs(log_folder)

# Check data before plotting
print(df.head())

df_no_music = df.filter(pl.col("Condition") == "No Music")
df_music = df.filter(pl.col("Condition") == "Music")
print(df_no_music.mean(), df_music.mean())


# 2. Plotting (Slopegraph)
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# A pointplot connects points with the same 'hue' (Subject_ID) across X variables
sns.pointplot(
    data=df,
    x="Condition",
    y="Success_Count",
    hue="Subject_ID",
    palette="viridis",  # Distinct colors for subjects
    markers="o",
    dodge=False  # Important: keeps lines straight (slopegraph style)
)

plt.title("Impact of Music on Click Success (Within-Subject)", fontsize=14)
plt.ylabel("Number of Successful Clicks")
plt.xlabel("Condition")

# Move legend outside if it blocks data
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Subject ID")
plt.tight_layout()

plt.show()