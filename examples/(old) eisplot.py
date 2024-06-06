#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:03:21 2024

@author: christopherwarren
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load the CSV data

file_path = "/Users/christopherwarren/pyxdaq/" + input("Enter your desired file name: ") + ".csv"
df = pd.read_csv(file_path)


# Convert columns to numeric, ensuring no strings are present
df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
df['Magnitude (Ohm)'] = pd.to_numeric(df['Magnitude (Ohm)'], errors='coerce')
df['Phase (Degrees)'] = pd.to_numeric(df['Phase (Degrees)'], errors='coerce')

# Drop rows with NaN values that may result from conversion errors
df = df.dropna()

# Extract data
frequencies = df['Frequency (Hz)'].values
magnitudes = df['Magnitude (Ohm)'].values
phases = df['Phase (Degrees)'].values


# Fit lines (1st-degree polynomial = linear)
magnitude_coeffs = np.polyfit(np.log10(frequencies), np.log10(magnitudes), 2)
phase_coeffs = np.polyfit(np.log10(frequencies), phases, 2)

# Create polynomial functions from the coefficients
magnitude_poly = np.poly1d(magnitude_coeffs)
phase_poly = np.poly1d(phase_coeffs)

# Generate x-values for the fit lines
fit_frequencies = np.linspace(min(frequencies), max(frequencies), 1000)
fit_magnitude = 10**(magnitude_poly(np.log10(fit_frequencies)))  # For magnitude, use log-log fit
fit_phase = phase_poly(np.log10(fit_frequencies))  # For phase, assuming linear fit is sufficient

# Plotting
fig, ax1 = plt.subplots()

# Scatter plot for magnitude and its line of best fit
color = 'tab:red'
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Impedance (Ohm)', color=color)
ln1 = ax1.scatter(frequencies, magnitudes, color=color, label='', s=1)
#ln2 = ax1.plot(fit_frequencies, fit_magnitude, color=color, linestyle='--', label='Magnitude Fit')
ax1.set_yscale('log')
ax1.set_xscale('log')


# Create a twin Axes sharing the xaxis for phase scatter plot and its line of best fit
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Phase (Degrees)', color=color)
ln3 = ax2.scatter(frequencies, phases, color=color, label='Phase', s=1)
#ln4 = ax2.plot(fit_frequencies, fit_phase, color=color, linestyle='--', label='Phase Fit')
ax2.tick_params(axis='y', labelcolor=color)

# Correctly combine legends
#lns = [ln1] + ln2 + [ln3] + ln4  # Note: wrap ln1 and ln3 in lists to concatenate them with ln2 and ln4
lns = [ln1] + [ln3]  # Note: wrap ln1 and ln3 in lists to concatenate them with ln2 and ln4

labs = [l.get_label() for l in lns]
#ax1.legend(lns, labs, loc='best')

fig.tight_layout()  # To ensure the layout does not overlap
plt.title('Impedance and Phase vs. Frequency with Lines of Best Fit')
plt.show()