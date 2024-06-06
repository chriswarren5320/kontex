import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem
import os

# Constants
NUM_SWEEPS = 3
NUM_CHANNELS = 16

# Function to load data from a file
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

# Function to preprocess the data
def preprocess_data(df):
    if df.empty:
        return df
    try:
        df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
        df['Magnitude (Ohm)'] = pd.to_numeric(df['Magnitude (Ohm)'].str.strip('[]'), errors='coerce')
        df['Phase (Degrees)'] = pd.to_numeric(df['Phase (Degrees)'].str.strip('[]'), errors='coerce')
    except Exception:
        return pd.DataFrame()
    return df.dropna()

# Function to calculate complex impedance
def calculate_impedance(df):
    if df.empty:
        return np.array([])
    Z = df['Magnitude (Ohm)'] * np.exp(1j * np.deg2rad(df['Phase (Degrees)']))
    return Z.to_numpy()

# Function to generate Nyquist plot
def generate_nyquist_plot(real_mean, imag_mean, real_sem, imag_sem, title, output_file_path):
    plt.figure(figsize=(8, 8))
    plt.errorbar(real_mean, -imag_mean, xerr=real_sem, yerr=imag_sem, fmt='o-', markersize=5, linewidth=1, label='Mean with SEM')
    plt.xlabel('Re|G($\omega$)|')
    plt.ylabel('-Im|G($\omega$)|')
    plt.title(title)
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.savefig(output_file_path, bbox_inches='tight')
    plt.close()

# Function to process and plot data for a single channel
def process_channel_data(base_folder_name, base_filename_1, channel):
    real_parts_list = []
    imag_parts_list = []

    for i in range(1, NUM_SWEEPS + 1):
        file_path = f"/Users/christopherwarren/pyxdaq/data/{base_folder_name}/rawdata/{base_folder_name}_{base_filename_1}_{channel}_{i}.csv"
        df = preprocess_data(load_data(file_path))
        Z = calculate_impedance(df)

        if Z.size == 0:
            continue

        real_parts_list.append(Z.real)
        imag_parts_list.append(Z.imag)

    if not real_parts_list or not imag_parts_list:
        return

    real_parts = np.array(real_parts_list)
    imag_parts = np.array(imag_parts_list)
    real_mean = np.mean(real_parts, axis=0)
    real_sem = sem(real_parts, axis=0)
    imag_mean = np.mean(imag_parts, axis=0)
    imag_sem = sem(imag_parts, axis=0)

    output_file_path = f"/Users/christopherwarren/pyxdaq/data/{base_folder_name}/figures/nyquist/{base_folder_name}_{base_filename_1}_nyquist_{channel}.png"
    generate_nyquist_plot(real_mean, imag_mean, real_sem, imag_sem, f'Nyquist Plot for Channel {channel} (Mean with SEM)', output_file_path)

# Function to process and plot data for all channels
def process_all_channels_data(base_folder_name, base_filename_1):
    all_real_parts_list = []
    all_imag_parts_list = []

    for channel in range(NUM_CHANNELS):
        real_parts_list = []
        imag_parts_list = []

        for i in range(1, NUM_SWEEPS + 1):
            file_path = f"/Users/christopherwarren/pyxdaq/data/{base_folder_name}/rawdata/{base_folder_name}_{base_filename_1}_{channel}_{i}.csv"
            df = preprocess_data(load_data(file_path))
            Z = calculate_impedance(df)

            if Z.size == 0:
                continue

            real_parts_list.append(Z.real)
            imag_parts_list.append(Z.imag)

        if not real_parts_list or not imag_parts_list:
            continue

        real_parts = np.array(real_parts_list)
        imag_parts = np.array(imag_parts_list)
        all_real_parts_list.append(real_parts)
        all_imag_parts_list.append(imag_parts)

    if not all_real_parts_list or not all_imag_parts_list:
        return

    all_real_parts = np.concatenate(all_real_parts_list, axis=1)
    all_imag_parts = np.concatenate(all_imag_parts_list, axis=1)
    real_mean = np.mean(all_real_parts, axis=1)
    real_sem = sem(all_real_parts, axis=1)
    imag_mean = np.mean(all_imag_parts, axis=1)
    imag_sem = sem(all_imag_parts, axis=1)

    output_file_path = f"/Users/christopherwarren/pyxdaq/data/{base_folder_name}/figures/nyquist/combined_nyquist_all_channels.png"
    generate_nyquist_plot(real_mean, imag_mean, real_sem, imag_sem, 'Combined Nyquist Plot (All Channels) (Mean with SEM)', output_file_path)

# Main execution
def main():
    base_folder_name = input("Enter the folder where the data is stored (i.e., 01may24_1): ")
    base_filename_1 = input("Enter the description for your sweep (i.e., preplate): ")

    # Create folder in figures folder for Nyquist plots
    save_directory = f"/Users/christopherwarren/pyxdaq/data/{base_folder_name}/figures/nyquist"
    os.makedirs(save_directory, exist_ok=True)

    for channel in range(NUM_CHANNELS):
        process_channel_data(base_folder_name, base_filename_1, channel)

    process_all_channels_data(base_folder_name, base_filename_1)

if __name__ == "__main__":
    main()
