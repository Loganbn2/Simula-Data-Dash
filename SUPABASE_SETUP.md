# Supabase Setup Guide

This guide will help you set up Supabase as the backend database for your AI Chat Analytics Dashboard.

## Prerequisites

1. A Supabase account (sign up at [supabase.com](https://supabase.com))
2. Python environment with the required packages installed

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose your organization
4. Fill in your project details:
   - **Name**: `ai-chat-analytics` (or any name you prefer)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose the region closest to you
5. Click "Create new project"
6. Wait for the project to be ready (usually takes 1-2 minutes)

## Step 2: Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** > **API**
2. Copy the following values:
   - **Project URL** (something like `https://abcdefgh.supabase.co`)
   - **Anon (public) key** (starts with `eyJ...`)

## Step 3: Set Up the Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Create a new query
3. Copy and paste the entire content from `supabase_schema.sql` file
4. Click **Run** to execute the schema
5. You should see success messages for all the tables, functions, and sample data

## Step 4: Configure Environment Variables

1. Open your `.env` file in the project directory
2. Update the Supabase configuration:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Replace the values with your actual Project URL and Anon key from Step 2.

## Step 5: Install Dependencies

Make sure you have the Supabase client installed:

```bash
pip install -r requirements.txt
```

## Step 6: Test the Connection

1. Run the Supabase client test:

```bash
python supabase_client.py
```

You should see:
```
✅ Supabase connection successful!
✅ Migrated X sample conversations
✅ Retrieved X records from database
```

## Step 7: Run the Dashboard

```bash
streamlit run dashboard.py
```

You should now see:
- 🟢 Connected to Supabase (green indicator)
- A new "Process Raw Conversation" section for adding data
- All existing functionality working with Supabase backend

## Database Schema Overview

The setup creates the following tables:

### `conversations`
- Stores raw conversation data in JSONB format
- Each record contains the original `{"id": "...", "messages": [...]}` structure

### `chat_logs`
- Processed analytics data extracted from conversations
- Contains fields for sentiment analysis, categorization, ad data, etc.
- Optimized for dashboard queries and analytics

### Key Functions

- `process_conversation()`: Converts raw conversations to analytics data
- `get_analytics_data()`: Filtered data retrieval for dashboard
- Sample data generation and basic sentiment/categorization logic

## Adding Your Own Data

### Single Conversation
Use the "Process Raw Conversation" section in the dashboard to paste JSON data:

```json
{
  "id": "unique-conversation-id",
  "messages": [
    {
      "content": "Your user question here",
      "role": "user"
    },
    {
      "content": "Assistant response here", 
      "role": "assistant"
    }
  ]
}
```

### Bulk Upload
Create a JSON file with an array of conversations and upload via the dashboard.

## Troubleshooting

### Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check that your Supabase project is active
- Ensure you have internet connectivity

### Schema Issues
- Make sure you ran the entire `supabase_schema.sql` file
- Check the Supabase SQL Editor for any error messages
- Verify all tables were created in the **Table Editor**

### Data Issues
- Check that RLS (Row Level Security) policies allow your operations
- Verify the raw conversation format matches the expected structure
- Look at the Supabase logs for detailed error messages

## Security Notes

- The current setup uses Row Level Security (RLS) with permissive policies for demo purposes
- For production use, implement proper authentication and more restrictive RLS policies
- Consider using Supabase Auth for user management
- Keep your database credentials secure and never commit them to version control

## Advanced Configuration

### Custom Processing Logic
Edit the `process_conversation()` function in the SQL schema to customize:
- Sentiment analysis logic
- Categorization rules
- Additional data extraction

### API Integration
The dashboard can integrate with external APIs for:
- Advanced sentiment analysis (e.g., Google Cloud Natural Language API)
- Content categorization (e.g., OpenAI's classification API)
- Geographic data enrichment

### Monitoring
- Use Supabase's built-in monitoring for database performance
- Set up alerts for high query volumes
- Monitor storage usage as your data grows
