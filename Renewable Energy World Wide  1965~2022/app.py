import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Renewable Energy World Wide | Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
def apply_premium_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .stMetric {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .stSidebar {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    
    h1, h2, h3 {
        color: #60a5fa;
        font-weight: 700;
    }
    
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }

    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

apply_premium_style()

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("processed_renewable_data.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please run the data pipeline first.")
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.title("⚡ Renewable Analytics")
    st.markdown("---")
    nav = st.radio("Navigation", ["Global Overview", "Regional Deep Dive", "Equity & Resilience"])
    
    st.markdown("---")
    st.markdown("### Filters")
    years = sorted(df['Year'].unique())
    year_range = st.slider("Select Year Range", min(years), max(years), (2000, 2021))
    
    entities = sorted(df['Entity'].unique())
    selected_entity = st.selectbox("Select Country/Region", entities, index=entities.index("World") if "World" in entities else 0)

# Filter Data
filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
entity_df = filtered_df[filtered_df['Entity'] == selected_entity]

# --- Main Dashboard ---
if nav == "Global Overview":
    st.title("🌎 Global Renewable Overview")
    st.subheader(f"Analyzing energy transitions from {year_range[0]} to {year_range[1]}")
    
    # Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    # Use the latest year in the selected range for the current entity
    latest_year_in_range = entity_df['Year'].max()
    latest_stats = entity_df[entity_df['Year'] == latest_year_in_range]
    
    if not latest_stats.empty:
        total_twh = latest_stats['Total_Prod_TWh'].values[0]
        solar_twh = latest_stats['Electricity from solar (TWh)'].values[0]
        resilience = latest_stats['Resilience_Index'].values[0]
        growth = latest_stats['Growth_Score'].values[0]
        
        m1.metric(f"Production ({latest_year_in_range})", f"{total_twh:,.0f} TWh")
        m2.metric("Solar Share", f"{(solar_twh/total_twh)*100:.1f}%" if total_twh > 0 else "0.0%")
        m3.metric("Resilience Index", f"{resilience:.2f}")
        m4.metric("Growth Score", f"{growth*100:.1f}%")

    # Trend Chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Production Trends by Source")
    trend_cols = ['Electricity from wind (TWh)', 'Electricity from hydro (TWh)', 'Electricity from solar (TWh)', 'Other renewables including bioenergy (TWh)']
    fig_trend = px.area(entity_df, x='Year', y=trend_cols, 
                        labels={'value': 'Production (TWh)', 'variable': 'Source'},
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.qualitative.Safe)
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Top Producers
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"### 🏆 Top Producers ({latest_year_in_range})")
        top_10 = filtered_df[(filtered_df['Year'] == latest_year_in_range) & (filtered_df['Code'].notna())].sort_values('Total_Prod_TWh', ascending=False).head(10)
        fig_top = px.bar(top_10, x='Total_Prod_TWh', y='Entity', orientation='h',
                         color='Total_Prod_TWh', color_continuous_scale='Blues')
        st.plotly_chart(fig_top, use_container_width=True)

    with col_b:
        st.markdown(f"### 🧩 Energy Mix ({selected_entity})")
        mix_data = latest_stats[trend_cols].T.reset_index()
        mix_data.columns = ['Source', 'TWh']
        fig_pie = px.pie(mix_data, values='TWh', names='Source', hole=0.6,
                         color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig_pie, use_container_width=True)

elif nav == "Regional Deep Dive":
    st.title("📍 Regional Deep Dive")
    st.subheader(f"Detailed analysis for: {selected_entity}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔋 Capacity vs. Production")
        # Note: We only have solar capacity in this merged dataset for now
        fig_cap = go.Figure()
        fig_cap.add_trace(go.Bar(x=entity_df['Year'], y=entity_df['Electricity from solar (TWh)'], name="Solar Production (TWh)"))
        fig_cap.add_trace(go.Scatter(x=entity_df['Year'], y=entity_df['Solar Capacity'], name="Solar Capacity (GW)", yaxis="y2"))
        
        fig_cap.update_layout(
            template="plotly_dark",
            yaxis=dict(title="Production (TWh)"),
            yaxis2=dict(title="Capacity (GW)", overlaying="y", side="right"),
            legend=dict(orientation="h")
        )
        st.plotly_chart(fig_cap, use_container_width=True)

    with col2:
        st.markdown("### 📊 Statistics Snapshot")
        st.dataframe(entity_df[['Year', 'Total_Prod_TWh', 'Resilience_Index', 'Renewable_Share_Pct']].tail(10), use_container_width=True)

elif nav == "Equity & Resilience":
    st.title("⚖️ Equity & Resilience Matrix")
    
    # Hardcoded GDP data for Equity Score (Demo purpose)
    gdp_data = {
        'China': 12556, 'United States': 70248, 'Brazil': 7507, 'India': 2256, 
        'Germany': 51203, 'Japan': 39312, 'Canada': 51987, 'World': 12262
    }
    
    st.info("The Resilience Index measures the diversification of renewables away from traditional Hydropower.")
    
    # Resilience Map
    st.markdown("### 🌍 Global Resilience Index (2021)")
    df_2021 = df[(df['Year'] == 2021) & (df['Code'].notna())]
    fig_map = px.choropleth(df_2021, locations="Code", color="Resilience_Index",
                            hover_name="Entity", color_continuous_scale="Viridis",
                            title="Higher Resilience = Higher Diversification (Wind/Solar vs Hydro)")
    fig_map.update_layout(template="plotly_dark", geo=dict(bgcolor= 'rgba(0,0,0,0)'))
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Resilience vs Growth Scatter
    st.markdown("### 📈 Resilience vs. Growth Momentum")
    fig_scatter = px.scatter(df_2021, x="Resilience_Index", y="Growth_Score",
                             size="Total_Prod_TWh", color="Entity",
                             hover_name="Entity", log_y=True,
                             labels={'Growth_Score': '5-yr Growth Rate (Log)'})
    st.plotly_chart(fig_scatter, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("⚡ **Renewable Energy Insights Dashboard** | Data Source: Kaggle / Our World in Data | Developed by **Shudufhadzo Lesley Raphalalani**")
