import time
import pandas as pd
import pathlib  # allows for creating new directories
from pyxdaq.xdaq import get_XDAQ, XDAQ
from pyxdaq.stim import enable_stim
from pyxdaq.constants import StimStepSize, StimShape, StartPolarity, TriggerEvent, TriggerPolarity
from pyxdaq.impedance import Frequency, Strategy
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem  # Import SEM calculation function


def flatten_list_column(df, column_name):
    df[column_name] = df[column_name].apply(lambda x: x.strip('[]')).astype(float)
    return df

def load_and_preprocess(file_path):
    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    # print(f"Data loaded from {file_path}, first few rows:\n{df.head()}")
    df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
    df['Magnitude (Ohm)'] = pd.to_numeric(df['Magnitude (Ohm)'].apply(lambda x: x.strip('[]')), errors='coerce')
    df['Phase (Degrees)'] = pd.to_numeric(df['Phase (Degrees)'].apply(lambda x: x.strip('[]')), errors='coerce')
    df = df.dropna()
    return df

# Prompts for data used in file naming
date = input('What is todays date? We suggest "DayMonthYear" (i.e.,  01may24): ')
device_number = input('What is the device number? ')
sweep_type = input('What is the sweep type? We suggest "preplate" or "postplate: ')
readme = input('What text do you want in the README file associated with this sweep? We suggest a description of the device and the sweeping conditions. ')

# Creates new folders to store data
base_file_name = f"{date}_{device_number}_{sweep_type}"
base_file_path = f"/Users/christopherwarren/pyxdaq/data/{date}_{device_number}"
new_dir = pathlib.Path(base_file_path)
new_dir.mkdir(parents=True, exist_ok=True)

# Create subfolders for raw data and figures
rawdata_dir = new_dir / 'rawdata'
figures_dir = new_dir / 'figures'
figures_sweep_dir = figures_dir / sweep_type  # Corrected line
rawdata_dir.mkdir(parents=True, exist_ok=True)
figures_dir.mkdir(parents=True, exist_ok=True)
figures_sweep_dir.mkdir(parents=True, exist_ok=True)

# Write the README file inside the new directory
new_file = new_dir / f'{sweep_type}_README.txt' 
new_file.write_text(readme)

# Prompt for user specified channel numbers
channel_input = input("Enter the channel numbers separated by a comma (e.g., 0,1,2): ")
channels = [int(x.strip()) for x in channel_input.split(',')]

# Actual order of channels based on current PCB design
actual_order = [14, 12, 4, 5, 10, 11, 2, 3, 8, 9, 0, 1, 13, 6, 7, 15]

# XDAQ connection and setup
xdaq = get_XDAQ(rhs=True)
print(xdaq.ports)

# Initialize lists to accumulate data for all channels
all_magnitudes = []
all_phases = []
all_frequencies = None

# Loop over each channel
for target_channel in channels:
    actual_channel = actual_order[target_channel]

    # Perform three frequency sweeps for each channel
    for sweep_number in range(1, 4):
        # Lists to store frequency, magnitude, and phase values
        frequencies = []
        magnitudes = []
        phases = []

        # Perform frequency sweep
        for freq in range(50, 1150, 100):
            print(f'Channel {target_channel}: Checking impedance at {freq} Hz, Sweep {sweep_number}')

            magnitude, phase = xdaq.measure_impedance(
                frequency=Frequency(freq),
                strategy=Strategy.from_duration(0.2),
                channels=[actual_channel],
                progress=False
            )

            frequencies.append(freq)
            magnitudes.append(magnitude[0])
            phases.append(phase[0])

        # Data preparation for saving
        data = {
            "Frequency (Hz)": frequencies,
            "Magnitude (Ohm)": magnitudes,
            "Phase (Degrees)": phases
        }
        df = pd.DataFrame(data)

        # Generate modified file path for each sweep
        modified_file_path = f"{rawdata_dir}/{base_file_name}_{target_channel}_{sweep_number}.csv"

        # Save the DataFrame to a CSV file
        df.to_csv(modified_file_path, index=False)
        print(f'Data saved to {modified_file_path}')

    # Construct input filenames for the current n
    input_filenames = [f"{base_file_name}_{target_channel}_{i}" for i in range(1, 4)]

    # Construct file paths using the input filenames
    file_paths = [f"{rawdata_dir}/{filename}.csv" for filename in input_filenames]

    # Use the list of file paths in the data loading and processing part
    dataframes = [load_and_preprocess(file_path) for file_path in file_paths]

    # Concatenate the dataframes for mean and SEM calculations
    df_concat = pd.concat(dataframes)

    # Group by frequency and calculate mean and SEM
    grouped = df_concat.groupby('Frequency (Hz)')
    means = grouped.mean()
    sems = grouped.sem()

    # Extract mean values for plotting
    frequencies = means.index.values
    mean_magnitudes = means['Magnitude (Ohm)'].values
    mean_phases = means['Phase (Degrees)'].values

    # Extract SEM values for error bars
    sem_magnitudes = sems['Magnitude (Ohm)'].values
    sem_phases = sems['Phase (Degrees)'].values

    # Append data for all channels
    all_magnitudes.append(mean_magnitudes)
    all_phases.append(mean_phases)

    if all_frequencies is None:
        all_frequencies = frequencies
    else:
        # Validate that frequencies are consistent
        if not np.array_equal(all_frequencies, frequencies):
            print(f"Warning: Frequency mismatch for channel {target_channel}")

    # Plotting
    fig, ax1 = plt.subplots(figsize=(6.5, 4.5))  # sets size

    # Magnitude plot with SEM bars
    color = 'tab:red'
    ax1.set_xlabel('Frequency (Hz)', fontsize=14)
    ax1.set_ylabel('Impedance (Ohm)', color=color, fontsize=14)
    ax1.errorbar(frequencies, mean_magnitudes, yerr=sem_magnitudes, fmt='--', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.set_xlim([0, 1100])
    ax1.set_ylim([10**3, 10**8])

    # Create a twin Axes for phase
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Phase (Degrees)', color=color, fontsize=14)
    ax2.errorbar(frequencies, mean_phases, yerr=sem_phases, fmt='--', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)
    ax2.set_ylim([-100, 10])
    textstr = f'-- Gold \nSEM error bars \nN = 1 channel, 3 sweeps each channel'
    plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    fig.tight_layout()
    plt.title(f'Bodi Plot for Channel {target_channel}', fontsize=14)
    output_file_name = f"{figures_sweep_dir}/{base_file_name}_{target_channel}.png"
    plt.savefig(output_file_name, bbox_inches='tight')

    print(f'Data saved to {output_file_name}.png')
    plt.close(fig)  # Close the figure to avoid display issues in some environments

# Convert lists to numpy arrays for combined calculations
all_magnitudes = np.array(all_magnitudes)
all_phases = np.array(all_phases)

# Check that the shapes of combined arrays are correct
print(f"Shape of all_magnitudes: {all_magnitudes.shape}")
print(f"Shape of all_phases: {all_phases.shape}")
print(f"Length of all_frequencies: {len(all_frequencies)}")

# Calculate mean and SEM for all channels
magnitude_mean = np.mean(all_magnitudes, axis=0)
magnitude_sem = sem(all_magnitudes, axis=0)
phase_mean = np.mean(all_phases, axis=0)
phase_sem = sem(all_phases, axis=0)

# Plotting combined data for all channels
fig, ax1 = plt.subplots(figsize=(6.5, 4.5))  # sets size

# Magnitude plot with SEM bars
color = 'tab:red'
ax1.set_xlabel('Frequency (Hz)', fontsize=14)
ax1.set_ylabel('Impedance (Ohm)', color=color, fontsize=14)
ax1.errorbar(all_frequencies, magnitude_mean, yerr=magnitude_sem, fmt='--', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)
ax1.set_yscale('log')

ax1.set_xscale('log')
ax1.set_xlim([0, 1100])
ax1.set_ylim([10**3, 10**8])

# Create a twin Axes for phase
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Phase (Degrees)', color=color, fontsize=14)
ax2.errorbar(all_frequencies, phase_mean, yerr=phase_sem, fmt='--', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)
ax2.set_ylim([-100, 10])
textstr = f'-- Gold \nSEM error bars \nN = 16 channels, 3 sweeps each channel'
plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

fig.tight_layout()
plt.title('Bodi Plot for All Channels', fontsize=14)
output_file_name = f"{figures_sweep_dir}/{base_file_name}_all_channels.png"
plt.savefig(output_file_name, bbox_inches='tight')

print(f'Combined data saved to {output_file_name}.png')
plt.close(fig)  # Close the figure to avoid display issues in some environments
