import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Supabase client
try:
    from supabase_client import SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.warning("⚠️ Supabase client not available")

def load_data_from_supabase():
    """Load data from Supabase"""
    if not SUPABASE_AVAILABLE:
        return pd.DataFrame()
    
    try:
        # Initialize Supabase client
        supabase_client = SupabaseClient()
        
        # Query data from chat_logs table
        response = supabase_client.client.table('chat_logs').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        else:
            st.warning("No data found in Supabase")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Failed to load data from Supabase: {e}")
        return pd.DataFrame()

def create_basic_analytics(df):
    """Create basic analytics visualizations"""
    if df.empty:
        st.warning("No data available for analytics")
        return
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conversations", len(df))
    
    with col2:
        if 'ad_clicked' in df.columns:
            click_rate = (df['ad_clicked'].sum() / len(df) * 100) if len(df) > 0 else 0
            st.metric("Ad Click Rate", f"{click_rate:.1f}%")
        else:
            st.metric("Ad Click Rate", "N/A")
    
    with col3:
        if 'device_type' in df.columns:
            mobile_pct = (df['device_type'].value_counts().get('Mobile', 0) / len(df) * 100) if len(df) > 0 else 0
            st.metric("Mobile Users", f"{mobile_pct:.1f}%")
        else:
            st.metric("Mobile Users", "N/A")
    
    with col4:
        if 'user_sentiment' in df.columns:
            positive_pct = (df['user_sentiment'].value_counts().get('Positive', 0) / len(df) * 100) if len(df) > 0 else 0
            st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
        else:
            st.metric("Positive Sentiment", "N/A")
    
    # Conversation categories chart
    if 'conversation_category' in df.columns:
        st.subheader("📊 Conversation Categories")
        category_counts = df['conversation_category'].value_counts()
        
        fig = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="Conversation Categories Distribution",
            labels={'x': 'Category', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Device type pie chart
    if 'device_type' in df.columns:
        st.subheader("📱 Device Type Distribution")
        device_counts = df['device_type'].value_counts()
        
        fig = px.pie(
            values=device_counts.values,
            names=device_counts.index,
            title="Device Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment analysis
    if 'user_sentiment' in df.columns:
        st.subheader("😊 Sentiment Analysis")
        sentiment_counts = df['user_sentiment'].value_counts()
        
        colors = {'Positive': '#2E8B57', 'Neutral': '#FFD700', 'Negative': '#DC143C'}
        color_map = [colors.get(sentiment, '#1f77b4') for sentiment in sentiment_counts.index]
        
        fig = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            title="User Sentiment Distribution",
            labels={'x': 'Sentiment', 'y': 'Count'},
            color=sentiment_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main Streamlit application"""
    
    # Configure the page
    st.set_page_config(
        page_title="AI Chat Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🚀 AI Chat Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # Check environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            st.success("✅ Supabase configured")
        else:
            st.error("❌ Supabase not configured")
            st.markdown("**Missing environment variables:**")
            if not supabase_url:
                st.write("- SUPABASE_URL")
            if not supabase_key:
                st.write("- SUPABASE_ANON_KEY")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.markdown("---")
        st.info("Data refreshes automatically every 60 seconds")
    
    # Load data
    with st.spinner("Loading data from Supabase..."):
        df = load_data_from_supabase()
    
    if not df.empty:
        st.success(f"✅ Loaded {len(df)} records from Supabase")
        
        # Create analytics
        create_basic_analytics(df)
        
        # Show recent data sample
        st.subheader("📋 Recent Data Sample")
        display_columns = ['user_message', 'assistant_message', 'device_type', 'country', 'user_sentiment', 'conversation_category']
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            st.dataframe(df[available_columns].head(10), use_container_width=True)
        else:
            st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("No data available. Please check your Supabase connection and data.")
    
    # Footer
    st.markdown("---")
    st.markdown("🎯 **Simula Data Dashboard** - Connected to live Supabase data!")

if __name__ == "__main__":
    main()
