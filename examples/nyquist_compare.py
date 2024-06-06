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

# Function to generate combined Nyquist plot for two devices
def generate_combined_nyquist_plot(base_filename_1, base_filename_2, channel):
    # Initialize lists to store data for all sweeps for both devices
    real_parts_list_1 = []
    imag_parts_list_1 = []
    real_parts_list_2 = []
    imag_parts_list_2 = []
    
    for i in range(1, 4):  # Assuming 3 sweeps per channel for each device
        # Process device 1
        input_file_path_1 = f"/Users/christopherwarren/pyxdaq/rawdata/{base_filename_1}_{channel}_{i}.csv"
        df_1 = load_and_preprocess(input_file_path_1)
        Z_1 = df_1['Magnitude (Ohm)'] * np.exp(1j * np.deg2rad(df_1['Phase (Degrees)']))
        Z_np_1 = Z_1.to_numpy()
        real_parts_list_1.append(Z_np_1.real)
        imag_parts_list_1.append(Z_np_1.imag)
        
        # Process device 2
        input_file_path_2 = f"/Users/christopherwarren/pyxdaq/rawdata/{base_filename_2}_{channel}_{i}.csv"
        df_2 = load_and_preprocess(input_file_path_2)
        Z_2 = df_2['Magnitude (Ohm)'] * np.exp(1j * np.deg2rad(df_2['Phase (Degrees)']))
        Z_np_2 = Z_2.to_numpy()
        real_parts_list_2.append(Z_np_2.real)
        imag_parts_list_2.append(Z_np_2.imag)
        
    # Convert lists to numpy arrays
    real_parts_1 = np.array(real_parts_list_1)
    imag_parts_1 = np.array(imag_parts_list_1)
    real_parts_2 = np.array(real_parts_list_2)
    imag_parts_2 = np.array(imag_parts_list_2)
    
    # Calculate mean and SEM for both devices
    real_mean_1 = np.mean(real_parts_1, axis=0)
    real_sem_1 = sem(real_parts_1, axis=0)
    imag_mean_1 = np.mean(imag_parts_1, axis=0)
    imag_sem_1 = sem(imag_parts_1, axis=0)
    
    real_mean_2 = np.mean(real_parts_2, axis=0)
    real_sem_2 = sem(real_parts_2, axis=0)
    imag_mean_2 = np.mean(imag_parts_2, axis=0)
    imag_sem_2 = sem(imag_parts_2, axis=0)
    
    # Plotting
    plt.figure(figsize=(8, 8))
    
    # Plot device 1
    plt.errorbar(real_mean_1, -imag_mean_1, xerr=real_sem_1, yerr=imag_sem_1, fmt='o-', markersize=5, linewidth=1, label=f'{base_filename_1} Mean with SEM', color='tab:red')
    
    # Plot device 2
    plt.errorbar(real_mean_2, -imag_mean_2, xerr=real_sem_2, yerr=imag_sem_2, fmt='s-', markersize=5, linewidth=1, label=f'{base_filename_2} Mean with SEM', color='tab:blue')
    
    plt.xlabel('Re|G($\omega$)|')
    plt.ylabel('-Im|G($\omega$)|')
    plt.title(f'Nyquist Plot for Channel {channel} (Comparison)')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    output_file_path = f"/Users/christopherwarren/pyxdaq/figures/combined_nyquist_{channel}.png"
    plt.savefig(output_file_path, bbox_inches='tight')
    plt.close()

# Example usage
base_filename_1 = input("Enter your first base file name: ")
base_filename_2 = input("Enter your second base file name: ")

for channel in range(0, 16):  # Assuming you want to do this for each channel
    generate_combined_nyquist_plot(base_filename_1, base_filename_2, channel)
    print(f"Combined Nyquist plot for channel {channel} comparing {base_filename_1} and {base_filename_2} done.")
