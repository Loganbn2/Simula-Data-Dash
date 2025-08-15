# AI Chat Analytics Dashboard with Supabase

A comprehensive analytics dashboard for AI chat conversations with sentiment analysis, ad performance tracking, and AI-powered insights. Now with **Supabase** backend support for scalable, real-time data management.

## 🚀 Quick Start

### Option 1: SQLite (Local Development)
```bash
# Clone and setup
git clone <repository-url>
cd Simula-Data-Dash
pip install -r requirements.txt

# Run with sample data
streamlit run dashboard.py
```

### Option 2: Supabase (Production Ready)
```bash
# 1. Set up Supabase (see detailed guide below)
# 2. Configure environment
cp .env.example .env  # Add your Supabase credentials

# 3. Test and setup
python setup_supabase.py --setup

# 4. Run dashboard
streamlit run dashboard.py
```

## 🏗️ Database Architecture

### Raw Data Format
The system expects conversations in this JSON format:
```json
{
  "id": "20f84baa-bd75-41d2-a793-8eca12e238d3",
  "messages": [
    {
      "content": "is that postgresql array declaration correct? declare a uuid[] := Array['a1092a64-159f-45fa-a64a-d15f7e61693a']",
      "role": "user"
    },
    {
      "content": "The declaration in PostgreSQL is not correct due to the use of `:=` which is typically used for variable assignment in PL/pgSQL...",
      "role": "assistant"
    }
  ]
}
```

### Processed Analytics Schema
Each conversation is processed into structured analytics data:

| Field | Type | Description |
|-------|------|-------------|
| `user_message` | TEXT | Original user message |
| `assistant_message` | TEXT | AI assistant response |
| `device_type` | VARCHAR(100) | User's device type |
| `country` | VARCHAR(100) | User's country/location |
| `user_sentiment` | VARCHAR(20) | Positive/Neutral/Negative |
| `ad_message` | TEXT | Displayed advertisement |
| `ad_clicked` | BOOLEAN | Whether user clicked the ad |
| `ad_category` | VARCHAR(100) | Advertisement category |
| `conversation_category` | VARCHAR(100) | Topic/category of conversation |
| `timestamp` | TIMESTAMP | When the conversation occurred |

## 🗄️ Supabase Setup

### Prerequisites
1. [Supabase](https://supabase.com) account
2. Python 3.8+ environment

### Step-by-Step Setup

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project: `ai-chat-analytics`
   - Note your Project URL and Anon Key

2. **Set Up Database Schema**
   - Open Supabase SQL Editor
   - Copy-paste content from `supabase_schema.sql`
   - Execute the schema

3. **Configure Environment**
   ```bash
   # Update .env file
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
   ```

4. **Test and Initialize**
   ```bash
   python setup_supabase.py --setup
   ```

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions.

## 📊 Features

### Core Analytics
- **Sentiment Analysis**: Real-time sentiment tracking across conversations
- **Category Classification**: Automatic conversation topic categorization  
- **Ad Performance**: Click-through rates and campaign analytics
- **Geographic Insights**: Location-based user behavior analysis
- **Device Analytics**: Cross-platform usage patterns

### AI-Powered Insights
- **Natural Language Queries**: Ask questions about your data in plain English
- **Automated Analysis**: AI-generated insights and recommendations
- **Trend Detection**: Identify patterns and anomalies in conversation data

### Data Management
- **Raw Conversation Processing**: Direct input from chat logs
- **Bulk Import**: CSV/JSON file uploads
- **Real-time Updates**: Live data refresh and filtering
- **Export Capabilities**: Download filtered datasets

## 🛠️ Management Commands

### Connection Testing
```bash
python setup_supabase.py --test
```

### Data Migration
```bash
# Generate sample data
python setup_supabase.py --migrate-sample 100

# Import from SQLite
python setup_supabase.py --migrate-sqlite chat_analytics.db

# Process JSON file
python setup_supabase.py --process-json conversations.json
```

### Data Analysis
```bash
# View data summary
python setup_supabase.py --summary
```

## 📁 Project Structure

```
Simula-Data-Dash/
├── dashboard.py              # Main Streamlit application
├── supabase_client.py        # Supabase database client
├── setup_supabase.py         # Setup and migration utility
├── analytics.py              # Visualization components
├── ai_insights.py            # AI-powered analysis
├── data_generator.py         # Sample data generation
├── supabase_schema.sql       # Database schema
├── SUPABASE_SETUP.md         # Detailed setup guide
└── requirements.txt          # Python dependencies
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# AI Services (Optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Supabase (Required for production)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# Fallback Database
DATABASE_URL=sqlite:///chat_analytics.db
```

### Dashboard Configuration
The app automatically:
- ✅ Connects to Supabase if configured
- ⚠️ Falls back to SQLite for local development
- 🔄 Generates sample data if no data exists

## 💡 Usage Examples

### Adding Single Conversation
Use the dashboard's "Process Raw Conversation" section:
```json
{
  "id": "conv-001",
  "messages": [
    {"content": "How do I reset my password?", "role": "user"},
    {"content": "I can help you reset your password...", "role": "assistant"}
  ]
}
```

### Bulk Data Import
Create a JSON file with conversation array:
```json
[
  {"id": "conv-001", "messages": [...]},
  {"id": "conv-002", "messages": [...]},
  ...
]
```

Upload via dashboard or command line:
```bash
python setup_supabase.py --process-json bulk_conversations.json
```

### AI Insights Queries
Ask natural language questions in the dashboard:
- "What are the most common user complaints?"
- "Show me sentiment trends over the last week"
- "Which ad categories perform best?"

## 🔍 Analytics Capabilities

### Filtering & Search
- **Text Search**: Search across user messages, responses, and ads
- **Sentiment Filter**: Filter by positive/neutral/negative sentiment
- **Category Filter**: Focus on specific conversation topics
- **Location Filter**: Analyze by geographic regions
- **Device Filter**: Compare performance across devices
- **Time Range**: Date-based filtering

### Visualizations
- **Category Distribution**: Bar charts of conversation topics
- **CTR Analysis**: Ad performance by category
- **Sentiment Trends**: Time-series sentiment analysis
- **Geographic Heat Maps**: Location-based user activity
- **Device Usage**: Cross-platform analytics

## 🚨 Troubleshooting

### Common Issues

**Supabase Connection Failed**
- Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env
- Check Supabase project is active
- Ensure schema was properly executed

**No Data Visible**
- Run `python setup_supabase.py --migrate-sample 50`
- Check RLS policies in Supabase dashboard
- Verify data was inserted: `python setup_supabase.py --summary`

**Import Errors**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Verify JSON format for conversation imports

### Performance Optimization
- Use database indexes on frequently filtered columns
- Limit large queries with pagination
- Consider data archiving for old conversations

## 🔐 Security

### Production Deployment
- **Environment Variables**: Never commit credentials to version control
- **RLS Policies**: Configure appropriate Row Level Security in Supabase
- **API Keys**: Rotate keys regularly and use least-privilege access
- **HTTPS**: Always use encrypted connections in production

### Data Privacy
- **PII Handling**: Implement data masking for sensitive information
- **Retention**: Set up automatic data cleanup policies
- **Audit Logs**: Monitor database access and modifications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Test with both SQLite and Supabase backends
4. Submit pull request with comprehensive description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Analyzing! 📊✨**

For detailed setup instructions, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
