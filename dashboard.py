import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import AnalyticsVisualizer
from data_generator import DataGenerator
from ai_insights import AIInsights
from supabase_client import SupabaseClient, DataMigration
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Chat Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007acc;
    }
    .stDataFrame {
        border: 1px solid #e1e5e9;
        border-radius: 0.5rem;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    div.stButton > button {
        background-color: #007acc;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    div.stButton > button:hover {
        background-color: #005a9e;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
    }
    
    /* Hide anchor link buttons that appear on hover */
    .stMarkdown h1 .anchor-link,
    .stMarkdown h2 .anchor-link,
    .stMarkdown h3 .anchor-link,
    .stMarkdown h4 .anchor-link,
    .stMarkdown h5 .anchor-link,
    .stMarkdown h6 .anchor-link,
    .element-container .anchor-link,
    .stTitle .anchor-link,
    .stSubheader .anchor-link,
    .stHeader .anchor-link,
    a.anchor-link {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    /* Hide anchor links in headers */
    h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"], 
    h4 a[href^="#"], h5 a[href^="#"], h6 a[href^="#"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Remove hover effects that show anchor links */
    h1:hover a[href^="#"], h2:hover a[href^="#"], h3:hover a[href^="#"],
    h4:hover a[href^="#"], h5:hover a[href^="#"], h6:hover a[href^="#"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide all anchor elements that start with # */
    a[href^="#"] {
        display: none !important;
    }
    
    /* Custom width for pagination controls */
    div[data-testid="stNumberInput"] {
        width: 150px !important;
        max-width: 150px !important;
    }
    
    div[data-testid="stNumberInput"] > div {
        width: 150px !important;
        max-width: 150px !important;
    }
    
    div[data-testid="stNumberInput"] input {
        width: 150px !important;
        max-width: 150px !important;
        min-width: 150px !important;
    }
    
    div[data-testid="stSelectbox"] {
        width: 100px !important;
        max-width: 100px !important;
    }
    
    div[data-testid="stSelectbox"] > div {
        width: 100px !important;
        max-width: 100px !important;
    }
    
    div[data-testid="stSelectbox"] select {
        width: 100px !important;
        max-width: 100px !important;
        min-width: 100px !important;
    }
    
    /* More specific targeting for number input */
    div[data-testid="stNumberInput"] > div > div > input {
        width: 150px !important;
        max-width: 150px !important;
        min-width: 150px !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading data...")
def load_data(cache_key=None):
    """Load data from Supabase database or generate sample data if not configured."""
    try:
        # Try to initialize Supabase client
        supabase_client = SupabaseClient()
        
        if supabase_client.test_connection():
            # Load data from Supabase
            data = supabase_client.get_all_analytics_data()
            
            if data.empty:
                # If no data exists, migrate some sample data
                st.info("No data found in Supabase. Generating sample data...")
                migration = DataMigration(supabase_client)
                migrated = migration.migrate_sample_data(100)
                
                if migrated > 0:
                    data = supabase_client.get_all_analytics_data()
                    st.success(f"✅ Generated and loaded {migrated} sample conversations!")
                else:
                    st.error("Failed to generate sample data")
                    return pd.DataFrame()
            
            return data
            
    except Exception as e:
        st.warning(f"Supabase connection failed: {str(e)}")
        st.info("Falling back to SQLite database...")
        
        # Fallback to SQLite if Supabase is not configured
        return load_sqlite_data()

@st.cache_data
def load_sqlite_data():
    """Fallback method to load data from SQLite database."""
    db_path = Path("chat_analytics.db")
    
    if not db_path.exists():
        # Generate sample data if database doesn't exist
        generator = DataGenerator()
        data = generator.generate_sample_data(1000)  # Generate 1000 sample records
        
        # Save to database
        conn = sqlite3.connect(db_path)
        data.to_sql('chat_logs', conn, if_exists='replace', index=False)
        conn.close()
        
        st.info("Generated sample SQLite data for demo purposes")
        return data
    else:
        # Load from database
        conn = sqlite3.connect(db_path)
        data = pd.read_sql_query("SELECT * FROM chat_logs", conn)
        conn.close()
        return data

@st.cache_data
def filter_data(df, filters):
    """Apply filters to the dataframe."""
    filtered_df = df.copy()
    
    # Text search
    if filters.get('search_text'):
        search_text = filters['search_text'].lower()
        text_mask = (
            filtered_df['user_message'].str.lower().str.contains(search_text, na=False)
        )
        
        # Check if model_response column exists, if not use assistant_message
        response_col = 'model_response' if 'model_response' in filtered_df.columns else 'assistant_message'
        if response_col in filtered_df.columns:
            text_mask |= filtered_df[response_col].str.lower().str.contains(search_text, na=False)
        
        # Check if ad_message column exists
        if 'ad_message' in filtered_df.columns:
            text_mask |= filtered_df['ad_message'].str.lower().str.contains(search_text, na=False)
        
        filtered_df = filtered_df[text_mask]
    
    # Sentiment filter
    if filters.get('sentiment') and 'All' not in filters['sentiment']:
        filtered_df = filtered_df[filtered_df['user_sentiment'].isin(filters['sentiment'])]
    
    # Category filter
    if filters.get('category') and 'All' not in filters['category']:
        filtered_df = filtered_df[filtered_df['message_category'].isin(filters['category'])]
    
    # Location filter
    if filters.get('location') and 'All' not in filters['location']:
        filtered_df = filtered_df[filtered_df['user_location'].isin(filters['location'])]
    
    # Device filter
    if filters.get('device') and 'All' not in filters['device']:
        # Check if user_device column exists, if not use device_type
        device_col = 'user_device' if 'user_device' in filtered_df.columns else 'device_type'
        if device_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[device_col].isin(filters['device'])]
    
    # Ad clicked filter
    if filters.get('ad_clicked') != 'All':
        clicked_value = True if filters['ad_clicked'] == 'Yes' else False
        filtered_df = filtered_df[filtered_df['ad_clicked'] == clicked_value]
    
    return filtered_df

def create_summary_metrics(df):
    """Create summary metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #007acc;">Total Records</h3>
            <h2 style="margin: 0; color: #333;">{:,}</h2>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        avg_ctr = (df['ad_clicked'].sum() / len(df) * 100) if len(df) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #007acc;">Avg CTR</h3>
            <h2 style="margin: 0; color: #333;">{:.2f}%</h2>
        </div>
        """.format(avg_ctr), unsafe_allow_html=True)
    
    with col3:
        positive_sentiment = (df['user_sentiment'] == 'Positive').sum() / len(df) * 100 if len(df) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #007acc;">Positive Sentiment</h3>
            <h2 style="margin: 0; color: #333;">{:.1f}%</h2>
        </div>
        """.format(positive_sentiment), unsafe_allow_html=True)
    
    with col4:
        unique_categories = df['message_category'].nunique() if len(df) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #007acc;">Categories</h3>
            <h2 style="margin: 0; color: #333;">{}</h2>
        </div>
        """.format(unique_categories), unsafe_allow_html=True)

def main():
    # Header
    st.title("AI Chat Analytics Dashboard")
    st.markdown("Interactive dashboard for exploring AI chat logs with sentiment analysis and ad performance metrics.")
    
    # Initialize session state
    if 'data' not in st.session_state:
        with st.spinner('Loading data...'):
            st.session_state.data = load_data()
    
    if 'ai_insights' not in st.session_state:
        st.session_state.ai_insights = AIInsights()
    
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = AnalyticsVisualizer()
    
    # Try to initialize Supabase client
    supabase_client = None
    try:
        supabase_client = SupabaseClient()
        if not supabase_client.test_connection():
            supabase_client = None
    except:
        supabase_client = None
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Search box
    search_text = st.sidebar.text_input("Search in messages:", placeholder="Enter search terms...")
    
    # Filter options
    sentiment_options = ['All'] + list(st.session_state.data['user_sentiment'].unique())
    selected_sentiment = st.sidebar.multiselect("Sentiment:", sentiment_options, default=['All'])
    
    category_options = ['All'] + list(st.session_state.data['message_category'].unique())
    selected_category = st.sidebar.multiselect("Category:", category_options, default=['All'])
    
    location_options = ['All'] + list(st.session_state.data['user_location'].unique())
    selected_location = st.sidebar.multiselect("Location:", location_options, default=['All'])
    
    # Handle device column name differences
    device_col = 'user_device' if 'user_device' in st.session_state.data.columns else 'device_type'
    device_options = ['All'] + list(st.session_state.data[device_col].unique())
    selected_device = st.sidebar.multiselect("Device:", device_options, default=['All'])
    
    ad_clicked_filter = st.sidebar.selectbox("Ad Clicked:", ['All', 'Yes', 'No'])
    
    # Apply filters
    filters = {
        'search_text': search_text,
        'sentiment': selected_sentiment,
        'category': selected_category,
        'location': selected_location,
        'device': selected_device,
        'ad_clicked': ad_clicked_filter
    }
    
    filtered_data = filter_data(st.session_state.data, filters)
    
    # Clear filters button
    if st.sidebar.button("Clear All Filters"):
        st.rerun()
    
    # Export button
    if st.sidebar.button("Export Filtered Data"):
        csv = filtered_data.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"chat_analytics_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Main content layout
    
    # AI Insights Panel at the top
    st.subheader("AI Insights")
    
    # Suggested queries - chatbot style
    st.markdown("**💬 Suggested questions:**")
    
    # Arrange buttons close together with optimal widths for single-line text
    col1, col2, col3, col4 = st.columns([0.8, 0.7, 0.75, 0.5], gap="small")
    
    with col1:
        if st.button("What is the click rate for ai game ads on mobile?", key="query1", help="Click to see AI games performance"):
            st.session_state.selected_answer = "query1"
    
    with col2:
        if st.button("How do users feel about XBox vs Playstation?", key="query2", help="Click to see sentiment analysis"):
            st.session_state.selected_answer = "query2"
    
    with col3:
        if st.button("How many users are using AI for online shopping?", key="query3", help="Click to see AI shopping usage"):
            st.session_state.selected_answer = "query3"
    
    # col4 is left empty to push everything to the left
    
    # Query input
    user_query = st.text_area(
        "Or ask your own question:",
        placeholder="e.g., 'What are the top use cases?' or 'Show sentiment trends'",
        height=80
    )
    
    if st.button("Get Insights", type="primary"):
        # Button is disabled - no functionality
        pass
    
    # Single container for all answers
    if 'selected_answer' in st.session_state:
        if st.session_state.selected_answer == "query1":
            st.markdown("""
            <div class="insight-box">
                <h4>🎮 AI Game Ads Click Rate</h4>
                <p>The click rate for <strong>AI Game ads on mobile devices</strong> is <strong>3.4%</strong>, which is significantly higher than the desktop click rate of 1.8%.</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.selected_answer == "query2":
            st.markdown("""
            <div class="insight-box">
                <h4>💭 Xbox vs PlayStation Sentiment</h4>
                <p>User sentiment shows <strong>PlayStation discussions</strong> have <strong>72% positive sentiment</strong> compared to Xbox at 65%. However, Xbox users show more engagement with <strong>2.1x longer conversation</strong> threads.</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.selected_answer == "query3":
            st.markdown("""
            <div class="insight-box">
                <h4>🛒 AI Shopping Usage</h4>
                <p><strong>4.2% of user queries</strong> are using AI for online shopping assistance, with peak usage during <strong>evening hours</strong>.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Analytics cards
    st.subheader("Analytics Overview")
    
    # Create analytics charts in a grid
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        # Top categories
        if not filtered_data.empty:
            top_categories = filtered_data['message_category'].value_counts().head(10).reset_index()
            top_categories.columns = ['category', 'count']
            fig_categories = st.session_state.visualizer.create_category_chart(
                top_categories, "Top Message Categories"
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        
    with chart_col2:
        # Top ad categories by CTR
        if not filtered_data.empty:
            ad_stats = filtered_data.groupby('ad_category').agg({
                'ad_clicked': ['sum', 'count']
            }).round(2)
            ad_stats.columns = ['clicks', 'impressions']
            # Avoid division by zero in CTR calculation
            ad_stats['ctr'] = 0.0  # Default to 0
            mask = ad_stats['impressions'] > 0  # Only calculate CTR where impressions > 0
            ad_stats.loc[mask, 'ctr'] = (ad_stats.loc[mask, 'clicks'] / ad_stats.loc[mask, 'impressions'] * 100).round(2)
            ad_stats = ad_stats.reset_index()
            ad_stats = ad_stats.nlargest(10, 'ctr')
            
            if not ad_stats.empty:
                fig_ctr = st.session_state.visualizer.create_ctr_chart(
                    ad_stats, "Top Ad Categories by CTR"
                )
                st.plotly_chart(fig_ctr, use_container_width=True)
    
    with chart_col3:
        # Top ad categories by impressions
        if not filtered_data.empty:
            ad_impressions = filtered_data['ad_category'].value_counts().head(10).reset_index()
            ad_impressions.columns = ['ad_category', 'impressions']
            fig_impressions = st.session_state.visualizer.create_category_chart(
                ad_impressions, "Top Ad Categories by Impressions"
            )
            st.plotly_chart(fig_impressions, use_container_width=True)
    
    # Additional analytics - consolidated into one row
    st.subheader("Additional Analytics")
    
    additional_col1, additional_col2, additional_col3 = st.columns(3)
    
    with additional_col1:
        if not filtered_data.empty:
            fig_sentiment = st.session_state.visualizer.create_sentiment_distribution(filtered_data, "Sentiment Distribution")
            st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with additional_col2:
        if not filtered_data.empty:
            fig_devices = st.session_state.visualizer.create_device_distribution(filtered_data, "Device Distribution")
            st.plotly_chart(fig_devices, use_container_width=True)
    
    with additional_col3:
        if not filtered_data.empty:
            fig_locations = st.session_state.visualizer.create_location_map(filtered_data, "Location Distribution")
            st.plotly_chart(fig_locations, use_container_width=True)
    
    # Data table
    st.subheader("Chat Logs Data")
    
    # Prepare display data (always show full text)
    display_data = filtered_data.copy()
    
    # Format boolean column
    display_data['ad_clicked'] = display_data['ad_clicked'].map({True: 'Yes', False: 'No'})
    
    # Column order and renaming - handle both old and new column names
    response_col = 'model_response' if 'model_response' in display_data.columns else 'assistant_message'
    device_col = 'user_device' if 'user_device' in display_data.columns else 'device_type'
    
    column_mapping = {
        'user_message': 'User Message',
        response_col: 'Model Response',
        'user_sentiment': 'User Sentiment',
        'ad_message': 'Ad Message',
        'ad_clicked': 'Ad Clicked?',
        'message_category': 'Message Category',
        'user_location': 'User Location',
        device_col: 'User Device'
    }
    
    # Only include columns that actually exist in the data
    available_columns = [col for col in column_mapping.keys() if col in display_data.columns]
    display_data = display_data[available_columns].rename(columns=column_mapping)
    
    # Pagination
    total_records = len(display_data)
    
    # Initialize records per page in session state
    if 'records_per_page' not in st.session_state:
        st.session_state.records_per_page = 50
    
    records_per_page = st.session_state.records_per_page
    total_pages = (total_records - 1) // records_per_page + 1
    
    # Display table
    if not display_data.empty:
        # Initialize pagination variables
        current_page = 1
        
        # Check if we have session state for current page
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        current_page = st.session_state.current_page
        
        # Ensure current page is within valid range
        if current_page > total_pages:
            current_page = total_pages
            st.session_state.current_page = current_page
        
        start_idx = (current_page - 1) * records_per_page
        end_idx = min(start_idx + records_per_page, total_records)
        
        page_data = display_data.iloc[start_idx:end_idx]
        st.dataframe(
            page_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Bottom controls - smaller and left-aligned
        if total_pages > 1:
            bottom_col1, bottom_col2, bottom_col3 = st.columns([0.8, 1.2, 4])
            with bottom_col1:
                new_page = st.number_input(
                    "Page:",
                    min_value=1,
                    max_value=total_pages,
                    value=current_page,
                    key="page_selector_final"
                )
                # Update session state when page changes
                if new_page != current_page:
                    st.session_state.current_page = new_page
                    st.rerun()
            with bottom_col2:
                new_records_per_page = st.selectbox(
                    "Per page:",
                    [25, 50, 100, 200],
                    index=[25, 50, 100, 200].index(records_per_page),
                    key="records_per_page_selector"
                )
                # Update session state when records per page changes
                if new_records_per_page != records_per_page:
                    st.session_state.records_per_page = new_records_per_page
                    st.session_state.current_page = 1  # Reset to first page
                    st.rerun()
        else:
            # Single page but still show records per page selector
            bottom_col1, bottom_col2 = st.columns([1.2, 4.8])
            with bottom_col1:
                new_records_per_page = st.selectbox(
                    "Per page:",
                    [25, 50, 100, 200],
                    index=[25, 50, 100, 200].index(records_per_page),
                    key="records_per_page_single"
                )
                # Update session state when records per page changes
                if new_records_per_page != records_per_page:
                    st.session_state.records_per_page = new_records_per_page
                    st.rerun()
        
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_records} records")
    else:
        st.info("No data matches the current filters.")

if __name__ == "__main__":
    main()
