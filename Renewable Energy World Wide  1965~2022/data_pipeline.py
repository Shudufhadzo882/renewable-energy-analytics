import pandas as pd
import os

def merge_renewable_datasets(input_dir, output_file):
    print("Starting Data Pipeline...")
    
    # 1. Load Core Datasets
    # File 01: Share of energy
    # File 03: Production (Wind, Hydro, Solar, Bio)
    # File 13: Solar Capacity (as a sample for capacity)
    
    f01 = os.path.join(input_dir, "01 renewable-share-energy.csv")
    f03 = os.path.join(input_dir, "03 modern-renewable-prod.csv")
    f13 = os.path.join(input_dir, "13 installed-solar-PV-capacity.csv")
    
    if not all(os.path.exists(f) for f in [f01, f03, f13]):
        print("Missing one or more core CSV files.")
        return

    df_share = pd.read_csv(f01)
    df_prod = pd.read_csv(f03)
    df_cap = pd.read_csv(f13)

    # 2. Standardize Column Names
    # Note: Column names in these files are often long. We will simplify them.
    df_share.rename(columns={'Renewables (% equivalent primary energy)': 'Renewable_Share_Pct'}, inplace=True)
    
    # 3. Merge Datasets
    # Merge on Entity, Code, Year
    print("Merging datasets...")
    merged_df = pd.merge(df_prod, df_share, on=['Entity', 'Code', 'Year'], how='left')
    merged_df = pd.merge(merged_df, df_cap, on=['Entity', 'Code', 'Year'], how='left')

    # 4. Implement Metrics
    print("Implementing KPIs...")
    
    # Growth Rate (5-year CAGR proxy)
    merged_df = merged_df.sort_values(['Entity', 'Year'])
    merged_df['Total_Prod_TWh'] = (
        merged_df['Electricity from wind (TWh)'].fillna(0) + 
        merged_df['Electricity from hydro (TWh)'].fillna(0) + 
        merged_df['Electricity from solar (TWh)'].fillna(0) + 
        merged_df['Other renewables including bioenergy (TWh)'].fillna(0)
    )
    
    # Resilience Index: Non-Hydro Renewables / Total Renewables
    # This shows how much a country is diversifying away from just Hydro.
    merged_df['Non_Hydro_Prod'] = merged_df['Total_Prod_TWh'] - merged_df['Electricity from hydro (TWh)'].fillna(0)
    merged_df['Resilience_Index'] = (merged_df['Non_Hydro_Prod'] / merged_df['Total_Prod_TWh']).fillna(0)

    # Growth Score: 5-year production growth
    merged_df['Prod_5yr_Ago'] = merged_df.groupby('Entity')['Total_Prod_TWh'].shift(5)
    merged_df['Growth_Score'] = ((merged_df['Total_Prod_TWh'] - merged_df['Prod_5yr_Ago']) / merged_df['Prod_5yr_Ago']).fillna(0)

    # 5. Save Processed Data
    merged_df.to_csv(output_file, index=False)
    print(f"Master dataset created: {output_file}")
    print(f"Final Shape: {merged_df.shape}")

if __name__ == "__main__":
    workspace = "." # Current directory
    merge_renewable_datasets(workspace, "processed_renewable_data.csv")
