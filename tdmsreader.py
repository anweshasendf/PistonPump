from nptdms import TdmsFile
import pandas as pd
import os

# Read the TDMS file
#join with current path
#file_path = os.path.join(os.getcwd(), "1_1.tdms")
file_path = r"C:\Users\U436445\Downloads\EfficiencyTest_Gen\Efficency test\180F\75%\P16_HY5_Eff_180F_75%_500rpm_500psi.tdms"
tdms_file = TdmsFile.read(file_path)

# Convert TDMS data to a dictionary of DataFrames
data = {group.name: group.as_dataframe() for group in tdms_file.groups()}

# Display the data as an organized DataFrame
for group_name, df in data.items():
    print(f"Group: {group_name}")
    print(df.columns)
    print(df)
    
#/'Data'/'Time'	/'Data'/'Inlet_temp'
