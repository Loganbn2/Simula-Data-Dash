#!/usr/bin/env python3
"""
Simple CSV upload script (run AFTER disabling RLS in Supabase)
"""

import pandas as pd
import os
from supabase_client import SupabaseClient
from datetime import datetime, timezone
import uuid
import re

def clean_timestamp(timestamp_str):
    """Clean and validate timestamp string"""
    if pd.isna(timestamp_str):
        return datetime.now(timezone.utc).isoformat()
    
    try:
        # Try to parse the timestamp and convert to proper format
        timestamp_str = str(timestamp_str).strip()
        
        # Handle timezone offset issues (like +16, +18, +19)
        # Replace invalid timezone offsets with +00 (UTC)
        timestamp_str = re.sub(r'\+\d{2}$', '+00', timestamp_str)
        
        # Parse and reformat
        dt = pd.to_datetime(timestamp_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
        
    except Exception as e:
        print(f"⚠️  Invalid timestamp '{timestamp_str}', using current time")
        return datetime.now(timezone.utc).isoformat()

def upload_csv_simple():
    """Simple CSV upload (requires RLS to be disabled first)"""
    
    csv_file_path = "/Users/loganbn2/Downloads/Chat Data - Sheet2.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return False
    
    # Initialize Supabase client
    try:
        supabase_client = SupabaseClient()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
        print(f"✅ Loaded CSV file with {len(df)} records")
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return False
    
    # Process the data
    processed_records = []
    
    for _, row in df.iterrows():
        try:
            # Convert the row to a dictionary, excluding the 'id' column to let database generate UUIDs
            record = {
                'user_message': str(row.get('user_message', '')),
                'assistant_message': str(row.get('assistant_message', '')),
                'device_type': str(row.get('device_type', 'Web Browser')),
                'country': str(row.get('country', 'United States')),
                'user_sentiment': str(row.get('user_sentiment', 'Neutral')),
                'ad_message': str(row.get('ad_message', '')),
                'ad_clicked': bool(row.get('ad_clicked', False)) if str(row.get('ad_clicked', '')).upper() != 'FALSE' else False,
                'ad_category': str(row.get('ad_category', '')),
                'conversation_category': str(row.get('conversation_category', 'General Information')),
                'timestamp': clean_timestamp(row.get('timestamp')),
                'created_at': clean_timestamp(row.get('created_at'))
            }
            
            # Clean up any NaN values
            for key, value in record.items():
                if pd.isna(value) or str(value).lower() == 'nan':
                    if key in ['ad_clicked']:
                        record[key] = False
                    elif key in ['timestamp', 'created_at']:
                        record[key] = datetime.now(timezone.utc).isoformat()
                    else:
                        record[key] = ''
            
            processed_records.append(record)
            
        except Exception as e:
            print(f"⚠️  Error processing row {len(processed_records) + 1}: {e}")
            continue
    
    print(f"✅ Processed {len(processed_records)} records for upload")
    
    # Insert data in smaller batches
    batch_size = 50
    successful_inserts = 0
    failed_inserts = 0
    
    for i in range(0, len(processed_records), batch_size):
        batch = processed_records[i:i + batch_size]
        
        try:
            # Insert batch into Supabase (let database generate UUIDs)
            result = supabase_client.client.table('chat_logs').insert(batch).execute()
            successful_inserts += len(batch)
            print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} records")
            
        except Exception as e:
            print(f"❌ Failed to insert batch {i//batch_size + 1}: {e}")
            failed_inserts += len(batch)
    
    print(f"\n📊 Upload Summary:")
    print(f"✅ Successfully inserted: {successful_inserts} records")
    print(f"❌ Failed to insert: {failed_inserts} records")
    if len(processed_records) > 0:
        print(f"📈 Success rate: {(successful_inserts / len(processed_records) * 100):.1f}%")
    
    return successful_inserts > 0

def main():
    """Main function"""
    print("🚀 Starting simple CSV upload to Supabase...")
    print("⚠️  IMPORTANT: Make sure you have disabled RLS first by running STEP1_DISABLE_RLS.sql")
    print()
    
    success = upload_csv_simple()
    
    if success:
        print("\n🎉 Upload completed successfully!")
        print("📌 IMPORTANT: Now run STEP2_ENABLE_RLS.sql to re-enable security")
        print("💡 You can refresh your dashboard to see the new data")
    else:
        print("\n💥 Upload failed. Please check the errors above.")
        print("💡 Make sure you ran STEP1_DISABLE_RLS.sql first")

if __name__ == "__main__":
    main()
