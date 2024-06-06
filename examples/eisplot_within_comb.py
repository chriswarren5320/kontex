import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem  # Import SEM calculation function

# Function to load and preprocess data
def load_and_preprocess(file_path):
    df = pd.read_csv(file_path)
    df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
    df['Magnitude (Ohm)'] = pd.to_numeric(df['Magnitude (Ohm)'], errors='coerce')
    df['Phase (Degrees)'] = pd.to_numeric(df['Phase (Degrees)'], errors='coerce')
    df = df.dropna()
    return df

# Ask for base filename
base_filename = input("Enter your base file name: ")
title = input("What do you want in the graph titles: ")
channel_input = input("Enter the channel numbers separated by a comma (e.g., 0,1,2): ")
channels = [int(x.strip()) for x in channel_input.split(',')]

# Prepare the plots outside the loop
fig, ax1 = plt.subplots(figsize=(6.5, 4.5))
ax2 = ax1.twinx()

colors = [
    'tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple', 
    'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan', 
    'darkred', 'darkblue', 'darkgreen', 'darkorange', 'darkviolet', 
    'lightcoral', 'lightblue', 'lightgreen', 'peachpuff', 'mediumpurple', 
    'mediumseagreen', 'coral', 'skyblue', 'lime', 'deepskyblue', 
    'tomato', 'navy', 'slateblue', 'limegreen', 'goldenrod', 
    'forestgreen', 'aqua', 'dodgerblue', 'plum', 'tan'
]
color_idx = 0

markers = [
    "o", "v", "^", "<", ">", "1", "2", "3", "4", "s",
    "p", "*", "h", "H", "+", "x"
]
marker_idx = 0

legend_labels = ["Control", "10nA, 2.5 min", "10nA, 5 min", "10nA, 5 min", "10nA, 10 min", "10nA, 20 min",
                            "20nA, 2.5 min", "20nA, 5 min", "20nA, 5 min", "20nA, 10 min", "20nA, 20 min",
                            "40nA, 2.5 min", "40nA, 5 min", "40nA, 5 min", "40nA, 10 min", "40nA, 20 min"]


# Loop only over the specified indices
# [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

for n in channels:
    # Construct input filenames for the current n
    input_filenames = [f"{base_filename}_{n}_{i}" for i in range(1, 4)]

    # Construct file paths using the input filenames
    file_paths = [f"/Users/christopherwarren/pyxdaq/rawdata/{filename}.csv" for filename in input_filenames]

    # Use the list of file paths in the data loading and processing part
    dataframes = [load_and_preprocess(file_path) for file_path in file_paths]

    # Concatenate the dataframes for mean and SEM calculations
    df_concat = pd.concat(dataframes)

    # Group by frequency and calculate mean and SEM
    grouped = df_concat.groupby('Frequency (Hz)')
    means = grouped.mean()
    sems = grouped.sem()

    # Extract mean and SEM values for plotting
    frequencies = means.index.values
    mean_magnitudes = means['Magnitude (Ohm)'].values
    mean_phases = means['Phase (Degrees)'].values
    sem_magnitudes = sems['Magnitude (Ohm)'].values
    sem_phases = sems['Phase (Degrees)'].values

    # Plotting for this n - Impedance (Magnitude)
    ax1.errorbar(frequencies, mean_magnitudes, yerr=sem_magnitudes, fmt=markers[0], color=colors[color_idx], ecolor='lightgray', elinewidth=3, capsize=0, markersize=3, label=legend_labels[n])
    # Plotting for this n - Phase
    ax2.errorbar(frequencies, mean_phases, yerr=sem_phases, fmt=markers[1], color=colors[color_idx], ecolor='lightgray', elinewidth=3, capsize=0, markersize=3, label=legend_labels[n])
    color_idx += 1
    # marker_idx += 1

# Finalize Magnitude plot
ax1.set_xlabel('Frequency (Hz)', fontsize=14)
ax1.set_ylabel('Impedance (Ohm)', color='black', fontsize=14)
ax2.set_ylabel('Phase (Degrees)', color='black', fontsize=14)
ax1.set_yscale('log')
ax1.set_xlim([0, 1100])
ax1.set_ylim([10**5, 10**8])
ax2.set_ylim([-100, 0])

# Adjust layout for better fit
fig.tight_layout()

# Adding legend
# Since we have two axes, we need to handle legends for both.
# Collect all legends' handles and labels, then display them together.
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
# plt.legend(handles1 + handles2, labels1 + labels2, facecolor='white', edgecolor='black', framealpha=1)
# unused legend parameters: facecolor='white', edgecolor='black', framealpha=1

# Save the figures
magnitude_filename = f"{base_filename}_within_combined.png"
magnitude_file_path = f"/Users/christopherwarren/pyxdaq/figures/{magnitude_filename}"

plt.title(f'Mean Impedance and Phase vs. Frequency ({title})', fontsize=14)
fig.savefig(magnitude_file_path, bbox_inches='tight')

print(f'Impedance data saved to {magnitude_filename}')

plt.close(fig)  # Close the magnitude figure