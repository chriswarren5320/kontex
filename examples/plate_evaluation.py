import pandas as pd
import matplotlib.pyplot as plt
import os

# Ask for the base file name
base_file_name = input("Enter the folder where the data is stored (i.e., 01may24_1): ")

# loads plating data
csv_file_path = f"/Users/christopherwarren/pyxdaq/data/{base_file_name}/rawdata/{base_file_name}_platingdata.csv"



# Read the CSV file
data = pd.read_csv(csv_file_path)

x_labels = ["None", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]

# x_labels = ["None", "1", "3", "5", "7", "9", "11", "13", "15"]


# Clean the data: strip the ' Ohm' text and convert to numeric values
for col in data.columns[1:]:  # Exclude the first column for the labels
    data[col] = data[col].str.replace(' Ohm', '').astype(float)

# Define marker styles for channels before 10 and for 10 and onwards
markers_before_10 = 'o'  # Marker for channels before 10
markers_after_10 = 's'  # Marker for channels 10 and onwards (s for square)

# Create a directory to save the plots
save_dir = f"/Users/christopherwarren/pyxdaq/data/{base_file_name}/figures/plating_plots"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Plot and save a separate graph for each channel
for i in range(16):
    fig, ax = plt.subplots(figsize=(10, 6))
    marker_style = markers_before_10 if i < 10 else markers_after_10

    ax.plot(x_labels, data.iloc[:, i+1], marker=marker_style, label=f'Channel {i}')
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=90)
    ax.set_yscale('log')
    ax.set_ylim([10**2, 10**7])
    ax.set_xlabel('Stimulated Channel')
    ax.set_ylabel('Impedance (Ohm)')
    ax.set_title(f'Impedance for Channel {i}')
    ax.legend()
    
    # Save the figure
    fig.savefig(os.path.join(save_dir, f"{base_file_name}_{i}.png"))
    plt.close(fig)  # Close the figure to free up memory
