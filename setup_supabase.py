#!/usr/bin/env python3
"""
Migration and setup utility for AI Chat Analytics Dashboard with Supabase
"""

import os
import sys
import json
import argparse
from pathlib import Path
from supabase_client import SupabaseClient, DataMigration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection."""
    print("🔄 Testing Supabase connection...")
    
    try:
        client = SupabaseClient()
        
        if client.test_connection():
            print("✅ Supabase connection successful!")
            return client
        else:
            print("❌ Supabase connection failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        print("\nPlease ensure:")
        print("1. Your Supabase project is set up")
        print("2. You've run the SQL schema (supabase_schema.sql)")
        print("3. SUPABASE_URL and SUPABASE_ANON_KEY are set in your .env file")
        return None

def migrate_sample_data(client, num_records=50):
    """Generate and migrate sample data."""
    print(f"🔄 Generating {num_records} sample conversations...")
    
    migration = DataMigration(client)
    migrated = migration.migrate_sample_data(num_records)
    
    if migrated > 0:
        print(f"✅ Successfully migrated {migrated} conversations!")
        return True
    else:
        print("❌ Failed to migrate sample data")
        return False

def migrate_sqlite_data(client, sqlite_path="chat_analytics.db"):
    """Migrate existing SQLite data to Supabase."""
    if not Path(sqlite_path).exists():
        print(f"❌ SQLite database not found at {sqlite_path}")
        return False
    
    print(f"🔄 Migrating data from {sqlite_path}...")
    
    migration = DataMigration(client)
    migrated = migration.migrate_existing_sqlite_data(sqlite_path)
    
    if migrated > 0:
        print(f"✅ Successfully migrated {migrated} conversations from SQLite!")
        return True
    else:
        print("❌ Failed to migrate SQLite data")
        return False

def process_json_file(client, file_path):
    """Process conversations from a JSON or JSONL file."""
    if not Path(file_path).exists():
        print(f"❌ File not found at {file_path}")
        return False
    
    print(f"🔄 Processing conversations from {file_path}...")
    
    try:
        conversations = []
        
        # Handle JSONL format (one JSON object per line)
        if file_path.endswith('.jsonl'):
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            data = json.loads(line)
                            conversations.append(data)
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Skipping invalid JSON on line {line_num}: {e}")
        else:
            # Handle regular JSON format
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Ensure data is a list
            if isinstance(data, dict):
                conversations = [data]
            else:
                conversations = data
        
        # Validate conversation format
        valid_conversations = []
        for conv in conversations:
            if isinstance(conv, dict) and 'id' in conv and 'messages' in conv:
                valid_conversations.append(conv)
            else:
                print(f"⚠️  Skipping invalid conversation format: {conv}")
        
        if not valid_conversations:
            print("❌ No valid conversations found in the file")
            return False
        
        print(f"📊 Found {len(valid_conversations)} valid conversations")
        
        # Process conversations
        result = client.insert_conversations(valid_conversations)
        
        if result['successful_conversations'] > 0:
            print(f"✅ Successfully processed {result['successful_conversations']}/{len(valid_conversations)} conversations!")
            print(f"📈 Total messages inserted: {result['total_messages']}")
            return True
        else:
            print("❌ Failed to process conversations")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return False

def show_data_summary(client):
    """Show summary of data in Supabase."""
    print("🔄 Fetching data summary...")
    
    try:
        df = client.get_all_analytics_data()
        
        if df.empty:
            print("📊 No data found in database")
            return
        
        print(f"📊 Data Summary:")
        print(f"   Total records: {len(df)}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Unique categories: {df['message_category'].nunique()}")
        print(f"   Unique locations: {df['user_location'].nunique()}")
        print(f"   Overall CTR: {(df['ad_clicked'].sum() / len(df) * 100):.2f}%")
        
        print(f"\n   Sentiment distribution:")
        sentiment_dist = df['user_sentiment'].value_counts()
        for sentiment, count in sentiment_dist.items():
            percentage = (count / len(df) * 100)
            print(f"     {sentiment}: {count} ({percentage:.1f}%)")
        
        print(f"\n   Top 5 categories:")
        top_categories = df['message_category'].value_counts().head()
        for category, count in top_categories.items():
            percentage = (count / len(df) * 100)
            print(f"     {category}: {count} ({percentage:.1f}%)")
    
    except Exception as e:
        print(f"❌ Error fetching data summary: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Supabase setup and migration utility")
    parser.add_argument('--test', action='store_true', help='Test Supabase connection')
    parser.add_argument('--migrate-sample', type=int, metavar='N', help='Generate N sample conversations')
    parser.add_argument('--migrate-sqlite', metavar='PATH', help='Migrate SQLite database to Supabase')
    parser.add_argument('--process-json', metavar='PATH', help='Process conversations from JSON or JSONL file')
    parser.add_argument('--summary', action='store_true', help='Show data summary')
    parser.add_argument('--setup', action='store_true', help='Full setup: test connection and add sample data')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Test connection first
    client = test_connection()
    if not client:
        return
    
    # Execute requested operations
    if args.setup:
        print("\n🚀 Running full setup...")
        migrate_sample_data(client, 50)
        show_data_summary(client)
        print("\n✅ Setup complete! You can now run: streamlit run dashboard.py")
    
    if args.test:
        print("\n✅ Connection test completed successfully!")
    
    if args.migrate_sample:
        migrate_sample_data(client, args.migrate_sample)
    
    if args.migrate_sqlite:
        migrate_sqlite_data(client, args.migrate_sqlite)
    
    if args.process_json:
        process_json_file(client, args.process_json)
    
    if args.summary:
        show_data_summary(client)

if __name__ == "__main__":
    main()
