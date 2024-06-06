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

# Function to process files and calculate mean and SEM for each device
def process_files(base_filename, num_channels=16):
    all_magnitudes = []
    all_phases = []
    all_frequencies = []

    for n in range(num_channels):
        magnitudes = []
        phases = []
        frequencies = []

        for i in range(1, 4):  # Assuming 3 sweeps per channel
            input_file_path = f"/Users/christopherwarren/pyxdaq/rawdata/{base_filename}_{n}_{i}.csv"
            df = load_and_preprocess(input_file_path)

            # Ensure all sweeps have the same frequencies
            if frequencies and not np.array_equal(frequencies[-1], df['Frequency (Hz)'].values):
                raise ValueError("Frequency values do not match across sweeps")

            # Store magnitudes, phases, and frequencies
            magnitudes.append(df['Magnitude (Ohm)'].values)
            phases.append(df['Phase (Degrees)'].values)
            frequencies.append(df['Frequency (Hz)'].values)

        # Convert lists to numpy arrays and store them
        all_magnitudes.append(np.array(magnitudes))
        all_phases.append(np.array(phases))
        all_frequencies.append(np.array(frequencies)[0])  # Frequencies should be the same for all measurements

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

# Ask for two base filenames
base_filename_1 = input("Enter your first base file name: ")
base_filename_2 = input("Enter your second base file name: ")
base_filename_save = input("Enter the folder where your files will be saved (you must create this folder first): ")

# Loop from n = 0 to n = 15
for n in range(16):
    # Construct input filenames for the current n for both base filenames
    input_filenames_1 = [f"{base_filename_1}_{n}_{i}" for i in range(1, 4)]
    input_filenames_2 = [f"{base_filename_2}_{n}_{i}" for i in range(1, 4)]

    # Construct file paths using the input filenames
    file_paths_1 = [f"/Users/christopherwarren/pyxdaq/rawdata/{filename}.csv" for filename in input_filenames_1]
    file_paths_2 = [f"/Users/christopherwarren/pyxdaq/rawdata/{filename}.csv" for filename in input_filenames_2]

    # Process files for both sets
    dataframes_1 = [load_and_preprocess(file_path) for file_path in file_paths_1]
    dataframes_2 = [load_and_preprocess(file_path) for file_path in file_paths_2]

    # Concatenate and process dataframes for each set
    df_concat_1 = pd.concat(dataframes_1)
    df_concat_2 = pd.concat(dataframes_2)

    # Calculate mean and SEM for each set
    grouped_1 = df_concat_1.groupby('Frequency (Hz)')
    means_1 = grouped_1.mean()
    sems_1 = grouped_1.sem()

    grouped_2 = df_concat_2.groupby('Frequency (Hz)')
    means_2 = grouped_2.mean()
    sems_2 = grouped_2.sem()

    # Prepare plotting data
    frequencies_1 = means_1.index.values
    frequencies_2 = means_2.index.values

    # Plotting
    fig, ax1 = plt.subplots(figsize=(6.5, 4.5))

    # Set common axis labels
    ax1.set_xlabel('Frequency (Hz)', fontsize=14)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([40, 1400])
    ax1.set_ylim([10**3, 10**8])

    # Magnitude for base_filename_1
    ax1.errorbar(frequencies_1, means_1['Magnitude (Ohm)'].values, yerr=sems_1['Magnitude (Ohm)'].values, fmt='--', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Magnitude')
    # Phase for base_filename_1
    ax2 = ax1.twinx()
    ax2.errorbar(frequencies_1, means_1['Phase (Degrees)'].values, yerr=sems_1['Phase (Degrees)'].values, fmt='--', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Phase')

    # Magnitude for base_filename_2 with a different marker
    ax1.errorbar(frequencies_2, means_2['Magnitude (Ohm)'].values, yerr=sems_2['Magnitude (Ohm)'].values, fmt='-', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Magnitude')
    # Phase for base_filename_2 with a different marker
    ax2.errorbar(frequencies_2, means_2['Phase (Degrees)'].values, yerr=sems_2['Phase (Degrees)'].values, fmt='-', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Phase')

    # Setting axis labels for left (magnitude) and right (phase) y-axes
    ax1.set_ylabel('Magnitude (Ohm)', color='tab:red', fontsize=14)
    ax2.set_ylabel('Phase (Degrees)', color='tab:blue', fontsize=14)
    ax2.set_ylim([-100, 0])

    # Adjust layout for better fit
    fig.tight_layout()

    # Adding legend
    # Since we have two axes, we need to handle legends for both.
    # Collect all legends' handles and labels, then display them together.
    #handles1, labels1 = ax1.get_legend_handles_labels()
    #handles2, labels2 = ax2.get_legend_handles_labels()
    #plt.legend(handles1 + handles2, labels1 + labels2, loc='lower left')
    textstr = f'-- Gold \n— PEDOT:PSS \nSEM error bars \nN = 1 channel, 3 sweeps each channel'
    plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Title and save
    #plt.title(f'Mean Impedance and Phase vs. Frequency with SEM for Channel {n}', fontsize=14)
    plt.title(f'Bodi Plot for Channel {n}', fontsize=14)
    output_file_path = f"/Users/christopherwarren/pyxdaq/figures/{base_filename_save}/combined_{n}.png"
    fig.savefig(output_file_path, bbox_inches='tight')

    print(f'Data saved to combined_{n}.png')
    plt.close(fig)  # Close the figure

# Generate a combined Bode plot comparing the two devices
def generate_combined_all_channels_bode_plot(base_filename_1, base_filename_2, base_filename_save):
    frequencies_1, magnitude_mean_1, magnitude_sem_1, phase_mean_1, phase_sem_1 = process_files(base_filename_1)
    frequencies_2, magnitude_mean_2, magnitude_sem_2, phase_mean_2, phase_sem_2 = process_files(base_filename_2)

    # Check that frequencies match
    if not np.array_equal(frequencies_1, frequencies_2):
        raise ValueError("Frequency values do not match between the two devices")

    # Plotting Magnitude
    fig, ax1 = plt.subplots(figsize=(6.5, 4.5))
    ax1.set_xlabel('Frequency (Hz)', fontsize=14)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([40, 1400])
    ax1.set_ylim([10**3, 10**8])
    ax1.errorbar(frequencies_1, magnitude_mean_1, yerr=magnitude_sem_1, fmt='--', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Magnitude')
    ax1.errorbar(frequencies_2, magnitude_mean_2, yerr=magnitude_sem_2, fmt='-', color='tab:red', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Magnitude')
    ax1.set_ylabel('Magnitude (Ohm)', color = 'tab:red', fontsize=14)
    #ax1.legend(loc='lower left')

    # Plotting Phase
    ax2 = ax1.twinx()
    ax2.set_ylim([-100, 0])
    ax2.errorbar(frequencies_1, phase_mean_1, yerr=phase_sem_1, fmt='--', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_1} Phase')
    ax2.errorbar(frequencies_2, phase_mean_2, yerr=phase_sem_2, fmt='-', color='tab:blue', ecolor='lightgray', elinewidth=3, capsize=0, label=f'{base_filename_2} Phase')
    ax2.set_ylabel('Phase (Degrees)', color = 'tab:blue', fontsize=14)
    #ax2.legend(loc='lower right')
    textstr = f'-- Gold \n— PEDOT:PSS \nSEM error bars \nN = 16 channels, 3 sweeps each channel'
    plt.gcf().text(0.16, 0.2, textstr, fontsize=8, color='black', ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.5))


    # Adjust layout for better fit
    fig.tight_layout()

    # Adding title and saving
    plt.title('Bodi Plot for All Channels', fontsize=14)
    output_file_path = f"/Users/christopherwarren/pyxdaq/figures/{base_filename_save}/combined_bode_all_channels.png"
    fig.savefig(output_file_path, bbox_inches='tight')
    plt.close()

# Generate the combined Bode plot for all channels comparing the two devices
generate_combined_all_channels_bode_plot(base_filename_1, base_filename_2, base_filename_save)
print("Combined Bode plot for all channels comparing the two devices done.")
