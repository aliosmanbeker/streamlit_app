import pandas as pd
import numpy as np

# Load the dataset with the correct delimiter
file_path = 'F_XU0300624_trades.txt'
df = pd.read_csv(file_path)

# Convert the 'TARIH' column to datetime format
df['TARIH'] = pd.to_datetime(df['TARIH'], format='%d-%m-%Y %H:%M:%S')

# Sort the dataframe by 'TARIH' to ensure chronological order
df = df.sort_values(by='TARIH').reset_index(drop=True)

# Create an array to mark rows to keep
keep_rows = np.zeros(len(df), dtype=bool)

# Mark the rows with 1-minute intervals
previous_time = df.loc[0, 'TARIH']
keep_rows[0] = True
for i in range(1, len(df)):
    current_time = df.loc[i, 'TARIH']
    if (current_time - previous_time).seconds >= 60:
        previous_time = current_time
        keep_rows[i] = True

# Filter the dataframe
filtered_df = df[keep_rows]

# Save the filtered dataframe to a new CSV file
output_file_path_resampled = 'F_XU0300624_trades_1min.txt'
filtered_df.to_csv(output_file_path_resampled, index=False)

# Display a small sample of the filtered dataframe
filtered_df.head(10)
