
import pandas as pd
import os

file_path = 'hybrid_cloud_test_cases.xlsx'

try:
    # Read the excel file
    xls = pd.ExcelFile(file_path)
    print(f"File found: {file_path}")
    print(f"Sheet names: {xls.sheet_names}")
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"\n--- Sheet: {sheet_name} ---")
        print(df.to_string())
        
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except ImportError as e:
    print(f"Error: Missing dependency. {e}")
except Exception as e:
    print(f"Error reading excel file: {e}")
