import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better visualization
plt.style.use('seaborn-v0_8')  # Updated style name for newer versions
sns.set_theme()  # Use seaborn's default theme

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
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=hourly_trend, x='hr', y='cnt', marker='o', ax=ax)
    ax.set_title('Average Rentals by Hour of Day')
    ax.set_xlabel('Hour (24-hour format)')
    ax.set_ylabel('Average Number of Rentals')
    ax.grid(True)
    st.pyplot(fig)

with tab2:
    st.header("Daily Rental Patterns")
    
    # Map weekday numbers to names
    weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 
                   4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    
    # Daily pattern
    daily_trend = date_filtered_df.groupby('weekday')['cnt'].mean().reset_index()
    daily_trend['weekday_name'] = daily_trend['weekday'].map(weekday_map)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Daily rentals
    sns.barplot(data=daily_trend, x='weekday_name', y='cnt', ax=ax1)
    ax1.set_title('Average Rentals by Day of Week')
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Average Number of Rentals')
    plt.xticks(rotation=45)
    
    # User type comparison
    daily_user_trend = date_filtered_df.groupby('weekday')[['casual', 'registered']].mean().reset_index()
    daily_user_trend['weekday_name'] = daily_user_trend['weekday'].map(weekday_map)
    
    daily_user_trend_melted = pd.melt(daily_user_trend, 
                                     id_vars=['weekday_name'],
                                     value_vars=['casual', 'registered'],
                                     var_name='user_type',
                                     value_name='rentals')
    
    sns.barplot(data=daily_user_trend_melted, 
                x='weekday_name', 
                y='rentals',
                hue='user_type',
                ax=ax2)
    ax2.set_title('Casual vs Registered Users by Day')
    ax2.set_xlabel('Day of Week')
    ax2.set_ylabel('Average Number of Rentals')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    st.header("Monthly Rental Patterns")
    
    # Map month numbers to names
    month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    monthly_trend = date_filtered_df.groupby('mnth')['cnt'].mean().reset_index()
    monthly_trend['month_name'] = monthly_trend['mnth'].map(month_map)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_trend, x='month_name', y='cnt', marker='o')
    ax.set_title('Average Monthly Rentals Throughout the Year')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Number of Rentals')
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

with tab4:
    st.header("Yearly Rental Trends")
    
    # Calculate yearly statistics
    yearly_trend = date_filtered_df.groupby('yr')['cnt'].agg(['mean', 'sum']).reset_index()
    yearly_trend['yr'] = yearly_trend['yr'].map({0: '2011', 1: '2012'})
    
    # Year over year growth
    yoy_growth = ((yearly_trend['sum'].iloc[1] - yearly_trend['sum'].iloc[0]) / 
                  yearly_trend['sum'].iloc[0] * 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=yearly_trend, x='yr', y='sum')
        ax.set_title('Total Rentals by Year')
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Rentals')
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.pointplot(data=yearly_trend, x='yr', y='mean')
        ax.set_title('Average Daily Rentals by Year')
        ax.set_xlabel('Year')
        ax.set_ylabel('Average Rentals')
        st.pyplot(fig)
    
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
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Recency Distribution
    sns.histplot(data=rfm_df, x='recency', bins=30, ax=axes[0])
    axes[0].set_title('Days Since Last Rental')
    axes[0].set_xlabel('Days')
    axes[0].set_ylabel('Number of Customers')
    
    # Frequency Distribution
    sns.histplot(data=rfm_df, x='frequency', bins=30, ax=axes[1])
    axes[1].set_title('Number of Rentals per Customer')
    axes[1].set_xlabel('Number of Rentals')
    axes[1].set_ylabel('Number of Customers')
    
    # Total Rentals Distribution
    sns.histplot(data=rfm_df, x='total_rentals', bins=30, ax=axes[2])
    axes[2].set_title('Total Rentals by Customer')
    axes[2].set_xlabel('Total Rentals')
    axes[2].set_ylabel('Number of Customers')
    
    plt.tight_layout()
    st.pyplot(fig)

# Overall patterns summary
st.markdown("---")
st.header("Summary of Rental Patterns")
st.write("""
- **Hourly Pattern**: Shows typical daily usage cycles with peaks during commute hours
- **Daily Pattern**: Highlights differences between weekday and weekend usage
- **Monthly Pattern**: Reveals seasonal trends in bike rental behavior
- **Yearly Trend**: Demonstrates overall growth in bike rental usage from 2011 to 2012
""")
