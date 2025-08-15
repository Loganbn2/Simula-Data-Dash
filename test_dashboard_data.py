#!/usr/bin/env python3
"""
Test script to verify dashboard data display
"""

from supabase_client import SupabaseClient
import pandas as pd

def test_data_display():
    print("🔄 Testing dashboard data display...")
    
    try:
        # Initialize client
        client = SupabaseClient()
        
        # Get data as dashboard would
        df = client.get_all_analytics_data()
        
        print(f"📊 Total records: {len(df)}")
        print(f"📊 Columns: {df.columns.tolist()}")
        
        # Check required columns for dashboard
        required_cols = ['user_message', 'model_response', 'user_sentiment', 
                        'message_category', 'user_location', 'user_device', 'ad_clicked']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
        else:
            print("✅ All required columns present")
        
        # Show sample data
        if len(df) > 0:
            print("\n📋 Sample records:")
            for i, row in df.head(3).iterrows():
                print(f"\nRecord {i+1}:")
                print(f"  User Message: {str(row['user_message'])[:60]}...")
                print(f"  Model Response: {str(row['model_response'])[:60]}...")
                print(f"  Sentiment: {row['user_sentiment']}")
                print(f"  Category: {row['message_category']}")
                print(f"  Location: {row['user_location']}")
                print(f"  Device: {row['user_device']}")
                print(f"  Ad Clicked: {row['ad_clicked']}")
        
        # Check filter data
        print("\n📊 Filter options:")
        print(f"  Sentiments: {df['user_sentiment'].unique().tolist()}")
        print(f"  Categories: {df['message_category'].unique().tolist()}")
        print(f"  Locations: {df['user_location'].unique().tolist()}")
        print(f"  Devices: {df['user_device'].unique().tolist()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_data_display()
