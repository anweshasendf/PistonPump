import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences, savgol_filter
import pandas as pd
import os
from nptdms import TdmsFile
import mplcursors
from scipy.interpolate import interp1d
import pandas as pd
from sklearn.linear_model import LinearRegression
import math
import re
from scipy.interpolate import griddata, LinearNDInterpolator

from scipy.interpolate import griddata
import json
import base64
import logging
from scipy.interpolate import RegularGridInterpolator

def remove_duplicate_files(directory):
    """
    Remove duplicate TDMS files in a directory. A duplicate file is identified by having a '_1' suffix in its filename.

    Args:
        directory (str): The path to the directory containing the files.
    """
    # Create a set to store the base filenames without the _1 suffix
    base_filenames = set()

    # Iterate over the files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tdms'):
                # Check if the file has the _1 suffix
                match = re.match(r'^(.*)_1\.tdms$', file)
                if match:
                    base_filename = match.group(1) + '.tdms'
                    # Check if the base file exists
                    if base_filename in files:
                        # Remove the duplicate file with the _1 suffix
                        os.remove(os.path.join(root, file))
                        print(f"Removed duplicate file: {file}")
                else:
                    # Add the base filename to the set
                    base_filenames.add(file)


def calculate_pump_displacement(outlet_flow, shaft_rpm):
    """
    Calculate the pump displacement.

    Args:
        outlet_flow (float): The outlet flow in GPM (gallons per minute).
        shaft_rpm (float): The shaft speed in RPM (revolutions per minute).

    Returns:
        float: The pump displacement.
    """
    return (outlet_flow * 231) * 16.387064 / (shaft_rpm)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_displacement_df(temp_percent_tdms_dir):
    """
    Generate a DataFrame with mean values for various parameters from TDMS files in a directory and its subdirectories.

    Args:
        temp_percent_tdms_dir (str): The path to the directory containing the TDMS files.

    Returns:
        tuple: A tuple containing the DataFrame with mean values and the maximum derived displacement.
    """
    all_df = pd.DataFrame(
        columns=["TDMS file", "Mean_Main_Flow_GPM", "Mean_RPM", "Mean_Outlet_Pressure_Psi", "Mean_Displacement",
                 "Mean_Inlet_Temp_F"])
    
    logging.info(f"Searching for TDMS files in: {temp_percent_tdms_dir}")
    tdms_files_found = 0
    
    for root, dirs, files in os.walk(temp_percent_tdms_dir):
        logging.debug(f"Searching in directory: {root}")
        logging.debug(f"Files found: {files}")
        
        for file in files:
            if file.endswith(".tdms"):
                tdms_files_found += 1
                try:
                    file_path = os.path.join(root, file)
                    logging.info(f"Processing TDMS file: {file_path}")
                    tdms_file = TdmsFile.read(file_path)
                    df = tdms_file.as_dataframe()

                    # Remove columns that only contain NaN values
                    df = df.dropna(axis=1, how='all')

                    # Clean up column names
                    df.columns = df.columns.str.replace("/", "")
                    df.columns = df.columns.str.replace("'", "")
                    df.columns = df.columns.str.replace("Data", "")
                    df.columns = df.columns.str.strip()
                    
                    logging.debug(f"Columns in TDMS file: {df.columns}")

                    if 'Main_Flow_GPM' not in df.columns or 'RPM' not in df.columns:
                        logging.warning(f"Required columns missing in file {file}")
                        continue

                    df['Displacement'] = calculate_pump_displacement(df['Main_Flow_GPM'], df['RPM'])
                    # Calculate mean values
                    mean_main_flow_gpm = df["Main_Flow_GPM"].mean() if "Main_Flow_GPM" in df.columns else None
                    mean_rpm = df["RPM"].mean() if "RPM" in df.columns else None
                    mean_outlet_pressure_psi = df[
                        "Outlet_Pressure_Psi"].mean() if "Outlet_Pressure_Psi" in df.columns else None
                    mean_displacement = df['Displacement'].mean()
                    mean_inlet_temp = df['Inlet_Temp_F'].mean() if 'Inlet_Temp_F' in df.columns else None
                    # Append the results to all_df
                    all_df = all_df._append({
                        "TDMS file": file,
                        "Mean_Main_Flow_GPM": mean_main_flow_gpm,
                        "Mean_RPM": mean_rpm,
                        "Mean_Outlet_Pressure_Psi": mean_outlet_pressure_psi,
                        "Mean_Displacement": mean_displacement,
                        "Mean_Inlet_Temp_F": mean_inlet_temp,
                    }, ignore_index=True)

                except Exception as e:
                    logging.error(f"Error processing file {file}: {e}")

    if all_df.empty:
        if tdms_files_found == 0:
            logging.warning("No TDMS files found in the specified directory")
        else:
            logging.warning(f"Found {tdms_files_found} TDMS files, but no valid data could be processed")
        return all_df, np.nan

    max_derived_displacement = all_df['Mean_Displacement'].max()
    logging.info(f"Max derived displacement: {max_derived_displacement}")
    
    return all_df, max_derived_displacement
    # After calculating max_derived_displacement
# Add it to the Excel file
    
def process_tdms_to_csv(max_derived_displacement, tdms_file_path):
    """
    Process TDMS files in a directory and its subdirectories and save the processed data to CSV files.

    Args:
        max_derived_displacement (float): The maximum derived displacement.
        tdms_file_path (str): The path to the directory containing the TDMS files.
    """
    all_data = []
    for root, _, files in os.walk(tdms_file_path):
        for file in files:
            if file.endswith('.tdms'):
                try:
                    file_path = os.path.join(root, file)
                    logging.info(f"Processing TDMS file: {file_path}")
                    tdms_file = TdmsFile.read(file_path)
                    df = tdms_file.as_dataframe()
                    
                    df = df[~df.index.duplicated(keep='first')]

                    # Drop columns with all NaN values
                    df = df.dropna(axis=1, how='all')

                    # Clean up column names
                    df.columns = df.columns.str.replace("/", "")
                    df.columns = df.columns.str.replace("'", "")
                    df.columns = df.columns.str.replace("Data", "")
                    df.columns = df.columns.str.strip()

                    logging.debug(f"Columns in TDMS file: {df.columns}")

                    if 'Main_Flow_GPM' not in df.columns or 'RPM' not in df.columns:
                        logging.warning(f"Required columns missing in file {file}")
                        continue

                    # Calculate displacement
                    df['Displacement'] = calculate_pump_displacement(df['Main_Flow_GPM'], df['RPM'])

                    # Calculate the new columns
                    df['Calc_VE'] = df['Displacement'] * 100 / max_derived_displacement
                    df['Calc_ME'] = 100 * (
                                (((max_derived_displacement / 16.387064) * df['Outlet_Pressure_Psi']) / (2 * math.pi)) /
                                df['Pump_Torque_In.lbf'])
                    df['Calc_OE'] = df['Calc_VE'] * df['Calc_ME'] / 100

                    all_data.append(df)
                    logging.debug(f"Processed file: {file}")
                    logging.debug(f"Columns: {df.columns}")

                except Exception as e:
                    logging.error(f"Error processing file {file}: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.drop_duplicates().reset_index(drop=True)
        output_file = os.path.join(tdms_file_path, "results", "processed_combined_data.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Combined data saved to: {output_file}")
        logging.debug(f"Combined data columns: {combined_df.columns}")
    else:
        logging.warning("No data processed in process_tdms_to_csv")

def get_stats_df(output_path, max_derived_displacement):
    statistics_df = pd.DataFrame(columns=("TDMS file", "Speed", "Outlet Pressure", "Derived Displacement"))

    csv_files = [f for f in os.listdir(output_path) if f.endswith('.csv') and f.startswith('processed_')]
    logging.info(f"Found {len(csv_files)} CSV files in the output directory")

    for file in csv_files:
        file_path = os.path.join(output_path, file)
        try:
            df = pd.read_csv(file_path)
            logging.info(f"Processing file: {file}")
            logging.info(f"Columns in the CSV: {df.columns.tolist()}")

            # Extract speed and pressure from the filename
            temp_arr = file.split("_")
            speed = 0
            pressure = 0
            for item in temp_arr:
                if "rpm" in item.lower():
                    digits = ''.join(re.findall(r'\d', item))
                    speed = int(digits) if digits else 0
                elif "psi" in item.lower():
                    digits = ''.join(re.findall(r'\d', item))
                    pressure = int(digits) if digits else 0

            # Ensure speed and pressure are positive
            speed = abs(speed)
            pressure = abs(pressure)

            # If speed or pressure is still 0, try to get it from the data
            if speed == 0 and 'RPM' in df.columns:
                speed = abs(int(df['RPM'].mean()))
            if pressure == 0 and 'Outlet_Pressure_Psi' in df.columns:
                pressure = abs(int(df['Outlet_Pressure_Psi'].mean()))

            logging.info(f"Extracted Speed: {speed}, Pressure: {pressure}")

            # Calculate statistics for each column
            stats = {}
            for col in df.columns:
                if col not in ['Time_ms', '%VE', '%OVE', '%ME']:
                    stats[f'{col}_mean'] = df[col].mean()
                    stats[f'{col}_stddev'] = df[col].std()

            # Create a row with the statistics
            row = {
                "TDMS file": file,
                "Speed": speed,
                "Outlet Pressure": pressure,
                "Derived Displacement": max_derived_displacement,
                **stats
            }

            # Append the row to the statistics DataFrame
            statistics_df = statistics_df._append(row, ignore_index=True)

        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")

    # Clean up the 'TDMS file' column
    statistics_df['TDMS file'] = statistics_df['TDMS file'].str.replace('processed_', '', regex=False)
    statistics_df['TDMS file'] = statistics_df['TDMS file'].str.replace('.csv', '.tdms', regex=False)

    # Remove any duplicate rows based on Speed and Outlet Pressure
    statistics_df = statistics_df.drop_duplicates(subset=['Speed', 'Outlet Pressure'])

    logging.info(f"Final statistics DataFrame shape: {statistics_df.shape}")
    logging.info(f"Columns in statistics DataFrame: {statistics_df.columns.tolist()}")
    logging.info(f"Unique Speed values: {statistics_df['Speed'].unique().tolist()}")
    logging.info(f"Unique Outlet Pressure values: {statistics_df['Outlet Pressure'].unique().tolist()}")
    logging.info(f"Sample of statistics DataFrame:\n{statistics_df.head().to_string()}")

    return statistics_df

def get_pivot_tables(statistics_df):
    """
    Create pivot tables for VE, ME, and OE from the statistics DataFrame.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        tuple: A tuple containing the VE, ME, and OE pivot tables (DataFrames).
    """
    try:
        ve_pivot = statistics_df.pivot_table(
            values='Calc_VE_mean',
            index='Outlet Pressure',
            columns='Speed',
            aggfunc='mean'
        )
    except Exception as e:
        logging.warning(f"Unable to create VE pivot table: {e}")
        ve_pivot = None

    try:
        me_pivot = statistics_df.pivot_table(
            values='Calc_ME_mean',
            index='Outlet Pressure',
            columns='Speed',
            aggfunc='mean'
        )
    except Exception as e:
        logging.warning(f"Unable to create ME pivot table: {e}")
        me_pivot = None

    try:
        oe_pivot = statistics_df.pivot_table(
            values='Calc_OE_mean',
            index='Outlet Pressure',
            columns='Speed',
            aggfunc='mean'
        )
    except Exception as e:
        logging.warning(f"Unable to create OE pivot table: {e}")
        oe_pivot = None

    return ve_pivot, me_pivot, oe_pivot

def create_performace_excel(filename, all_df, statistics_df, ve_pivot, me_pivot, oe_pivot):
    """
    Save the given DataFrames and pivot tables to an Excel file.

    Args:
        filename (str): The name of the output Excel file.
        all_df (DataFrame): The DataFrame containing all data.
        statistics_df (DataFrame): The DataFrame containing statistics.
        ve_pivot (DataFrame): The pivot table for VE.
        me_pivot (DataFrame): The pivot table for ME.
        oe_pivot (DataFrame): The pivot table for OE.
    """
    output_file = filename

    # Write to Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        all_df.to_excel(writer, sheet_name='All Data', index=False)
        statistics_df.to_excel(writer, sheet_name='Statistics Data', index=False)

        # Write pivot tables to a single sheet
        startrow = 0
        ve_pivot.to_excel(writer, sheet_name='Pivot Tables', startrow=startrow)
        startrow += ve_pivot.shape[0] + 2
        me_pivot.to_excel(writer, sheet_name='Pivot Tables', startrow=startrow)
        startrow += me_pivot.shape[0] + 2
        oe_pivot.to_excel(writer, sheet_name='Pivot Tables', startrow=startrow)

    print(f"DataFrames have been successfully saved to '{output_file}'.")

def interp_df(ve_pivot, me_pivot, oe_pivot):
    """
    Interpolates data from given pivot tables.

    Args:
        ve_pivot (DataFrame): VE pivot table.
        me_pivot (DataFrame): ME pivot table.
        oe_pivot (DataFrame): OE pivot table.

    Returns:
        tuple: Interpolated DataFrames for VE, ME, and OE.
    """
    original_speeds = ve_pivot.columns.astype(float).tolist()
    original_pressures = ve_pivot.index.astype(float).tolist()

    # Define the new speed and pressure ranges based on actual data
    min_speed, max_speed = min(original_speeds), max(original_speeds)
    min_pressure, max_pressure = min(original_pressures), max(original_pressures)

    new_speeds = np.linspace(min_speed, max_speed, 100)
    new_pressures = np.linspace(min_pressure, max_pressure, 100)

    # Create meshgrid for new speeds and pressures
    new_speeds_mesh, new_pressures_mesh = np.meshgrid(new_speeds, new_pressures)
    new_points = np.array([new_pressures_mesh.ravel(), new_speeds_mesh.ravel()]).T

    # Interpolation for ve_pivot
    ve_interp_func = RegularGridInterpolator((original_pressures, original_speeds), ve_pivot.values, bounds_error=False, fill_value=None)
    ve_interpolated = ve_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    ve_interpolated_df = pd.DataFrame(ve_interpolated, index=new_pressures, columns=new_speeds)

    # Interpolation for me_pivot
    me_interp_func = RegularGridInterpolator((original_pressures, original_speeds), me_pivot.values, bounds_error=False, fill_value=None)
    me_interpolated = me_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    me_interpolated_df = pd.DataFrame(me_interpolated, index=new_pressures, columns=new_speeds)

    # Interpolation for oe_pivot
    oe_interp_func = RegularGridInterpolator((original_pressures, original_speeds), oe_pivot.values, bounds_error=False, fill_value=None)
    oe_interpolated = oe_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    oe_interpolated_df = pd.DataFrame(oe_interpolated, index=new_pressures, columns=new_speeds)

    return ve_interpolated_df, me_interpolated_df, oe_interpolated_df

def create_performace_excel(output_file, all_df, statistics_df, ve_pivot, me_pivot, oe_pivot):
    """
    Create an Excel file with all data, statistics, and pivot tables.

    Args:
        output_file (str): The path to save the Excel file.
        all_df (DataFrame): DataFrame containing all processed data.
        statistics_df (DataFrame): DataFrame containing calculated statistics.
        ve_pivot (DataFrame): Pivot table for Volumetric Efficiency.
        me_pivot (DataFrame): Pivot table for Mechanical Efficiency.
        oe_pivot (DataFrame): Pivot table for Overall Efficiency.
    """
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            all_df.to_excel(writer, sheet_name='All Data', index=False)
            statistics_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            if ve_pivot is not None and not ve_pivot.empty:
                ve_pivot.to_excel(writer, sheet_name='VE Pivot')
            else:
                logging.warning("VE Pivot table is empty or None. Skipping VE Pivot sheet.")
            
            if me_pivot is not None and not me_pivot.empty:
                me_pivot.to_excel(writer, sheet_name='ME Pivot')
            else:
                logging.warning("ME Pivot table is empty or None. Skipping ME Pivot sheet.")
            
            if oe_pivot is not None and not oe_pivot.empty:
                oe_pivot.to_excel(writer, sheet_name='OE Pivot')
            else:
                logging.warning("OE Pivot table is empty or None. Skipping OE Pivot sheet.")
        
        logging.info(f"Excel file successfully created: {output_file}")
    except Exception as e:
        logging.error(f"Error creating Excel file: {e}")
        raise


def create_contour_plot(statistics_df, value_column, title, z_label):
    X = statistics_df['Speed']
    Y = statistics_df['Outlet Pressure']
    Z = statistics_df[value_column]

    logging.info(f"Creating {title}")
    logging.info(f"Number of data points: {len(X)}")
    logging.info(f"Speed values: {X.tolist()}")
    logging.info(f"Pressure values: {Y.tolist()}")
    logging.info(f"{value_column} values: {Z.tolist()}")

    fig, ax = plt.subplots(figsize=(10, 6))

    if len(X) < 4:
        logging.warning(f"Not enough data points for {title}. Creating scatter plot instead.")
        scatter = ax.scatter(X, Y, c=Z, cmap='viridis', s=100)
        plt.colorbar(scatter, label=z_label)
    else:
        # Create a grid for interpolation
        xi = np.linspace(X.min(), X.max(), 100)
        yi = np.linspace(Y.min(), Y.max(), 100)
        Xi, Yi = np.meshgrid(xi, yi)

        # Use griddata for interpolation
        Zi = griddata((X, Y), Z, (Xi, Yi), method='cubic')

        # Create the contour plot
        contour = ax.contourf(Xi, Yi, Zi, levels=20, cmap='viridis', extend='both')
        ax.scatter(X, Y, c=Z, cmap='viridis', edgecolors='black', linewidth=0.5)
        plt.colorbar(contour, label=z_label)

    ax.set_xlabel('Speed (RPM)')
    ax.set_ylabel('Outlet Pressure (psi)')
    ax.set_title(title)

    return fig

def ve_contour(statistics_df):
    return create_contour_plot(statistics_df, 'Calc_VE_mean', 'Volumetric Efficiency Contour Plot', 'VE (%)')

def me_contour(statistics_df):
    return create_contour_plot(statistics_df, 'Calc_ME_mean', 'Mechanical Efficiency Contour Plot', 'ME (%)')

def oe_contour(statistics_df):
    return create_contour_plot(statistics_df, 'Calc_OE_mean', 'Overall Efficiency Contour Plot', 'OE (%)')

def efficiency_map(statistics_df):
    """
    Create a line plot for Overall Efficiency (OE) based on outlet pressure and speed.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the line plot.
    """
    X = statistics_df['Outlet Pressure']
    Y = statistics_df['Calc_OE_mean']
    Z = statistics_df['Speed']

    # Create the line plot
    fig, ax = plt.subplots(figsize=(10, 6), dpi=250)
    ax.grid()

    # Use a colormap to determine the color of each segment
    norm = plt.Normalize(Z.min(), Z.max())
    cmap = plt.get_cmap('viridis')

    # Group data by Speed
    grouped = statistics_df.groupby('Speed')

    # Plot each group separately
    for speed, group in grouped:
        sorted_group = group.sort_values(by='Outlet Pressure')
        ax.plot(sorted_group['Outlet Pressure'], sorted_group['Calc_OE_mean'],
                label=f'RPM {speed}', color=cmap(norm(speed)), linewidth=2, marker='x')

    # Set y-axis limits
    ax.set_ylim(0, 100)

    # Add labels and title
    ax.set_xlabel('OE (Overall Efficiency)')
    ax.set_ylabel('Outlet Pressure')
    ax.set_title('Line Graph of OE, Outlet Pressure, and RPM')

    # Add legend
    ax.legend()

    # Return the figure object
    return fig


def create_flow_line_plot(statistics_df):
    """
    Create a line plot for Main Flow (GPM) based on outlet pressure and speed.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the line plot.
    """
    X = statistics_df['Outlet Pressure']
    Y = statistics_df['Main_Flow_GPM_mean']
    Z = statistics_df['Speed']

    # Create the line plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Use a colormap to determine the color of each segment
    norm = plt.Normalize(Z.min(), Z.max())
    cmap = plt.get_cmap('viridis')

    # Group data by Speed
    grouped = statistics_df.groupby('Speed')

    # Plot each group separately
    for speed, group in grouped:
        sorted_group = group.sort_values(by='Outlet Pressure')
        ax.plot(sorted_group['Outlet Pressure'], sorted_group['Main_Flow_GPM_mean'],
                label=f'RPM {speed}', color=cmap(norm(speed)), linewidth=2, marker='x')

        # Annotate max, min, and middle points
        max_index = sorted_group['Main_Flow_GPM_mean'].idxmax()
        min_index = sorted_group['Main_Flow_GPM_mean'].idxmin()

        # Find the middle point based on the middle x-value (Outlet Pressure)
        median_pressure = sorted_group['Outlet Pressure'].median()
        mid_index = (sorted_group['Outlet Pressure'] - median_pressure).abs().idxmin()

        max_flow = sorted_group['Main_Flow_GPM_mean'][max_index]
        min_flow = sorted_group['Main_Flow_GPM_mean'][min_index]
        mid_flow = sorted_group['Main_Flow_GPM_mean'][mid_index]

        ax.annotate(f'{max_flow:.2f}', (sorted_group['Outlet Pressure'][max_index], max_flow),
                    textcoords="offset points", xytext=(0, 10), ha='center', color=cmap(norm(speed)))
        ax.annotate(f'{min_flow:.2f}', (sorted_group['Outlet Pressure'][min_index], min_flow),
                    textcoords="offset points", xytext=(0, 10), ha='center', color=cmap(norm(speed)))
        ax.annotate(f'{mid_flow:.2f}', (sorted_group['Outlet Pressure'][mid_index], mid_flow),
                    textcoords="offset points", xytext=(0, 10), ha='center', color=cmap(norm(speed)))

    # Add labels and title
    ax.set_xlabel('Outlet Pressure')
    ax.set_ylabel('Main Flow (GPM)')
    ax.set_title('Line Graph of Main Flow, Outlet Pressure, and RPM')

    # Add legend
    ax.legend()

    # Return the figure object
    return fig

def main(tdms_folder_path, output_path):
    try:
        logging.info(f"TDMS folder path: {tdms_folder_path}")
        logging.info(f"Output path: {output_path}")
        
        logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

        
        # Get displacement DataFrame and maximum derived displacement
        all_df, max_derived_displacement = get_displacement_df(tdms_folder_path)
        
        if all_df.empty or np.isnan(max_derived_displacement):
            raise ValueError("No valid data found in TDMS files. Check the log for more details.")

        # Process TDMS files and save to CSV
        process_tdms_to_csv(max_derived_displacement, tdms_folder_path)

        # Get statistics DataFrame
        statistics_df = get_stats_df(output_path, max_derived_displacement)
        
        if statistics_df.empty:
            raise ValueError("No statistics data generated. Check the log for more details.")

        logging.debug(f"Statistics DataFrame shape: {statistics_df.shape}")
        logging.debug(f"Statistics DataFrame columns: {statistics_df.columns}")
        
        # Create pivot tables
        ve_pivot, me_pivot, oe_pivot = get_pivot_tables(statistics_df)

        logging.debug(f"VE pivot shape: {ve_pivot.shape if ve_pivot is not None else 'None'}")
        logging.debug(f"ME pivot shape: {me_pivot.shape if me_pivot is not None else 'None'}")
        logging.debug(f"OE pivot shape: {oe_pivot.shape if oe_pivot is not None else 'None'}")

        # Check if pivot tables are valid before interpolation
        if ve_pivot is not None and not ve_pivot.empty and me_pivot is not None and not me_pivot.empty and oe_pivot is not None and not oe_pivot.empty:
            logging.info("Performing interpolation on pivot tables")
            ve_interpolated_df, me_interpolated_df, oe_interpolated_df = interp_df(ve_pivot, me_pivot, oe_pivot)
            logging.debug(f"Interpolated VE shape: {ve_interpolated_df.shape}")
            logging.debug(f"Interpolated ME shape: {me_interpolated_df.shape}")
            logging.debug(f"Interpolated OE shape: {oe_interpolated_df.shape}")
        else:
            logging.warning("One or more pivot tables are empty or None. Skipping interpolation.")
            ve_interpolated_df, me_interpolated_df, oe_interpolated_df = None, None, None
        # Generate plots
        ve_contour_plot = ve_contour(statistics_df)
        me_contour_plot = me_contour(statistics_df)
        oe_contour_plot = oe_contour(statistics_df)

        # Save plots in the results subdirectory
        os.makedirs(os.path.join(output_path, 'results'), exist_ok=True)
        
        ve_contour_plot.savefig(os.path.join(output_path, 've_contour_plot.png'))
        logging.info("VE plot saved")
        
        me_contour_plot.savefig(os.path.join(output_path,  'me_contour_plot.png'))
        logging.info("ME plot saved")
        
        oe_contour_plot.savefig(os.path.join(output_path,  'oe_contour_plot.png'))
        logging.info("OE plot saved")

        # Save the Excel file with all data and statistics
        excel_filename = os.path.join(output_path, 'performance.xlsx')
        create_performace_excel(excel_filename, all_df, statistics_df, ve_pivot, me_pivot, oe_pivot)
        with pd.ExcelWriter(excel_filename, engine='openpyxl', mode='a') as writer:
            pd.DataFrame({'max_derived_displacement': [max_derived_displacement]}).to_excel(writer, sheet_name='Parameters', index=False)
        print(json.dumps({"success": "Data processing completed successfully"}))
    except Exception as e:
        logging.exception("An error occurred during script execution")
        error_message = json.dumps({"error": str(e)})
        print(error_message, file=sys.stderr)
        sys.exit(1)

def encode_plot(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python piston_group.py <tdms_folder_path> <output_path>")
        sys.exit(1)
    
    tdms_folder_path = sys.argv[1]
    output_path = sys.argv[2]
    main(tdms_folder_path, output_path)
