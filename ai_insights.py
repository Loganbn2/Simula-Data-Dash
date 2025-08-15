import pandas as pd
import numpy as np
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIInsights:
    def __init__(self):
        """Initialize AI Insights with API configuration."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.use_openai = bool(self.openai_api_key)
        self.use_anthropic = bool(self.anthropic_api_key)
        
        # Initialize clients if API keys are available
        if self.use_openai:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            except (ImportError, TypeError, Exception) as e:
                self.use_openai = False
                print(f"OpenAI client initialization failed: {e}")
                print("AI insights will use fallback mode")
        
        if self.use_anthropic:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            except (ImportError, TypeError, Exception) as e:
                self.use_anthropic = False
                print(f"Anthropic client initialization failed: {e}")
                print("AI insights will use fallback mode")
    
    def get_data_summary(self, df: pd.DataFrame) -> str:
        """Generate a comprehensive data summary for context."""
        if df.empty:
            return "No data available for analysis."
        
        summary = f"""
        Data Summary:
        - Total records: {len(df):,}
        - Date range: {df.get('timestamp', pd.Series()).min()} to {df.get('timestamp', pd.Series()).max()}
        - Unique categories: {df['message_category'].nunique()}
        - Unique locations: {df['user_location'].nunique()}
        - Unique devices: {df['user_device'].nunique()}
        
        Sentiment Distribution:
        {df['user_sentiment'].value_counts().to_string()}
        
        Top 5 Categories:
        {df['message_category'].value_counts().head().to_string()}
        
        Top 5 Locations:
        {df['user_location'].value_counts().head().to_string()}
        
        Ad Performance:
        - Overall CTR: {(df['ad_clicked'].sum() / len(df) * 100):.2f}%
        - Total clicks: {df['ad_clicked'].sum():,}
        - Total impressions: {len(df):,}
        
        Top Ad Categories by CTR:
        """
        
        # Calculate CTR by ad category
        ad_stats = df.groupby('ad_category').agg({
            'ad_clicked': ['sum', 'count']
        })
        ad_stats.columns = ['clicks', 'impressions']
        ad_stats['ctr'] = (ad_stats['clicks'] / ad_stats['impressions'] * 100).round(2)
        ad_stats = ad_stats.sort_values('ctr', ascending=False).head()
        
        summary += ad_stats.to_string()
        
        return summary
    
    def get_insight_with_openai(self, data_summary: str, user_query: str) -> str:
        """Get insights using OpenAI API."""
        system_prompt = """You are a data analyst expert specializing in AI chat analytics and ad performance. 
        You analyze chat logs with sentiment analysis, user behavior, and advertisement click-through rates.
        
        Your task is to provide clear, actionable insights based on the data provided. 
        Focus on:
        - Sentiment patterns and what they reveal
        - User behavior trends
        - Ad performance and optimization opportunities
        - Category-specific insights
        - Geographic and device-based patterns
        
        Keep responses concise, insightful, and actionable. Use data to support your conclusions."""
        
        user_prompt = f"""
        Here's the current dataset summary:
        {data_summary}
        
        User question: {user_query}
        
        Please provide insights based on this data. Be specific and include relevant numbers when possible.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting insights from OpenAI: {str(e)}"
    
    def get_insight_with_anthropic(self, data_summary: str, user_query: str) -> str:
        """Get insights using Anthropic Claude API."""
        prompt = f"""Human: You are a data analyst expert specializing in AI chat analytics and ad performance. 
        You analyze chat logs with sentiment analysis, user behavior, and advertisement click-through rates.
        
        Here's the current dataset summary:
        {data_summary}
        
        User question: {user_query}
        
        Please provide clear, actionable insights based on this data. Focus on:
        - Sentiment patterns and what they reveal
        - User behavior trends  
        - Ad performance and optimization opportunities
        - Category-specific insights
        - Geographic and device-based patterns
        
        Keep responses concise, insightful, and actionable. Use data to support your conclusions.

        Assistant: """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error getting insights from Anthropic: {str(e)}"
    
    def get_fallback_insight(self, df: pd.DataFrame, user_query: str) -> str:
        """Generate basic insights without AI APIs."""
        if df.empty:
            return "No data available for analysis."
        
        query_lower = user_query.lower()
        
        # Sentiment analysis
        if any(word in query_lower for word in ['sentiment', 'mood', 'feeling', 'emotion']):
            sentiment_dist = df['user_sentiment'].value_counts(normalize=True) * 100
            sentiment_text = ", ".join([f"{idx}: {val:.1f}%" for idx, val in sentiment_dist.items()])
            
            insight = f"**Sentiment Analysis:** {sentiment_text}. "
            
            if sentiment_dist.get('Negative', 0) > 30:
                insight += "High negative sentiment suggests areas for improvement in user experience."
            elif sentiment_dist.get('Positive', 0) > 50:
                insight += "Strong positive sentiment indicates good user satisfaction."
            
            return insight
        
        # Category analysis
        if any(word in query_lower for word in ['category', 'topic', 'use case', 'common']):
            top_categories = df['message_category'].value_counts().head()
            categories_text = ", ".join([f"{idx} ({val} messages)" for idx, val in top_categories.items()])
            
            return f"**Top Categories:** {categories_text}. The most common use case is {top_categories.index[0]} with {top_categories.iloc[0]} messages."
        
        # CTR analysis
        if any(word in query_lower for word in ['ctr', 'click', 'ad', 'performance', 'conversion']):
            overall_ctr = (df['ad_clicked'].sum() / len(df) * 100)
            
            # CTR by sentiment
            ctr_by_sentiment = df.groupby('user_sentiment')['ad_clicked'].mean() * 100
            
            insight = f"**Overall CTR:** {overall_ctr:.2f}%. "
            insight += f"CTR by sentiment: {', '.join([f'{idx}: {val:.1f}%' for idx, val in ctr_by_sentiment.items()])}. "
            
            if ctr_by_sentiment.get('Positive', 0) > overall_ctr * 1.5:
                insight += "Positive sentiment users are significantly more likely to click ads."
            
            return insight
        
        # Location analysis
        if any(word in query_lower for word in ['location', 'geographic', 'region', 'city']):
            top_locations = df['user_location'].value_counts().head()
            locations_text = ", ".join([f"{idx} ({val})" for idx, val in top_locations.items()])
            
            return f"**Top Locations:** {locations_text}. {top_locations.index[0]} has the highest activity with {top_locations.iloc[0]} interactions."
        
        # Device analysis
        if any(word in query_lower for word in ['device', 'mobile', 'desktop', 'platform']):
            device_dist = df['user_device'].value_counts().head()
            device_text = ", ".join([f"{idx} ({val})" for idx, val in device_dist.items()])
            
            mobile_devices = df[df['user_device'].str.contains('iPhone|iPad|Samsung|Android', case=False, na=False)]
            mobile_percentage = len(mobile_devices) / len(df) * 100
            
            return f"**Device Distribution:** {device_text}. Mobile devices account for {mobile_percentage:.1f}% of interactions."
        
        # Trend analysis
        if any(word in query_lower for word in ['trend', 'pattern', 'time', 'when']):
            if 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                peak_hour = df['hour'].value_counts().index[0]
                return f"**Usage Patterns:** Peak activity occurs at {peak_hour}:00. Most interactions happen during business hours."
            else:
                return "**Usage Patterns:** Time-based analysis not available without timestamp data."
        
        # General overview
        return f"""
        **Data Overview:** 
        - Total interactions: {len(df):,}
        - Most common category: {df['message_category'].mode()[0]} ({df['message_category'].value_counts().iloc[0]} occurrences)
        - Overall sentiment: {df['user_sentiment'].mode()[0]} (most common)
        - Overall CTR: {(df['ad_clicked'].sum() / len(df) * 100):.2f}%
        - Top location: {df['user_location'].mode()[0]}
        - Top device: {df['user_device'].mode()[0]}
        """
    
    def get_insight(self, df: pd.DataFrame, user_query: str) -> str:
        """Main method to get insights - tries AI APIs first, falls back to rule-based."""
        data_summary = self.get_data_summary(df)
        
        # Try OpenAI first
        if self.use_openai:
            try:
                return self.get_insight_with_openai(data_summary, user_query)
            except Exception as e:
                print(f"OpenAI failed: {e}")
        
        # Try Anthropic as fallback
        if self.use_anthropic:
            try:
                return self.get_insight_with_anthropic(data_summary, user_query)
            except Exception as e:
                print(f"Anthropic failed: {e}")
        
        # Use rule-based fallback
        return self.get_fallback_insight(df, user_query)
    
    def get_suggested_questions(self, df: pd.DataFrame) -> list:
        """Generate suggested questions based on the data."""
        suggestions = [
            "What are the top use cases for our AI chat?",
            "How does sentiment vary across different categories?",
            "Which ad categories have the highest CTR?",
            "What are the geographic patterns in user behavior?",
            "How does device type affect ad click rates?",
            "What time of day has the highest engagement?",
            "Which message categories generate the most negative sentiment?",
            "How can we improve ad performance?",
            "What are the trending topics in user messages?",
            "Which locations show the highest conversion rates?"
        ]
        
        # Customize suggestions based on data patterns
        if not df.empty:
            # If high negative sentiment, suggest optimization questions
            if (df['user_sentiment'] == 'Negative').mean() > 0.3:
                suggestions.insert(0, "Why is there high negative sentiment and how can we improve it?")
            
            # If low CTR, suggest ad optimization questions
            if (df['ad_clicked'].mean() * 100) < 5:
                suggestions.insert(1, "How can we improve our low click-through rates?")
        
        return suggestions

# Example usage
if __name__ == "__main__":
    # Test with sample data
    insights = AIInsights()
    
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'user_sentiment': ['Positive', 'Negative', 'Neutral'] * 100,
        'message_category': ['Technical Support', 'Product Inquiry', 'Billing'] * 100,
        'ad_clicked': [True, False, False] * 100,
        'user_location': ['New York, NY', 'Los Angeles, CA'] * 150,
        'user_device': ['iPhone', 'Android', 'Desktop'] * 100,
        'ad_category': ['Software Tools', 'Cloud Services'] * 150
    })
    
    test_query = "What are the top use cases?"
    result = insights.get_insight(sample_data, test_query)
    print("Insight:", result)
