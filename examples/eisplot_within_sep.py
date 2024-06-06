# creates two plots, mangnitude and phase 
# each plot has mean of each channel with SEM bars 

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
fig_magnitude, ax1 = plt.subplots(figsize=(6.5, 4.5))
fig_phase, ax2 = plt.subplots(figsize=(6.5, 4.5))
fig_magnitude.suptitle(f'Mean Impedance vs. Frequency ({title})', fontsize=16)
fig_phase.suptitle(f'Mean Phase vs. Frequency ({title})', fontsize=16)

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
    ax1.errorbar(frequencies, mean_magnitudes, yerr=sem_magnitudes, fmt=markers[marker_idx], color=colors[color_idx], ecolor='lightgray', elinewidth=3, capsize=0, markersize=3, label=legend_labels[n])

    # Plotting for this n - Phase
    ax2.errorbar(frequencies, mean_phases, yerr=sem_phases, fmt=markers[marker_idx], color=colors[color_idx], ecolor='lightgray', elinewidth=3, capsize=0, markersize=3, label=legend_labels[n])
    color_idx += 1
    marker_idx += 1


# Finalize Magnitude plot
ax1.set_xlabel('Frequency (Hz)', fontsize=14)
ax1.set_ylabel('Impedance (Ohm)', color='black', fontsize=14)
ax1.set_yscale('log')
ax1.set_xlim([0, 1100])
ax1.set_ylim([10**5, 10**8])
ax2.set_ylim([-100, 0])
# ax1.legend()
fig_magnitude.tight_layout()

# Finalize Phase plot
ax2.set_xlabel('Frequency (Hz)', fontsize=14)
ax2.set_ylabel('Phase (Degrees)', color='black', fontsize=14)
ax2.set_ylim([-60, 30])
ax2.legend()
fig_phase.tight_layout()

# Save the figures
magnitude_filename = f"{base_filename}_magnitude.png"
phase_filename = f"{base_filename}_phase.png"
# magnitude_filename = f"{base_filename}_magnitude_combined2.png"
# phase_filename = f"{base_filename}_phase_combined2.png"
magnitude_file_path = f"/Users/christopherwarren/pyxdaq/figures/{base_filename}/{magnitude_filename}"
phase_file_path = f"/Users/christopherwarren/pyxdaq/figures/{base_filename}/{phase_filename}"

fig_magnitude.savefig(magnitude_file_path, bbox_inches='tight')
fig_phase.savefig(phase_file_path, bbox_inches='tight')

print(f'Impedance data saved to {magnitude_filename}')
print(f'Phase data saved to {phase_filename}')

plt.close(fig_magnitude)  # Close the magnitude figure
plt.close(fig_phase)  # Close the phase figure