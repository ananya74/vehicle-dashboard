import pandas as pd
import streamlit as st
def load_manufacturer_data(file_path, year):
    df = pd.read_excel(file_path, sheet_name='reportTable', skiprows=4)
    df.columns = df.columns.str.strip()  # Clean up column names

    df = df.rename(columns={'Unnamed: 1': 'Maker'})  # Rename to something meaningful
    df = df.dropna(subset=['Maker'])
    df['Year'] = year
    return df[['Maker', '4WIC', 'LMV', 'MMV', 'HMV', 'TOTAL', 'Year']]


def load_vehicle_class_data(file_path, year, category):
    df = pd.read_excel(file_path, sheet_name='reportTable', skiprows=4)
    df.columns = df.columns.str.strip()
    
    # Rename only 2nd column to 'Vehicle Class'
    df.columns.values[1] = 'Vehicle Class'

    df = df.dropna(subset=['Vehicle Class'])

    df['Year'] = year
    df['category'] = category

    # Define which columns to return based on vehicle category
    category_columns_map = {
        '2W': ['2WIC', '2WN', '2WT'],
        '3W': ['3WN', '3WT'],
        '4W': ['LMV', 'MMV', 'HMV'],
    }

    selected_columns = ['Vehicle Class'] + category_columns_map.get(category, []) + ['TOTAL', 'Year', 'category']

    # Debug print
    
    

    return df[selected_columns]



def load_qoq_data(path_2024, path_2025):
    import pandas as pd

    MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    def clean_sheet(path, year):
        # Correct header row is 3 (i.e. 4th row in Excel — JAN, FEB, ...)
        df = pd.read_excel(path, header=3)

        # Rename second column to "Maker" if unnamed
        if "Maker" not in df.columns:
            df.columns.values[1] = "Maker"

        # Drop TOTAL column if exists
        df = df.drop(columns=["TOTAL"], errors="ignore")

        # Drop rows where Maker is missing
        df = df.dropna(subset=["Maker"])
        df["YEAR"] = year

        # Coerce month columns to numeric
        for month in MONTHS:
            if month in df.columns:
                df[month] = pd.to_numeric(df[month], errors="coerce")

        # Melt to long format
        df_long = df.melt(
            id_vars=["Maker", "YEAR"],
            value_vars=[col for col in MONTHS if col in df.columns],
            var_name="Month",
            value_name="Value"
        )
        return df_long

    df_2024 = clean_sheet(path_2024, 2024)
    df_2025 = clean_sheet(path_2025, 2025)

    combined = pd.concat([df_2024, df_2025], ignore_index=True)
    return combined
