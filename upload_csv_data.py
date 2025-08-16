#!/usr/bin/env python3
"""
Script to upload CSV data to Supabase chat_logs table
"""

import pandas as pd
import os
from supabase_client import SupabaseClient
from datetime import datetime, timezone
import uuid
import re

def clean_uuid(uuid_str):
    """Clean and validate UUID string"""
    if pd.isna(uuid_str):
        return str(uuid.uuid4())
    
    # Remove any extra characters and ensure proper format
    cleaned = str(uuid_str).strip()
    
    # Check if it's a valid UUID format (36 characters with dashes)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    if re.match(uuid_pattern, cleaned, re.IGNORECASE):
        return cleaned
    else:
        # If invalid, generate a new UUID
        print(f"⚠️  Invalid UUID '{cleaned}', generating new one")
        return str(uuid.uuid4())

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

def upload_csv_to_supabase(csv_file_path):
    """Upload CSV data to Supabase chat_logs table"""
    
    # Initialize Supabase client
    try:
        supabase_client = SupabaseClient()
        print("✅ Connected to Supabase")
        
        # Temporarily disable RLS for data insertion
        try:
            supabase_client.client.postgrest.session.headers.update({
                'Authorization': f'Bearer {supabase_client.supabase_key}'
            })
            print("✅ Set authorization headers for bulk insert")
        except Exception as e:
            print(f"⚠️  Could not set auth headers: {e}")
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
        print(f"✅ Loaded CSV file with {len(df)} records")
        print(f"📊 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return False
    
    # Process the data to match the expected schema
    processed_records = []
    
    for _, row in df.iterrows():
        try:
            # Convert the row to a dictionary and handle the data
            record = {
                'id': clean_uuid(row.get('id')),  # Clean the UUID
                'user_message': str(row.get('user_message', '')),
                'assistant_message': str(row.get('assistant_message', '')),
                'device_type': str(row.get('device_type', 'Web Browser')),
                'country': str(row.get('country', 'United States')),
                'user_sentiment': str(row.get('user_sentiment', 'Neutral')),
                'ad_message': str(row.get('ad_message', '')),
                'ad_clicked': bool(row.get('ad_clicked', False)),
                'ad_category': str(row.get('ad_category', '')),
                'conversation_category': str(row.get('conversation_category', 'General Information')),
                'timestamp': clean_timestamp(row.get('timestamp')),  # Clean timestamps
                'created_at': clean_timestamp(row.get('created_at'))  # Clean timestamps
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
    
    # Insert data in batches to avoid hitting size limits
    batch_size = 100
    successful_inserts = 0
    failed_inserts = 0
    
    for i in range(0, len(processed_records), batch_size):
        batch = processed_records[i:i + batch_size]
        
        try:
            # Insert batch into Supabase
            result = supabase_client.client.table('chat_logs').insert(batch).execute()
            successful_inserts += len(batch)
            print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} records")
            
        except Exception as e:
            print(f"❌ Failed to insert batch {i//batch_size + 1}: {e}")
            failed_inserts += len(batch)
    
    print(f"\n📊 Upload Summary:")
    print(f"✅ Successfully inserted: {successful_inserts} records")
    print(f"❌ Failed to insert: {failed_inserts} records")
    print(f"📈 Success rate: {(successful_inserts / len(processed_records) * 100):.1f}%")
    
    return successful_inserts > 0

def main():
    """Main function to upload CSV data"""
    csv_file_path = "/Users/loganbn2/Downloads/Chat Data - Sheet2.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return
    
    print("🚀 Starting CSV upload to Supabase...")
    print(f"📁 CSV file: {csv_file_path}")
    
    success = upload_csv_to_supabase(csv_file_path)
    
    if success:
        print("\n🎉 Upload completed successfully!")
        print("💡 You can now refresh your dashboard to see the new data")
    else:
        print("\n💥 Upload failed. Please check the errors above.")

if __name__ == "__main__":
    main()
