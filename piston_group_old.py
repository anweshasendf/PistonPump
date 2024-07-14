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
from scipy.interpolate import griddata
import json
import base64
import logging

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

def get_stats_df(temp_percent_tdms_dir, max_derived_displacement):
    """
    Calculate statistics for each processed CSV file.

    Args:
        temp_percent_tdms_dir (str): The path to the directory containing the processed CSV files.
        max_derived_displacement (float): The maximum derived displacement.

    Returns:
        DataFrame: A DataFrame containing statistics for each file.
    """
    statistics_list = []

    csv_file = os.path.join(temp_percent_tdms_dir, "processed_combined_data.csv")
    if not os.path.exists(csv_file):
        logging.error(f"Combined CSV file not found: {csv_file}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_file)
        logging.debug(f"Read CSV file: {csv_file}")
        logging.debug(f"Columns in CSV: {df.columns}")

        # Calculate statistics for each column
        stats = {}
        for col in df.columns:
            if col not in ['Time_ms', '%VE', '%OVE', '%ME']:
                stats[f'{col}_mean'] = df[col].mean()
                stats[f'{col}_stddev'] = df[col].std()

        # Create a row with the statistics
        row = {
            "TDMS file": "combined_data",
            "Speed": df['RPM'].mean(),
            "Outlet Pressure": df['Outlet_Pressure_Psi'].mean(),
            "Derived Displacement": max_derived_displacement,
            **stats
        }

        # Append the row to the statistics list
        statistics_list.append(row)

    except Exception as e:
        logging.error(f"Error processing combined CSV file: {e}")

    # Create the statistics DataFrame from the list of dictionaries
    statistics_df = pd.DataFrame(statistics_list)
    logging.debug(f"Statistics DataFrame columns: {statistics_df.columns}")
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


def ve_contour(statistics_df):
    """
    Create a contour plot for Volumetric Efficiency (VE) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot, or None if not enough data.
    """
    if len(statistics_df) < 4:
        logging.warning(f"Not enough data points for VE contour plot. Found {len(statistics_df)} points, need at least 4.")
        return None

    X = statistics_df['Speed']
    Y = statistics_df['Outlet Pressure']
    Z = statistics_df['Calc_VE_mean']

    logging.debug(f"VE contour data points: {len(X)}")
    logging.debug(f"Speed range: {Y.min()} to {Y.max()}")
    logging.debug(f"Outlet Pressure range: {X.min()} to {X.max()}")
    logging.debug(f"VE range: {Z.min()} to {Z.max()}")

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), 3500, 100),  # Limiting RPM to 3500
        np.linspace(Y.min(), Y.max(), 100)
    )

    # Interpolate Z values on the grid
    Z_grid = griddata((X, Y), Z, (X_grid, Y_grid), method='linear')

    # Create the contour plot
    fig, ax = plt.subplots(figsize=(10, 6))
    contour_filled = ax.contourf(X_grid, Y_grid, Z_grid, levels=20, cmap='plasma')
    contour_lines = ax.contour(X_grid, Y_grid, Z_grid, levels=20, colors='black', linewidths=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt="%.1f")

    # Add color bar
    cbar = plt.colorbar(contour_filled, ax=ax, label='VE (Volumetric Efficiency)')

    # Add labels and title
    ax.set_xlabel('RPM (Speed)')
    ax.set_ylabel('Outlet Pressure')
    ax.set_ylim(0, 3500)
    ax.set_title('Contour Plot of VE, Outlet Pressure, and RPM')

    # Return the figure object
    return fig

def me_contour(statistics_df):
    """
    Create a contour plot for Mechanical Efficiency (ME) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot, or None if not enough data.
    """
    if len(statistics_df) < 4:
        logging.warning(f"Not enough data points for ME contour plot. Found {len(statistics_df)} points, need at least 4.")
        return None

    X = statistics_df['Speed']
    Y = statistics_df['Outlet Pressure']
    Z = statistics_df['Calc_ME_mean']

    logging.debug(f"ME contour data points: {len(X)}")
    logging.debug(f"Speed range: {Y.min()} to {Y.max()}")
    logging.debug(f"Outlet Pressure range: {X.min()} to {X.max()}")
    logging.debug(f"ME range: {Z.min()} to {Z.max()}")

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), 3500, 100),  # Limiting RPM to 3500
        np.linspace(Y.min(), Y.max(), 100)
    )

    # Interpolate Z values on the grid
    Z_grid = griddata((X, Y), Z, (X_grid, Y_grid), method='linear')

    # Create the contour plot
    fig, ax = plt.subplots(figsize=(10, 6))
    contour_filled = ax.contourf(X_grid, Y_grid, Z_grid, levels=20, cmap='plasma')
    contour_lines = ax.contour(X_grid, Y_grid, Z_grid, levels=20, colors='black', linewidths=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt="%.1f")

    # Add color bar
    cbar = plt.colorbar(contour_filled, ax=ax, label='ME (Mechanical Efficiency)')

    # Add labels and title
    ax.set_xlabel('Outlet Pressure')
    ax.set_ylabel('RPM (Speed)')
    ax.set_ylim(0, 3500)
    ax.set_title('Contour Plot of ME, Outlet Pressure, and RPM')

    # Return the figure object
    return fig

def oe_contour(statistics_df):
    """
    Create a contour plot for Overall Efficiency (OE) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot, or None if not enough data.
    """
    if len(statistics_df) < 4:
        logging.warning(f"Not enough data points for OE contour plot. Found {len(statistics_df)} points, need at least 4.")
        return None

    X = statistics_df['Speed']
    Y = statistics_df['Outlet Pressure']
    Z = statistics_df['Calc_OE_mean']

    logging.debug(f"OE contour data points: {len(X)}")
    logging.debug(f"Speed range: {Y.min()} to {Y.max()}")
    logging.debug(f"Outlet Pressure range: {X.min()} to {X.max()}")
    logging.debug(f"OE range: {Z.min()} to {Z.max()}")

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), 3500, 100),  # Limiting RPM to 3500
        np.linspace(Y.min(), Y.max(), 100)
    )

    # Interpolate Z values on the grid
    Z_grid = griddata((X, Y), Z, (X_grid, Y_grid), method='linear')

    # Create the contour plot
    fig, ax = plt.subplots(figsize=(10, 6))
    contour_filled = ax.contourf(X_grid, Y_grid, Z_grid, levels=20, cmap='plasma')
    contour_lines = ax.contour(X_grid, Y_grid, Z_grid, levels=20, colors='black', linewidths=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt="%.1f")

    # Add color bar
    cbar = plt.colorbar(contour_filled, ax=ax, label='OE (Overall Efficiency)')

    # Add labels and title
    ax.set_xlabel('RPM (Speed)')
    ax.set_ylim(0, 3500)
    ax.set_ylabel('Outlet Pressure')
    ax.set_title('Contour Plot of OE, Outlet Pressure, and RPM')

    # Return the figure object
    return fig

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

        # Generate plots
        ve_contour_plot = ve_contour(statistics_df)
        me_contour_plot = me_contour(statistics_df)
        oe_contour_plot = oe_contour(statistics_df)

        # Save plots in the results subdirectory
        if ve_contour_plot:
            ve_contour_plot.savefig(os.path.join(output_path, 've_contour_plot.png'))
        if me_contour_plot:
            me_contour_plot.savefig(os.path.join(output_path, 'me_contour_plot.png'))
        if oe_contour_plot:
            oe_contour_plot.savefig(os.path.join(output_path, 'oe_contour_plot.png'))

        # Save the Excel file with all data and statistics
        excel_filename = os.path.join(output_path, 'performance.xlsx')
        create_performace_excel(excel_filename, all_df, statistics_df, ve_pivot, me_pivot, oe_pivot)

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
