import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences, savgol_filter
import pandas as pd
import os
from nptdms import TdmsFile
import mplcursors

#GLOBALS

file_dict = dict()


def neutral_deadband_test(df, file):
    derivative = savgol_filter(df['HST_output_RPM'], 1751, 3, 2)  # window size bvased on file not hardcoded
    peak_indices, _ = find_peaks(derivative)
    peak_proms = peak_prominences(derivative, peak_indices)[0]
    sorted_peak_indices = peak_indices[np.argsort(peak_proms)]
    top_40_percent = int(0.75 * len(sorted_peak_indices))  # hardcoded
    highest_peaks = sorted_peak_indices[-top_40_percent:]

    threshold_val = df['HST_output_RPM'].max() // 100  # define your threshold here
    df_new = pd.DataFrame()
    df_new['Time'] = df['Time'][highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new['Derivative'] = derivative[highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new['HST_output_RPM'] = df['HST_output_RPM'][highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new = df_new.sort_values('Time')

    df_4pt = pd.DataFrame()
    mid_time = df_new['Time'].max() / 2
    first_half = df_new[df_new['Time'] <= mid_time]
    second_half = df_new[df_new['Time'] > mid_time]
    min_max_first_half = first_half.loc[[first_half['Time'].idxmin(), first_half['Time'].idxmax()]]
    min_max_second_half = second_half.loc[[second_half['Time'].idxmin(), second_half['Time'].idxmax()]]
    df_4pt = pd.concat([df_4pt, min_max_first_half, min_max_second_half])

    ndb_df = pd.DataFrame(
        columns=["Input RPM", "HST_output_RPM", "A1", "A2", "B1", "B2", "Swash Angle Total Band", "A band", "B band",
                 "Zero of NDB lies at", "Delta @ A1", "Delta @ A2", "Delta @ B1", "Delta @ B2", "Time @ A1",
                 "Time @ A2", "Time @ B1", "Time @ B2"])

    # Extract input RPM from the filename
    input_rpm = os.path.splitext(os.path.basename(file))[0]

    # Compute HST output RPM
    hst_output_rpm = df_4pt['HST_output_RPM'].mean()

    # Merge dataframes on the index
    merged_df = df_4pt.merge(df[['Swash_Angle', 'Delta']], left_index=True, right_index=True)
    # Identify A points (1st and 4th row)
    A1_swash_angle = min(merged_df.iloc[0]['Swash_Angle'], merged_df.iloc[3]['Swash_Angle'])
    A2_swash_angle = max(merged_df.iloc[0]['Swash_Angle'], merged_df.iloc[3]['Swash_Angle'])

    # Identify B points (2nd and 3rd row)
    B1_swash_angle = max(merged_df.iloc[1]['Swash_Angle'], merged_df.iloc[2]['Swash_Angle'])
    B2_swash_angle = min(merged_df.iloc[1]['Swash_Angle'], merged_df.iloc[2]['Swash_Angle'])

    # Extract the Delta values for these points
    A1_delta = merged_df[merged_df['Swash_Angle'] == A1_swash_angle]['Delta'].values[0]
    A2_delta = merged_df[merged_df['Swash_Angle'] == A2_swash_angle]['Delta'].values[0]
    B1_delta = merged_df[merged_df['Swash_Angle'] == B1_swash_angle]['Delta'].values[0]
    B2_delta = merged_df[merged_df['Swash_Angle'] == B2_swash_angle]['Delta'].values[0]

    A1_time = merged_df[merged_df['Swash_Angle'] == A1_swash_angle]['Time'].values[0]
    A2_time = merged_df[merged_df['Swash_Angle'] == A2_swash_angle]['Time'].values[0]
    B1_time = merged_df[merged_df['Swash_Angle'] == B1_swash_angle]['Time'].values[0]
    B2_time = merged_df[merged_df['Swash_Angle'] == B2_swash_angle]['Time'].values[0]

    # Compute the required bands and zero of NDB
    swash_angle_tot_band = A1_swash_angle - B1_swash_angle
    a_band = abs(A1_swash_angle - A2_swash_angle)
    b_band = abs(B1_swash_angle - B2_swash_angle)
    zero_of_ndb = A1_swash_angle - (swash_angle_tot_band / 2)

    # Add the computed values to the DataFrame
    ndb_df.loc[0] = [
        input_rpm,
        hst_output_rpm,
        A1_swash_angle,
        A2_swash_angle,
        B1_swash_angle,
        B2_swash_angle,
        swash_angle_tot_band,
        a_band,
        b_band,
        zero_of_ndb,
        A1_delta,
        A2_delta,
        B1_delta,
        B2_delta,
        A1_time,
        A2_time,
        B1_time,
        B2_time
    ]

    return ndb_df


def plot_peaks(df, file):
    # smoothed = savgol_filter(,751, 3)
    derivative = savgol_filter(df['HST_output_RPM'], 1751, 3, 2)

    # Find the peaks in the derivative
    peak_indices, _ = find_peaks(derivative)

    # Calculate the prominences of the peaks
    peak_proms = peak_prominences(derivative, peak_indices)[0]

    # Sort the peaks by prominence and select the top 10%
    sorted_peak_indices = peak_indices[np.argsort(peak_proms)]
    top_10_percent = int(0.75 * len(sorted_peak_indices))
    highest_peaks = sorted_peak_indices[-top_10_percent:]

    threshold_val = df['HST_output_RPM'].max() // 100  # define your threshold here
    df_new = pd.DataFrame()
    df_new['Time'] = df['Time'][highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new['Derivative'] = derivative[highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new['HST_output_RPM'] = df['HST_output_RPM'][highest_peaks][df['HST_output_RPM'][highest_peaks] < threshold_val]
    df_new = df_new.sort_values('Time')

    df_4pt = pd.DataFrame()
    mid_time = df_new['Time'].max() / 2
    first_half = df_new[df_new['Time'] <= mid_time]
    second_half = df_new[df_new['Time'] > mid_time]
    min_max_first_half = first_half.loc[[first_half['Time'].idxmin(), first_half['Time'].idxmax()]]
    min_max_second_half = second_half.loc[[second_half['Time'].idxmin(), second_half['Time'].idxmax()]]
    df_4pt = pd.concat([df_4pt, min_max_first_half, min_max_second_half])
    merged_df = df_4pt.merge(df[['Swash_Angle', 'Delta']], left_index=True, right_index=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df['Time'], derivative, label='Derivative')
    plt.plot(df_4pt['Time'], df_4pt['Derivative'], 'ro', alpha=0.8, markersize=3)
    plt.title(f'Plot for file: {file}')
    plt.legend()
    mplcursors.cursor(hover=True)  # Enable interactive cursor
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(df['Time'], df['HST_output_RPM'], label='HST_output_RPM')
    plt.plot(df_4pt['Time'], df_4pt['HST_output_RPM'], 'ro', alpha=0.8, markersize=3)
    plt.legend()

    print("Num points: " + str(len(df_4pt)))
    print("Length df: " + str(len(df)))
    print(df_4pt)
    print("*" * 50)
    print(merged_df)
    mplcursors.cursor(hover=True)  # Enable interactive cursor
    plt.show()

def main():
    # Define the directory and initialize variables
    directory = r'C:\Deadband_testing\Neutral Deadband'
    count = 0
    all_results = []
    # Loop over all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tdms'):
                count += 1
                tdms_file = TdmsFile.read(os.path.join(root, file))
                df = tdms_file.as_dataframe()

                # Remove columns that only contain NaN values
                df = df.dropna(axis=1, how='all')
                df.columns = df.columns.str.replace("/", "")
                df.columns = df.columns.str.replace("'", "")
                df.columns = df.columns.str.replace("Data", "")

                # Plot peaks (assuming this function is defined elsewhere)
                #plot_peaks(df, os.path.join(root, file))

                # Compute the neutral deadband test
                temp_df = neutral_deadband_test(df, os.path.join(root, file))

                # Add a column for the filename
                temp_df['Filename'] = os.path.join(root, file)

                # Append the result to the list
                all_results.append(temp_df)

                file_dict[os.path.join(root, file)] = temp_df

    # Concatenate all results into a single DataFrame
    final_df = pd.concat(all_results, ignore_index=True)

    # Save the concatenated DataFrame to a CSV file
    output_csv = r'C:\Deadband_testing\Neutral_Deadband_Results.csv'
    final_df.to_csv(output_csv, index=False)

    print(f"Processed {count} files. Results saved to {output_csv}.")

if __name__=="__main__":
    main()