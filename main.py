import os
import pandas as pd
import geopandas as gpd
import streamlit as st  # Import streamlit here
from core import methods as m1
from core import HelperTools as ht
from config import pdict

@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""
    # Load data
    df_geodat_plz = pd.read_csv('datasets/geodata_berlin_plz.csv', sep=';')  # For geospatial data
    df_lstat = pd.read_excel('datasets/Ladesaeulenregister_SEP.xlsx', header=10)

    # Inspect data (optional debugging statements)
    print("Sample data from df_lstat:", df_lstat.head())

    df_residents = pd.read_csv('datasets/plz_einwohner.csv')  # Adjust the path accordingly

    # Data Quality Checks
    required_columns_charging = ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']
    column_formats_charging = {
        'Postleitzahl': int,
        'Bundesland': str,
        'Breitengrad': (float, str),  # Allow strings due to conversion step
        'Längengrad': (float, str),
        'Nennleistung Ladeeinrichtung [kW]': float
    }
    value_ranges_charging = {
        'Postleitzahl': (10000, 14200),
        'Nennleistung Ladeeinrichtung [kW]': (0, 1000)
    }
    quality_issues_lstat = ht.check_data_quality(df_lstat, required_columns_charging, column_formats_charging, value_ranges_charging)
    if quality_issues_lstat:
        print("Data Quality Issues for Charging Stations:", quality_issues_lstat)

    required_columns_residents = ['plz', 'einwohner', 'lat', 'lon']
    column_formats_residents = {
        'plz': int,
        'einwohner': int,
        'lat': float,
        'lon': float
    }
    value_ranges_residents = {
        'plz': (10000, 14200),
        'einwohner': (0, 50000)
    }
    quality_issues_residents = ht.check_data_quality(df_residents, required_columns_residents, column_formats_residents, value_ranges_residents)
    if quality_issues_residents:
        print("Data Quality Issues for Residents Data:", quality_issues_residents)

    # Preprocess data
    gdf_lstat = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

    # Streamlit app logic with radio button for function selection
    st.title('Berlin Electric Charging Station Heatmaps')
    function_selection = st.radio(
        "Select Visualization Type",
        (
            "Heatmap: Electric Charging Stations and Residents",
            "Heatmap: Electric Charging Stations by KW and Residents"
        )
    )

    if function_selection == "Heatmap: Electric Charging Stations and Residents":
        m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)
    else:
        m1.make_streamlit_electric_Charging_resid_by_kw(gdf_lstat3, gdf_residents2)

if __name__ == "__main__":
    main()
