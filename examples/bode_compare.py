import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem
import os
import ast

# Function to load and preprocess data
def load_and_preprocess(file_path):
    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    
    # Debugging: Print out the raw data loaded
    #print(f"Raw data:\n{df.head()}")
    
    # Convert string representation of lists to actual lists and then extract the first element
    df['Magnitude (Ohm)'] = df['Magnitude (Ohm)'].apply(lambda x: ast.literal_eval(x)[0])
    df['Phase (Degrees)'] = df['Phase (Degrees)'].apply(lambda x: ast.literal_eval(x)[0])
    
    df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
    df['Magnitude (Ohm)'] = pd.to_numeric(df['Magnitude (Ohm)'], errors='coerce')
    df['Phase (Degrees)'] = pd.to_numeric(df['Phase (Degrees)'], errors='coerce')
    
    # Debugging: Print out the data after conversion
    #print(f"Data after conversion to numeric:\n{df.head()}")
    
    df = df.dropna()
    #print(f"Data after dropping NaN values:\n{df.head()}")
    return df

# Function to process files and calculate mean and SEM for each device
def process_files(base_filename, description, num_channels=16):
    all_magnitudes = []
    all_phases = []
    all_frequencies = []

    for n in range(num_channels):
        magnitudes = []
        phases = []
        frequencies = []

        for i in range(1, 4):  # Assuming 3 sweeps per channel
            input_file_path = f"/Users/christopherwarren/pyxdaq/data/{base_filename}/rawdata/{base_filename}_{description}_{n}_{i}.csv"
            
            if not os.path.exists(input_file_path):
                print(f"File not found: {input_file_path}")
                continue
            
            df = load_and_preprocess(input_file_path)

            # Ensure all sweeps have the same frequencies
            if frequencies and not np.array_equal(frequencies[-1], df['Frequency (Hz)'].values):
                raise ValueError("Frequency values do not match across sweeps")

            # Store magnitudes, phases, and frequencies
            magnitudes.append(df['Magnitude (Ohm)'].values)
            phases.append(df['Phase (Degrees)'].values)
            frequencies.append(df['Frequency (Hz)'].values)

        if magnitudes:
            # Convert lists to numpy arrays and store them
            all_magnitudes.append(np.array(magnitudes))
            all_phases.append(np.array(phases))
            all_frequencies.append(np.array(frequencies)[0])  # Frequencies should be the same for all measurements

    if not all_magnitudes or not all_phases:
        raise ValueError("No data found for processing.")

    # Combine data from all channels
    combined_magnitudes = np.concatenate(all_magnitudes, axis=0)
    combined_phases = np.concatenate(all_phases, axis=0)
    combined_frequencies = all_frequencies[0]  # Frequencies should be the same for all measurements

    # Calculate mean and SEM
    magnitude_mean = np.mean(combined_magnitudes, axis=0)
    magnitude_sem = sem(combined_magnitudes, axis=0)
    phase_mean = np.mean(combined_phases, axis=0)
    phase_sem = sem(combined_phases, axis=0)

    return combined_frequencies, magnitude_mean, magnitude_sem, phase_mean, phase_sem

base_foldername = input("Enter the folder where the data is stored (i.e., 01may24_1): ")
base_filename_1 = input("Enter the description for your first sweep (i.e., preplate): ")
base_filename_2 = input("Enter the description for your second sweep (i.e., postplate): ")

save_directory = f"/Users/christopherwarren/pyxdaq/data/{base_foldername}/figures/bode_combined"
os.makedirs(save_directory, exist_ok=True)

for n in range(16):
    input_filenames_1 = [f"{base_foldername}_{base_filename_1}_{n}_{i}" for i in range(1, 4)]
    input_filenames_2 = [f"{base_foldername}_{base_filename_2}_{n}_{i}" for i in range(1, 4)]

    file_paths_1 = [f"/Users/christopherwarren/pyxdaq/data/{base_foldername}/rawdata/{filename}.csv" for filename in input_filenames_1]
    file_paths_2 = [f"/Users/christopherwarren/pyxdaq/data/{base_foldername}/rawdata/{filename}.csv" for filename in input_filenames_2]

    dataframes_1 = [load_and_preprocess(file_path) for file_path in file_paths_1 if os.path.exists(file_path)]
    dataframes_2 = [load_and_preprocess(file_path) for file_path in file_paths_2 if os.path.exists(file_path)]

    if not dataframes_1 or not dataframes_2:
        print(f"No data found for channel {n}. Skipping.")
        continue

    df_concat_1 = pd.concat(dataframes_1)
    df_concat_2 = pd.concat(dataframes_2)

    grouped_1 = df_concat_1.groupby('Frequency (Hz)')
    means_1 = grouped_1.mean()
    sems_1 = grouped_1.sem()

    grouped_2 = df_concat_2.groupby('Frequency (Hz)')
    means_2 = grouped_2.mean()
    sems_2 = grouped_2.sem()

    print(f"Channel {n} - {base_filename_1} means:\n{means_1}")
    print(f"Channel {n} - {base_filename_1} sems:\n{sems_1}")
    print(f"Channel {n} - {base_filename_2} means:\n{means_2}")
    print(f"Channel {n} - {base_filename_2} sems:\n{sems_2}")

    frequencies_1 = means_1.index.values
    frequencies_2 = means_2.index.values

    fig, ax1 = plt.subplots(figsize=(6.5, 4.5))
    ax1.set_xlabel('Frequency (Hz)', fontsize=14)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([40, 1400])
    ax1.set_ylim([10**3, 10**8])

    ax1.errorbar(frequencies_1, means_1['Magnitude (Ohm)'].values, yerr=sems_1['Magnitude (Ohm)'].values, fmt='--', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Magnitude')
    ax2 = ax1.twinx()
    ax2.errorbar(frequencies_1, means_1['Phase (Degrees)'].values, yerr=sems_1['Phase (Degrees)'].values, fmt='--', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Phase')

    ax1.errorbar(frequencies_2, means_2['Magnitude (Ohm)'].values, yerr=sems_2['Magnitude (Ohm)'].values, fmt='-', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Magnitude')
    ax2.errorbar(frequencies_2, means_2['Phase (Degrees)'].values, yerr=sems_2['Phase (Degrees)'].values, fmt='-', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Phase')

    ax1.set_ylabel('Magnitude (Ohm)', color='tab:red', fontsize=14)
    ax2.set_ylabel('Phase (Degrees)', color='tab:blue', fontsize=14)
    ax2.set_ylim([-100, 0])
    fig.tight_layout()

    textstr = f'-- Gold \n— PEDOT:PSS \nSEM error bars \nN = 1 channel, 3 sweeps each channel'
    plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    plt.title(f'Bodi Plot for Channel {n}', fontsize=14)
    output_file_path = f"{save_directory}/bode_combined_{n}.png"
    fig.savefig(output_file_path, bbox_inches='tight')

    print(f"Data saved to {output_file_path}")
    plt.close(fig)

def generate_combined_all_channels_bode_plot(base_filename, base_filename_1, base_filename_2, save_directory):
    frequencies_1, magnitude_mean_1, magnitude_sem_1, phase_mean_1, phase_sem_1 = process_files(base_filename, base_filename_1)
    frequencies_2, magnitude_mean_2, magnitude_sem_2, phase_mean_2, phase_sem_2 = process_files(base_filename, base_filename_2)

    if not np.array_equal(frequencies_1, frequencies_2):
        raise ValueError("Frequency values do not match between the two devices")

    fig, ax1 = plt.subplots(figsize=(6.5, 4.5))
    ax1.set_xlabel('Frequency (Hz)', fontsize=14)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([40, 1400])
    ax1.set_ylim([10**3, 10**8])
    ax1.errorbar(frequencies_1, magnitude_mean_1, yerr=magnitude_sem_1, fmt='--', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Magnitude')
    ax1.errorbar(frequencies_2, magnitude_mean_2, yerr=magnitude_sem_2, fmt='-', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Magnitude')
    ax1.set_ylabel('Magnitude (Ohm)', color='tab:red', fontsize=14)

    ax2 = ax1.twinx()
    ax2.set_ylim([-100, 0])
    ax2.errorbar(frequencies_1, phase_mean_1, yerr=phase_sem_1, fmt='--', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Phase')
    ax2.errorbar(frequencies_2, phase_mean_2, yerr=phase_sem_2, fmt='-', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Phase')
    ax2.set_ylabel('Phase (Degrees)', color='tab:blue', fontsize=14)

    fig.tight_layout()

    textstr = f'-- Gold \n— PEDOT:PSS \nSEM error bars \nN = 16 channels, 3 sweeps each channel'
    plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    plt.title('Bodi Plot for All Channels', fontsize=14)
    output_file_path = f"{save_directory}/bode_combined_all_channels.png"
    fig.savefig(output_file_path, bbox_inches='tight')
    plt.close()

generate_combined_all_channels_bode_plot(base_foldername, base_filename_1, base_filename_2, save_directory)
print("Combined Bode plot for all channels comparing the two devices done.")
