"""
Supabase client for AI Chat Analytics Dashboard
Handles database operations with Supabase PostgreSQL database
"""

import os
import json
import pandas as pd
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
        
        if not self.supabase_url.startswith('https://'):
            raise ValueError("Invalid SUPABASE_URL format. Should start with 'https://'")
        
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            print(f"✅ Supabase client initialized successfully")
            self.test_connection()
        except Exception as e:
            print(f"❌ Error initializing Supabase client: {e}")
            raise
    
    def test_connection(self):
        """Test the connection to Supabase"""
        try:
            # Try a simple query to test connection
            result = self.client.table('chat_logs').select('count').limit(1).execute()
            print(f"✅ Connection test successful")
            return True
        except Exception as e:
            print(f"⚠️  Connection test failed (this is expected if tables don't exist yet): {e}")
            return False

    def process_raw_conversation(self, conversation_data: Dict) -> List[Dict]:
        """
        Process raw conversation JSON into structured chat_logs records
        
        Input format: {"id": "...", "messages": [{"content": "...", "role": "..."}]}
        Output: Records for the chat_logs table with user_message/assistant_message columns
        """
        if 'id' not in conversation_data or 'messages' not in conversation_data:
            raise ValueError("Invalid conversation format. Expected {'id': '...', 'messages': [...]}")
        
        conversation_id = conversation_data['id']
        messages = conversation_data['messages']
        
        # Group messages by conversation pairs (user + assistant)
        processed_records = []
        
        i = 0
        while i < len(messages):
            user_message = None
            assistant_message = None
            
            # Look for user message
            if i < len(messages) and messages[i].get('role') == 'user':
                user_message = messages[i].get('content', '')
                i += 1
            
            # Look for assistant message
            if i < len(messages) and messages[i].get('role') == 'assistant':
                assistant_message = messages[i].get('content', '')
                i += 1
            
            # Only create a record if we have both user and assistant messages
            if user_message and assistant_message:
                # Extract analytics data
                sentiment = self._analyze_sentiment(user_message)
                category = self._categorize_conversation(user_message)
                
                record = {
                    'user_message': user_message,
                    'assistant_message': assistant_message,
                    'device_type': 'Web Browser',  # Default value
                    'country': 'United States',    # Default value
                    'user_sentiment': sentiment,
                    'ad_message': 'Try our premium AI assistant for advanced features!',
                    'ad_clicked': False,  # Default value
                    'ad_category': 'AI Tools',
                    'conversation_category': category,
                    'timestamp': messages[i-2].get('timestamp', datetime.utcnow().isoformat()) if i >= 2 else datetime.utcnow().isoformat()
                }
                
                processed_records.append(record)
            else:
                # Skip incomplete pairs
                i += 1
        
        return processed_records
    
    def _categorize_conversation(self, text: str) -> str:
        """Categorize conversation based on content"""
        text_lower = text.lower()
        
        # Technical/Programming related
        if any(keyword in text_lower for keyword in ['error', 'bug', 'problem', 'issue', 'debug']):
            return 'Technical Support'
        elif any(keyword in text_lower for keyword in ['price', 'cost', 'billing', 'payment', 'subscription']):
            return 'Billing Question'
        elif any(keyword in text_lower for keyword in ['api', 'integration', 'code', 'programming', 'function', 'variable']):
            return 'API Questions'
        elif any(keyword in text_lower for keyword in ['database', 'sql', 'query', 'postgresql', 'mysql']):
            return 'Database Questions'
        elif any(keyword in text_lower for keyword in ['how', 'what', 'help', 'explain', 'tutorial']):
            return 'General Information'
        else:
            return 'General Information'
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis - returns capitalized format for database"""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'amazing', 'wonderful', 'fantastic', 'awesome', 'brilliant', 'help', 'thanks', 'thank you']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating', 'annoying', 'difficult', 'problem', 'error', 'fail']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return 'Positive'
        elif negative_score > positive_score:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract basic topics/keywords from text"""
        tech_keywords = {
            'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'matplotlib', 'pyplot'],
            'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'node'],
            'database': ['database', 'sql', 'postgresql', 'mysql', 'mongodb', 'supabase'],
            'ai': ['ai', 'machine learning', 'ml', 'neural network', 'deep learning'],
            'web': ['html', 'css', 'frontend', 'backend', 'api', 'rest'],
            'data': ['data', 'analytics', 'visualization', 'chart', 'graph'],
            'education': ['teach', 'learn', 'school', 'student', 'class', 'education'],
            'writing': ['write', 'essay', 'introduction', 'story', 'content']
        }
        
        text_lower = text.lower()
        topics = []
        
        for category, keywords in tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(category)
        
        return topics
    
    def insert_conversations(self, conversations: List[Dict]) -> Dict:
        """
        Insert multiple conversations into the database
        Returns summary of insertion results
        """
        total_messages = 0
        successful_conversations = 0
        failed_conversations = 0
        
        for conversation in conversations:
            try:
                records = self.process_raw_conversation(conversation)
                
                # Insert all records for this conversation
                result = self.client.table('chat_logs').insert(records).execute()
                
                total_messages += len(records)
                successful_conversations += 1
                print(f"✅ Processed conversation {conversation['id']}: {len(records)} messages")
                
            except Exception as e:
                print(f"❌ Failed to process conversation {conversation.get('id', 'unknown')}: {e}")
                failed_conversations += 1
        
        return {
            'successful_conversations': successful_conversations,
            'failed_conversations': failed_conversations,
            'total_messages': total_messages
        }
    
    def insert_bulk_conversations(self, conversations: List[Dict]) -> int:
        """
        Insert multiple conversations in bulk
        Returns the number of successfully processed conversations
        """
        return self.insert_conversations(conversations)['successful_conversations']

    def get_summary_stats(self):
        """Get basic stats from the database"""
        try:
            # Simple test query
            result = self.client.table('chat_logs').select('*').limit(5).execute()
            return {'status': 'connected', 'sample_count': len(result.data)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_all_analytics_data(self) -> pd.DataFrame:
        """
        Fetch all analytics data from the chat_logs table
        Returns a pandas DataFrame with all conversation data
        """
        try:
            # Fetch all data from chat_logs table with pagination to handle Supabase's row limits
            all_data = []
            page_size = 1000  # Supabase default max is 1000
            offset = 0
            
            print(f"🔄 Fetching data from Supabase in chunks of {page_size}...")
            
            while True:
                # Fetch data in chunks using range
                result = self.client.table('chat_logs').select('*').range(offset, offset + page_size - 1).execute()
                
                if not result.data:
                    print(f"📊 Finished loading. No more data at offset {offset}")
                    break
                
                current_batch = len(result.data)
                all_data.extend(result.data)
                print(f"📊 Loaded batch: {current_batch} records (total so far: {len(all_data)})")
                
                # If we got no data, we've reached the end
                if current_batch == 0:
                    print(f"📊 Reached end of data (got 0 records)")
                    break
                
                offset += current_batch  # Use actual batch size, not page_size
                
                # Safety check to prevent infinite loops
                if len(all_data) > 50000:  # Reasonable upper limit
                    print(f"⚠️  Reached safety limit of 50,000 records")
                    break
            
            if not all_data:
                return pd.DataFrame()
            
            print(f"✅ Successfully loaded {len(all_data)} total records from Supabase")
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(all_data)
            
            # Ensure timestamp column is properly formatted
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Map database columns to expected analytics columns
            column_mapping = {
                'user_sentiment': 'user_sentiment',
                'conversation_category': 'message_category', 
                'country': 'user_location',
                'ad_clicked': 'ad_clicked',
                'timestamp': 'timestamp',
                'assistant_message': 'model_response',
                'device_type': 'user_device'
            }
            
            # Rename columns to match expected format
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and old_col != new_col:
                    df = df.rename(columns={old_col: new_col})
            
            # Ensure required columns exist with defaults if missing
            required_columns = ['user_sentiment', 'message_category', 'user_location', 'ad_clicked', 'timestamp', 'model_response', 'user_device']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'user_sentiment':
                        df[col] = 'Neutral'
                    elif col == 'message_category':
                        df[col] = 'General Information'
                    elif col == 'user_location':
                        df[col] = 'United States'
                    elif col == 'ad_clicked':
                        df[col] = False
                    elif col == 'timestamp':
                        df[col] = datetime.utcnow()
                    elif col == 'model_response':
                        df[col] = df.get('assistant_message', 'No response')
                    elif col == 'user_device':
                        df[col] = df.get('device_type', 'Web Browser')
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching analytics data: {str(e)}")
            return pd.DataFrame()

class DataMigration:
    """Utility class for data migration and testing"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
    
    def create_sample_conversations(self, count: int = 5) -> List[Dict]:
        """Create sample conversation data for testing"""
        sample_conversations = []
        
        for i in range(count):
            conversation = {
                'id': str(uuid.uuid4()),
                'messages': [
                    {
                        'role': 'user',
                        'content': f'Hello, I need help with Python data analysis project #{i+1}. Can you help me visualize data using matplotlib?',
                        'timestamp': (datetime.utcnow() - timedelta(hours=i*2)).isoformat()
                    },
                    {
                        'role': 'assistant', 
                        'content': f'I\'d be happy to help you with your Python data analysis project! Here\'s a simple example using matplotlib:\n\n```python\nimport matplotlib.pyplot as plt\nimport pandas as pd\n\n# Sample code for project {i+1}\nplt.figure(figsize=(10, 6))\nplt.plot([1, 2, 3, 4], [1, 4, 2, 3])\nplt.show()\n```\n\nThis creates a basic line plot. What specific type of visualization do you need?',
                        'timestamp': (datetime.utcnow() - timedelta(hours=i*2, minutes=5)).isoformat()
                    },
                    {
                        'role': 'user',
                        'content': f'Great! That\'s exactly what I needed for project {i+1}. Thank you so much!',
                        'timestamp': (datetime.utcnow() - timedelta(hours=i*2, minutes=10)).isoformat()
                    }
                ]
            }
            sample_conversations.append(conversation)
        
        return sample_conversations
    
    def migrate_sample_data(self, count: int = 5) -> int:
        """Create and insert sample data"""
        print(f"📊 Creating {count} sample conversations...")
        
        try:
            # Create sample conversations
            sample_conversations = self.create_sample_conversations(count)
            
            # Insert them using the client
            result = self.client.insert_conversations(sample_conversations)
            
            return result['successful_conversations']
            
        except Exception as e:
            print(f"❌ Error migrating sample data: {str(e)}")
            return 0
    
    def migrate_existing_sqlite_data(self, sqlite_path: str) -> int:
        """Migrate data from existing SQLite database"""
        try:
            import sqlite3
            
            # Connect to SQLite database
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            
            # Check if the expected tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            
            if 'chat_logs' not in tables:
                print("❌ No 'chat_logs' table found in SQLite database")
                conn.close()
                return 0
            
            # Fetch all data from SQLite
            cursor.execute("SELECT * FROM chat_logs")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(chat_logs)")
            columns = [column[1] for column in cursor.fetchall()]
            
            conn.close()
            
            if not rows:
                print("📊 No data found in SQLite database")
                return 0
            
            # Convert SQLite data to records
            records = []
            for row in rows:
                record = dict(zip(columns, row))
                records.append(record)
            
            # Insert records into Supabase
            result = self.client.client.table('chat_logs').insert(records).execute()
            
            print(f"✅ Migrated {len(records)} records from SQLite")
            return len(records)
            
        except Exception as e:
            print(f"❌ Error migrating SQLite data: {str(e)}")
            return 0
