#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 19:13:27 2024

@author: christopherwarren
"""

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

# Ask for filenames separated by commas
input_filenames = input("Enter your file names separated by commas: ")

# Split the input string into a list of filenames and add the path and extension
file_paths = [f"/Users/christopherwarren/pyxdaq/{filename.strip()}.csv" for filename in input_filenames.split(',')]

# Ask for output filename
output_filename = input("Enter your output file name: ")

#established file path where the data from this script will be saved
output_file_path = "/Users/christopherwarren/pyxdaq/" + output_filename + ".png"

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

# Plotting
fig, ax1 = plt.subplots(figsize=(15.36, 7.54)) # sets size


# # Magnitude plot with SEM bars
color = 'tab:red'
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Impedance (Ohm)', color=color)
ax1.errorbar(frequencies, mean_magnitudes, yerr=sem_magnitudes, fmt='o', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)
ax1.set_yscale('log')
ax1.set_xscale('log')

#Create a twin Axes for phase
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Phase (Degrees)', color=color)
ax2.errorbar(frequencies, mean_phases, yerr=sem_phases, fmt='o', color=color, ecolor='lightgray', elinewidth=6, capsize=0, markersize=3)

fig.tight_layout()
plt.title('Mean Impedance and Phase vs. Frequency with SEM')
plt.savefig(output_file_path, bbox_inches='tight')

print(f'Data saved to {output_filename}')

# plt.show()