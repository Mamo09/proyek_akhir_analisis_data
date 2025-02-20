import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    main_data_df = pd.read_csv("main_data.csv", parse_dates=['dteday'])
    return main_data_df

main_data_df = load_data()

# Title and description
st.title("🚲 Bike Rental Analysis Dashboard")
st.markdown("Analysis of bike sharing patterns and customer behavior")

# Sidebar filters
with st.sidebar:
    st.header("Filter Data")
    
    # Date range filter
    min_date = main_data_df['dteday'].min().date()
    max_date = main_data_df['dteday'].max().date()
    
    start_date = st.date_input('Start Date', min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input('End Date', max_date, min_value=min_date, max_value=max_date)
    
    # Season filter
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    selected_season = st.multiselect(
        "Select Season",
        options=list(season_map.keys()),
        default=list(season_map.keys()),
        format_func=lambda x: season_map[x]
    )
    
    # Weather filter
    weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
    selected_weather = st.multiselect(
        "Select Weather",
        options=list(weather_map.keys()),
        default=list(weather_map.keys()),
        format_func=lambda x: weather_map[x]
    )
    
    # Working day filter
    workingday = st.radio("Working Day", ["All", "Working Day", "Holiday/Weekend"])
    
    # Temperature range
    temp_range = st.slider("Temperature Range (Normalized)", 
                          float(main_data_df['temp'].min()), 
                          float(main_data_df['temp'].max()), 
                          (float(main_data_df['temp'].min()), float(main_data_df['temp'].max())))

# Filter data
date_filtered_df = main_data_df[
    (main_data_df['dteday'].dt.date >= start_date) & 
    (main_data_df['dteday'].dt.date <= end_date) &
    (main_data_df['season'].isin(selected_season)) &
    (main_data_df['weathersit'].isin(selected_weather)) &
    (main_data_df['temp'].between(temp_range[0], temp_range[1]))
]

if workingday != "All":
    date_filtered_df = date_filtered_df[
        date_filtered_df['workingday'] == (1 if workingday == "Working Day" else 0)
    ]

# Download button for filtered data
csv = date_filtered_df.to_csv(index=False)
st.sidebar.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='filtered_bike_rentals.csv',
    mime='text/csv',
)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Hourly Patterns", "Daily Patterns", "Monthly Patterns", "Yearly Trend", "Customer Analysis"])

with tab1:
    st.header("Hourly Rental Patterns")
    
    # Average rentals by hour
    hourly_trend = date_filtered_df.groupby('hr')['cnt'].mean().reset_index()
    fig = px.line(hourly_trend, x='hr', y='cnt',
                  title='Average Rentals by Hour of Day',
                  labels={'hr': 'Hour', 'cnt': 'Average Rentals'},
                  markers=True)
    fig.update_layout(
        xaxis_title="Hour (24-hour format)",
        yaxis_title="Average Number of Rentals",
        hovermode='x'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights for hourly pattern
    st.subheader("Key Insights - Hourly Pattern")
    peak_hour = hourly_trend.loc[hourly_trend['cnt'].idxmax()]
    low_hour = hourly_trend.loc[hourly_trend['cnt'].idxmin()]
    st.write(f"- Peak rental hour: {int(peak_hour['hr']):02d}:00 with average {peak_hour['cnt']:.0f} rentals")
    st.write(f"- Lowest rental hour: {int(low_hour['hr']):02d}:00 with average {low_hour['cnt']:.0f} rentals")

with tab2:
    st.header("Daily Rental Patterns")
    
    # Map weekday numbers to names
    weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 
                   4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    
    # Daily pattern
    daily_trend = date_filtered_df.groupby('weekday')['cnt'].mean().reset_index()
    daily_trend['weekday_name'] = daily_trend['weekday'].map(weekday_map)
    
    fig = px.bar(daily_trend, x='weekday_name', y='cnt',
                 title='Average Rentals by Day of Week',
                 labels={'weekday_name': 'Day of Week', 'cnt': 'Average Rentals'},
                 color='cnt')
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Average Number of Rentals"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # User type comparison by day
    daily_user_trend = date_filtered_df.groupby('weekday')[['casual', 'registered']].mean().reset_index()
    daily_user_trend['weekday_name'] = daily_user_trend['weekday'].map(weekday_map)
    
    fig = px.bar(daily_user_trend, x='weekday_name', 
                 y=['casual', 'registered'],
                 title='Casual vs Registered Users by Day',
                 barmode='group',
                 labels={'value': 'Average Rentals', 'variable': 'User Type'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights for daily pattern
    st.subheader("Key Insights - Daily Pattern")
    peak_day = daily_trend.loc[daily_trend['cnt'].idxmax()]
    low_day = daily_trend.loc[daily_trend['cnt'].idxmin()]
    st.write(f"- Busiest day: {peak_day['weekday_name']} with average {peak_day['cnt']:.0f} rentals")
    st.write(f"- Slowest day: {low_day['weekday_name']} with average {low_day['cnt']:.0f} rentals")

with tab3:
    st.header("Monthly Rental Patterns")
    
    # Map month numbers to names
    month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    # Monthly pattern
    monthly_trend = date_filtered_df.groupby('mnth')['cnt'].mean().reset_index()
    monthly_trend['month_name'] = monthly_trend['mnth'].map(month_map)
    
    fig = px.line(monthly_trend, x='month_name', y='cnt',
                  title='Average Monthly Rentals Throughout the Year',
                  labels={'month_name': 'Month', 'cnt': 'Average Rentals'},
                  markers=True)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Number of Rentals",
        xaxis={'categoryorder': 'array',
               'categoryarray': list(month_map.values())}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights for monthly pattern
    st.subheader("Key Insights - Monthly Pattern")
    peak_month = monthly_trend.loc[monthly_trend['cnt'].idxmax()]
    low_month = monthly_trend.loc[monthly_trend['cnt'].idxmin()]
    st.write(f"- Peak month: {peak_month['month_name']} with average {peak_month['cnt']:.0f} rentals")
    st.write(f"- Lowest month: {low_month['month_name']} with average {low_month['cnt']:.0f} rentals")

with tab4:
    st.header("Yearly Rental Trends")
    
    # Calculate yearly statistics
    yearly_trend = date_filtered_df.groupby('yr')['cnt'].agg(['mean', 'sum']).reset_index()
    yearly_trend['yr'] = yearly_trend['yr'].map({0: '2011', 1: '2012'})
    
    # Year over year growth
    yoy_growth = ((yearly_trend['sum'].iloc[1] - yearly_trend['sum'].iloc[0]) / 
                  yearly_trend['sum'].iloc[0] * 100)
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(yearly_trend, x='yr', y='sum',
                     title='Total Rentals by Year',
                     labels={'yr': 'Year', 'sum': 'Total Rentals'},
                     color='sum')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(yearly_trend, x='yr', y='mean',
                      title='Average Daily Rentals by Year',
                      labels={'yr': 'Year', 'mean': 'Average Rentals'},
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights for yearly trend
    st.subheader("Key Insights - Yearly Trend")
    st.write(f"""
    - Year-over-Year Growth: **{yoy_growth:.1f}%**
    - 2011 Total Rentals: **{yearly_trend['sum'].iloc[0]:,.0f}**
    - 2012 Total Rentals: **{yearly_trend['sum'].iloc[1]:,.0f}**
    - 2011 Average Daily Rentals: **{yearly_trend['mean'].iloc[0]:.0f}**
    - 2012 Average Daily Rentals: **{yearly_trend['mean'].iloc[1]:.0f}**
    """)

with tab5:
    st.header("Customer Behavior Analysis (RFM)")
    
    # Calculate RFM metrics
    # Recency: days since last rental
    last_date = date_filtered_df['dteday'].max()
    rfm_df = date_filtered_df.groupby('registered').agg({
        'dteday': lambda x: (last_date - x.max()).days,  # Recency
        'instant': 'count',  # Frequency
        'cnt': 'sum'  # Monetary (total rentals)
    }).reset_index()
    
    # Rename columns
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'total_rentals']
    
    # Create three columns for RFM metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Recency Distribution")
        fig = px.histogram(rfm_df, x='recency',
                          title='Days Since Last Rental',
                          labels={'recency': 'Days', 'count': 'Number of Customers'},
                          nbins=30)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recency insights
        avg_recency = rfm_df['recency'].mean()
        st.markdown(f"**Average Days Since Last Rental:** {avg_recency:.1f} days")
    
    with col2:
        st.subheader("Frequency Distribution")
        fig = px.histogram(rfm_df, x='frequency',
                          title='Number of Rentals per Customer',
                          labels={'frequency': 'Number of Rentals', 'count': 'Number of Customers'},
                          nbins=30)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Frequency insights
        avg_frequency = rfm_df['frequency'].mean()
        st.markdown(f"**Average Rentals per Customer:** {avg_frequency:.1f}")
    
    with col3:
        st.subheader("Total Rentals Distribution")
        fig = px.histogram(rfm_df, x='total_rentals',
                          title='Total Rentals by Customer',
                          labels={'total_rentals': 'Total Rentals', 'count': 'Number of Customers'},
                          nbins=30)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Overall patterns summary
st.markdown("---")
st.header("Summary of Rental Patterns")
st.write("""
- **Hourly Pattern**: Shows typical daily usage cycles with peaks during commute hours
- **Daily Pattern**: Highlights differences between weekday and weekend usage
- **Monthly Pattern**: Reveals seasonal trends in bike rental behavior
- **Yearly Trend**: Demonstrates overall growth in bike rental usage from 2011 to 2012
""")
