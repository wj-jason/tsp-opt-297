import os
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Path to log file
log_file = "log.txt"

# Specify directory to save plots
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)  # Create directory if not exists

# Initialize storage for parsed data
data = []
current_alpha = None

# Read and parse log file
with open(log_file, "r") as file:
    for line in file:
        line = line.strip()

        # Detect alpha values
        alpha_match = re.match(r"alpha=([\d.]+)", line)
        if alpha_match:
            current_alpha = float(alpha_match.group(1))

        # Detect test case results
        match = re.match(r"(.+?): avg_runtime=([\d.e+-]+), avg_cost=([\d.e+-]+)", line)
        if match:
            test_case, avg_runtime, avg_cost = match.groups()
            data.append({
                "Alpha": current_alpha,
                "Test Case": test_case,
                "Avg Runtime": float(avg_runtime),
                "Avg Cost": float(avg_cost)
            })

for i in data:
    print(i)

# Convert to Pandas DataFrame
df = pd.DataFrame(data)

# Create plots for each test case
for test_case in df["Test Case"].unique():
    subset = df[df["Test Case"] == test_case]

    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Plot avg_runtime
    color1 = 'tab:blue'
    ax1.set_xlabel("Alpha")
    ax1.set_ylabel("Avg Runtime", color=color1)
    sns.lineplot(data=subset, x="Alpha", y="Avg Runtime", ax=ax1, marker="o", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)

    # Plot avg_cost on a secondary axis
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel("Avg Cost", color=color2)
    sns.lineplot(data=subset, x="Alpha", y="Avg Cost", ax=ax2, marker="s", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    # Title and layout
    plt.title(test_case)
    fig.tight_layout()

    # Save plot
    filename = os.path.join(output_dir, f"{test_case.replace(' ', '_')}.png")
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)  # Close figure to free memory

# Compute overall averages per alpha
overall_avg = df.groupby("Alpha", as_index=False)[["Avg Runtime", "Avg Cost"]].mean()

# Plot total average runtime and cost
fig, ax1 = plt.subplots(figsize=(8, 5))

# Plot overall avg_runtime
color1 = 'tab:blue'
ax1.set_xlabel("Alpha")
ax1.set_ylabel("Total Avg Runtime", color=color1)
sns.lineplot(data=overall_avg, x="Alpha", y="Avg Runtime", ax=ax1, marker="o", color=color1)
ax1.tick_params(axis="y", labelcolor=color1)

# Plot overall avg_cost on secondary axis
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel("Total Avg Cost", color=color2)
sns.lineplot(data=overall_avg, x="Alpha", y="Avg Cost", ax=ax2, marker="s", color=color2)
ax2.tick_params(axis="y", labelcolor=color2)

# Title and layout
plt.title("Overall Average Runtime & Cost")
fig.tight_layout()

# Save overall plot
overall_filename = os.path.join(output_dir, "overall.png")
plt.savefig(overall_filename, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Plots saved in {output_dir}")
