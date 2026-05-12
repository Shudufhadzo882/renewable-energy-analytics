import pandas as pd
import glob
import os

def generate_renewable_summary():
    # Define files of interest
    prod_file = "03 modern-renewable-prod.csv"
    share_file = "01 renewable-share-energy.csv"
    
    if not os.path.exists(prod_file) or not os.path.exists(share_file):
        print("Missing core CSV files for analysis.")
        return

    # Load production data
    df_prod = pd.read_csv(prod_file)
    
    # Filter for Africa to align with project goals
    africa_prod = df_prod[df_prod['Entity'].str.contains("Africa", na=False)]
    
    # Identify top growth periods
    latest_year = africa_prod['Year'].max()
    baseline_year = latest_year - 10
    
    recent_growth = africa_prod[africa_prod['Year'] >= baseline_year]
    
    print(f"--- Renewable Energy Production in Africa ({baseline_year}-{latest_year}) ---")
    summary = recent_growth.groupby('Year').agg({
        'Electricity from wind (TWh)': 'sum',
        'Electricity from hydro (TWh)': 'sum',
        'Electricity from solar (TWh)': 'sum'
    })
    print(summary)
    
    # Calculate Year-over-Year Growth for Solar (Fastest growing)
    summary['Solar_YoY_Growth'] = summary['Electricity from solar (TWh)'].pct_change() * 100
    print("\n--- Solar PV Year-over-Year Growth (%) ---")
    print(summary[['Electricity from solar (TWh)', 'Solar_YoY_Growth']].dropna())

if __name__ == "__main__":
    generate_renewable_summary()
