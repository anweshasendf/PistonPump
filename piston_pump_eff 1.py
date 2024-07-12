import numpy as np
import matplotlib.pyplot as plt
import os
from nptdms import TdmsFile
import pandas as pd
import math
import re
from scipy.interpolate import griddata
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

def get_displacement_df(temp_percent_tdms_dir):
    """
    Generate a DataFrame with mean values for various parameters from TDMS files in a directory.

    Args:
        temp_percent_tdms_dir (str): The path to the directory containing the TDMS files.

    Returns:
        tuple: A tuple containing the DataFrame with mean values and the maximum derived displacement.
    """
    all_df = pd.DataFrame(
        columns=["TDMS file", "Mean_Main_Flow_GPM", "Mean_RPM", "Mean_Outlet_Pressure_Psi", "Mean_Displacement",
                 "Mean_Inlet_Temp_F"])
    for root, dirs, files in os.walk(temp_percent_tdms_dir):
        for file in files:
            if file.endswith(".tdms"):
                try:
                    # Read the TDMS file
                    tdms_file = TdmsFile.read(os.path.join(root, file))
                    df = tdms_file.as_dataframe()

                    # Remove columns that only contain NaN values
                    df = df.dropna(axis=1, how='all')

                    # Clean up column names
                    df.columns = df.columns.str.replace("/", "")
                    df.columns = df.columns.str.replace("'", "")
                    df.columns = df.columns.str.replace("Data", "")
                    df.columns = df.columns.str.strip()
                    df['Displacement'] = calculate_pump_displacement(df['Main_Flow_GPM'], df['RPM'])
                    # Calculate mean values
                    mean_main_flow_gpm = df["Main_Flow_GPM"].mean() if "Main_Flow_GPM" in df.columns else None
                    mean_rpm = df["RPM"].mean() if "RPM" in df.columns else None
                    mean_outlet_pressure_psi = df[
                        "Outlet_Pressure_Psi"].mean() if "Outlet_Pressure_Psi" in df.columns else None
                    mean_displacement = df['Displacement'].mean()
                    mean_inlet_temp = df['Inlet_Temp_F'].mean()
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
                    print(f"Error processing file {file}: {e}")
    max_derived_displacement = all_df['Mean_Displacement'].max()
    return all_df,max_derived_displacement


def process_tdms_to_csv(max_derived_displacement, temp_percent_tdms_dir):
    """
    Process TDMS files in a directory and save the processed data to CSV files.

    Args:
        max_derived_displacement (float): The maximum derived displacement.
        temp_percent_tdms_dir (str): The path to the directory containing the TDMS files.
    """
    for root, dirs, files in os.walk(temp_percent_tdms_dir):
        for file in files:
            if file.endswith('.tdms'):  # Check if the file is a TDMS file
                try:
                    tdms_file = TdmsFile.read(os.path.join(root, file))
                    df = tdms_file.as_dataframe()

                    # Drop columns with all NaN values
                    df = df.dropna(axis=1, how='all')

                    # Clean up column names
                    df.columns = df.columns.str.replace("/", "")
                    df.columns = df.columns.str.replace("'", "")
                    df.columns = df.columns.str.replace("Data", "")
                    df.columns = df.columns.str.strip()

                    # Calculate displacement
                    df['Displacement'] = calculate_pump_displacement(df['Main_Flow_GPM'], df['RPM'])

                    # Calculate the new columns
                    df['Calc_VE'] = df['Displacement'] * 100 / max_derived_displacement
                    df['Calc_ME'] = 100 * (
                                (((max_derived_displacement / 16.387064) * df['Outlet_Pressure_Psi']) / (2 * math.pi)) /
                                df['Pump_Torque_In.lbf'])
                    df['Calc_OE'] = df['Calc_VE'] * df['Calc_ME'] / 100


                    # Save to the destination directory
                    output_file = os.path.join(temp_percent_tdms_dir, f"processed_{file.replace('.tdms', '.csv')}")
                    df.to_csv(output_file, index=False)

                except Exception as e:
                    print(f"Error processing file {file}: {e}")


def get_stats_df(temp_percent_tdms_dir, max_derived_displacement):
    """
    Generate a DataFrame with statistics for each processed CSV file in a directory.

    Args:
        temp_percent_tdms_dir (str): The path to the directory containing the processed CSV files.
        max_derived_displacement (float): The maximum derived displacement.

    Returns:
        DataFrame: A DataFrame containing statistics for each file.
    """
    statistics_df = pd.DataFrame(columns=("TDMS file", "Speed", "Outlet Pressure", "Derived Displacement"))

    for root, dirs, files in os.walk(temp_percent_tdms_dir):
        for file in files:
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(root, file))

                # Extract speed and pressure from the filename
                temp_arr = file.split("_")
                speed = 0
                pressure = 0
                for item in temp_arr:
                    if "rpm" in item:
                        digits = ''.join(re.findall(r'\d', item))
                        speed = int(digits) if digits else 0
                    elif "psi" in item:
                        digits = ''.join(re.findall(r'\d', item))
                        pressure = int(digits) if digits else 0

                # Calculate statistics for each column
                stats = {}
                for col in df.columns:
                    if col not in ['Time_ms', '%VE', '%OVE', '%ME']:
                        stats[f'{col}_mean'] = df[col].mean()
                        stats[f'{col}_stddev'] = df[col].std()

                # Create a row with the statistics
                td_file = file
                row = {
                    "TDMS file": td_file,
                    "Speed": speed,
                    "Outlet Pressure": pressure,
                    "Derived Displacement": max_derived_displacement,
                    **stats
                }

                # Append the row to the statistics DataFrame
                statistics_df = statistics_df._append(row, ignore_index=True)

    # Clean up the 'TDMS file' column
    statistics_df['TDMS file'] = statistics_df['TDMS file'].str.replace('processed_', '', regex=False)
    statistics_df['TDMS file'] = statistics_df['TDMS file'].str.replace('.csv', '.tdms', regex=False)

    return statistics_df


def get_pivot_tables(statistics_df):
    """
    Create pivot tables for VE, ME, and OE from the statistics DataFrame.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        tuple: A tuple containing three pivot tables for VE, ME, and OE.
    """
    ve_pivot = statistics_df.pivot(
        index='Outlet Pressure',
        columns='Speed',
        values='Calc_VE_mean'
    )

    me_pivot = statistics_df.pivot(
        index='Outlet Pressure',
        columns='Speed',
        values='Calc_ME_mean'
    )

    oe_pivot = statistics_df.pivot(
        index='Outlet Pressure',
        columns='Speed',
        values='Calc_OE_mean'
    )

    return ve_pivot, me_pivot, oe_pivot


def interp_df(ve_pivot,  me_pivot,oe_pivot):
    """
    Interpolates data from given pivot tables.

    Args:
        ve_pivot (DataFrame): VE pivot table.
        oe_pivot (DataFrame): OE pivot table.
        me_pivot (DataFrame): ME pivot table.

    Returns:
        tuple: Interpolated DataFrames for VE, ME, and OE.
    """
    original_speeds = ve_pivot.columns.astype(float).tolist()
    original_pressures = ve_pivot.index.astype(float).tolist()

    # Define the new speed and pressure ranges
    new_speeds = np.arange(525, 3476, 25)
    new_pressures = np.arange(550, 5001, 50)

    # Create meshgrid for new speeds and pressures
    new_speeds_mesh, new_pressures_mesh = np.meshgrid(new_speeds, new_pressures)
    new_points = np.array([new_pressures_mesh.ravel(), new_speeds_mesh.ravel()]).T

    # Interpolation for ve_pivot
    ve_interp_func = RegularGridInterpolator((original_pressures, original_speeds), ve_pivot.values)
    ve_interpolated = ve_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    ve_interpolated_df = pd.DataFrame(ve_interpolated, index=new_pressures, columns=new_speeds)

    # Interpolation for me_pivot
    me_interp_func = RegularGridInterpolator((original_pressures, original_speeds), me_pivot.values)
    me_interpolated = me_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    me_interpolated_df = pd.DataFrame(me_interpolated, index=new_pressures, columns=new_speeds)

    # Interpolation for oe_pivot
    oe_interp_func = RegularGridInterpolator((original_pressures, original_speeds), oe_pivot.values)
    oe_interpolated = oe_interp_func(new_points).reshape(len(new_pressures), len(new_speeds))
    oe_interpolated_df = pd.DataFrame(oe_interpolated, index=new_pressures, columns=new_speeds)

    return ve_interpolated_df, me_interpolated_df, oe_interpolated_df


def create_performance_excel(filename, all_df, statistics_df, ve_pivot, me_pivot, oe_pivot, ve_interpolated_df,
                             me_interpolated_df, oe_interpolated_df):
    """
    Save the given DataFrames and pivot tables to an Excel file.

    Args:
        filename (str): The name of the output Excel file.
        all_df (DataFrame): The DataFrame containing all data.
        statistics_df (DataFrame): The DataFrame containing statistics.
        ve_pivot (DataFrame): The pivot table for VE.
        me_pivot (DataFrame): The pivot table for ME.
        oe_pivot (DataFrame): The pivot table for OE.
        ve_interpolated_df (DataFrame): The interpolated VE DataFrame.
        me_interpolated_df (DataFrame): The interpolated ME DataFrame.
        oe_interpolated_df (DataFrame): The interpolated OE DataFrame.
    """
    output_file = filename

    try:
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

            # Write interpolated DataFrames to a new sheet
            ve_interpolated_df.to_excel(writer, sheet_name='Interpolated Data', startrow=0)
            startrow = ve_interpolated_df.shape[0] + 2
            me_interpolated_df.to_excel(writer, sheet_name='Interpolated Data', startrow=startrow)
            startrow += me_interpolated_df.shape[0] + 2
            oe_interpolated_df.to_excel(writer, sheet_name='Interpolated Data', startrow=startrow)

        print(f"DataFrames have been successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred while saving to Excel: {e}")


def ve_contour(statistics_df):
    """
    Create a contour plot for Volumetric Efficiency (VE) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot.
    """

    X = statistics_df['Outlet Pressure']
    Y = statistics_df['Speed']
    Z = statistics_df['Calc_VE_mean']

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), X.max(), 100),
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
    ax.set_xlabel('Outlet Pressure')
    ax.set_ylabel('RPM (Speed)')
    ax.set_title('Contour Plot of VE, RPM, and Outlet Pressure')

    # Return the figure object
    return fig


def me_contour(statistics_df):
    """
    Create a contour plot for Mechanical Efficiency (ME) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot.
    """

    X = statistics_df['Outlet Pressure']
    Y = statistics_df['Speed']
    Z = statistics_df['Calc_ME_mean']

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), X.max(), 100),
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
    ax.set_title('Contour Plot of ME, RPM, and Outlet Pressure')

    # Return the figure object
    return fig


def oe_contour(statistics_df):
    """
    Create a contour plot for Overall Efficiency (OE) based on speed and outlet pressure.

    Args:
        statistics_df (DataFrame): The DataFrame containing statistics.

    Returns:
        Figure: The matplotlib figure object for the contour plot.
    """
    Y = statistics_df['Speed']
    X = statistics_df['Outlet Pressure']
    Z = statistics_df['Calc_OE_mean']

    # Create a grid for interpolation
    X_grid, Y_grid = np.meshgrid(
        np.linspace(X.min(), X.max(), 100),
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
    ax.set_xlabel('Outlet Pressure')
    ax.set_ylabel('RPM (Speed)')
    ax.set_title('Contour Plot of OE, RPM, and Outlet Pressure')

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
    ax.set_xlabel('Outlet Pressure')
    ax.set_ylabel('OE (Overall Efficiency)')
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


def main():
    """
    Main function to process TDMS files, calculate statistics, create pivot tables,
    and generate plots for efficiency tests. Results are saved to an Excel file and
    as image files in a unique results directory.
    """
    # Define the directory containing the TDMS files and the output filename
    directory_name = r'C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\PistonPump\180F'
    filename = r'performance.xlsx'

    # Remove duplicate TDMS files in the directory
    remove_duplicate_files(directory_name)

    # Walk through the directory structure
    for root, dirs, files in os.walk(directory_name):
        for dir_name in dirs:
            if 'F' in dir_name:
                for root1, dirs1, files1 in os.walk(os.path.join(root, dir_name)):
                    for dir_name1 in dirs1:
                        if '%' in dir_name1:
                            print("Processing: " + os.path.join(root1, dir_name1))

                            # Get displacement DataFrame and maximum derived displacement
                            displacement_df, max_derived_displacement = get_displacement_df(
                                os.path.join(root1, dir_name1))

                            # Process TDMS files and save to CSV
                            process_tdms_to_csv(max_derived_displacement, os.path.join(root1, dir_name1))

                            # Get statistics DataFrame
                            statistics_df = get_stats_df(os.path.join(root1, dir_name1), max_derived_displacement)

                            # Create pivot tables
                            ve_pivot, me_pivot, oe_pivot = get_pivot_tables(statistics_df)
                            ve_interp_df,me_interp_df,oe_interp_df = interp_df(ve_pivot,me_pivot,oe_pivot)
                            # Create a unique directory for saving results based on the parent directory name
                            result_dir = os.path.join(root1, dir_name1, 'results')
                            os.makedirs(result_dir, exist_ok=True)

                            # Save the Excel file with all data and statistics
                            create_performance_excel(os.path.join(result_dir, filename), displacement_df, statistics_df,
                                                    ve_pivot, me_pivot, oe_pivot,ve_interp_df,me_interp_df,oe_interp_df)

                            # Generate and save VE contour plot
                            ve_contour_plot = ve_contour(statistics_df)
                            ve_contour_plot.savefig(os.path.join(result_dir, 've_contour_plot.png'), dpi=300,
                                                    bbox_inches='tight')

                            # Generate and save ME contour plot
                            me_contour_plot = me_contour(statistics_df)
                            me_contour_plot.savefig(os.path.join(result_dir, 'me_contour_plot.png'), dpi=300,
                                                    bbox_inches='tight')

                            # Generate and save OE contour plot
                            oe_contour_plot = oe_contour(statistics_df)
                            oe_contour_plot.savefig(os.path.join(result_dir, 'oe_contour_plot.png'), dpi=300,
                                                    bbox_inches='tight')

                            # Generate and save efficiency map plot
                            efficiency_map_plot = efficiency_map(statistics_df)
                            efficiency_map_plot.savefig(os.path.join(result_dir, 'efficiency_map_plot.png'), dpi=300,
                                                        bbox_inches='tight')

                            # Generate and save flow line plot
                            flow_line_plot = create_flow_line_plot(statistics_df)
                            flow_line_plot.savefig(os.path.join(result_dir, 'flow_line_plot.png'), dpi=300,
                                                   bbox_inches='tight')

if __name__ == "__main__":
    main()