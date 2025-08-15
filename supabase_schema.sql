-- Supabase Schema for AI Chat Analytics Dashboard
-- Simplified schema with direct chat_logs table

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create chat_logs table for analytics
CREATE TABLE chat_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    device_type VARCHAR(100),
    country VARCHAR(100),
    user_sentiment VARCHAR(20) CHECK (user_sentiment IN ('Positive', 'Neutral', 'Negative')),
    ad_message TEXT,
    ad_clicked BOOLEAN DEFAULT FALSE,
    ad_category VARCHAR(100),
    conversation_category VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_chat_logs_timestamp ON chat_logs(timestamp);
CREATE INDEX idx_chat_logs_sentiment ON chat_logs(user_sentiment);
CREATE INDEX idx_chat_logs_category ON chat_logs(conversation_category);
CREATE INDEX idx_chat_logs_country ON chat_logs(country);
CREATE INDEX idx_chat_logs_device ON chat_logs(device_type);
CREATE INDEX idx_chat_logs_ad_clicked ON chat_logs(ad_clicked);
CREATE INDEX idx_chat_logs_ad_category ON chat_logs(ad_category);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a function to process raw conversation data into analytics format
CREATE OR REPLACE FUNCTION process_conversation(conv_data JSONB)
RETURNS UUID AS $$
DECLARE
    new_record_id UUID;
    user_msg TEXT;
    assistant_msg TEXT;
    processed_category VARCHAR(100);
    processed_sentiment VARCHAR(20);
    processed_device VARCHAR(100);
    processed_country VARCHAR(100);
BEGIN
    -- Extract messages (assuming first is user, second is assistant)
    SELECT conv_data->'messages'->0->>'content' INTO user_msg;
    SELECT conv_data->'messages'->1->>'content' INTO assistant_msg;
    
    -- Basic categorization logic (can be enhanced with AI/ML)
    processed_category := CASE 
        WHEN LOWER(user_msg) LIKE '%error%' OR LOWER(user_msg) LIKE '%bug%' OR LOWER(user_msg) LIKE '%problem%' THEN 'Technical Support'
        WHEN LOWER(user_msg) LIKE '%price%' OR LOWER(user_msg) LIKE '%cost%' OR LOWER(user_msg) LIKE '%billing%' THEN 'Billing Question'
        WHEN LOWER(user_msg) LIKE '%how%' OR LOWER(user_msg) LIKE '%what%' OR LOWER(user_msg) LIKE '%help%' THEN 'General Information'
        WHEN LOWER(user_msg) LIKE '%api%' OR LOWER(user_msg) LIKE '%integration%' OR LOWER(user_msg) LIKE '%code%' THEN 'API Questions'
        ELSE 'General Information'
    END;
    
    -- Basic sentiment analysis (can be enhanced with AI/ML)
    processed_sentiment := CASE 
        WHEN LOWER(user_msg) LIKE '%great%' OR LOWER(user_msg) LIKE '%good%' OR LOWER(user_msg) LIKE '%excellent%' OR LOWER(user_msg) LIKE '%thanks%' THEN 'Positive'
        WHEN LOWER(user_msg) LIKE '%bad%' OR LOWER(user_msg) LIKE '%terrible%' OR LOWER(user_msg) LIKE '%awful%' OR LOWER(user_msg) LIKE '%hate%' THEN 'Negative'
        ELSE 'Neutral'
    END;
    
    -- Default device and country (would be enhanced with real user data)
    processed_device := 'Web Browser';
    processed_country := 'United States';
    
    -- Insert processed data directly into chat_logs
    INSERT INTO chat_logs (
        user_message,
        assistant_message,
        device_type,
        country,
        user_sentiment,
        ad_message,
        ad_clicked,
        ad_category,
        conversation_category
    ) VALUES (
        user_msg,
        assistant_msg,
        processed_device,
        processed_country,
        processed_sentiment,
        'Try our premium AI assistant for advanced features!',
        FALSE,
        'AI Tools',
        processed_category
    ) RETURNING id INTO new_record_id;
    
    RETURN new_record_id;
END;
$$ LANGUAGE plpgsql;

-- Create a view for analytics queries
CREATE VIEW chat_analytics_summary AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    conversation_category,
    user_sentiment,
    country,
    device_type,
    ad_category,
    COUNT(*) as message_count,
    COUNT(CASE WHEN ad_clicked THEN 1 END) as ad_clicks,
    ROUND(
        COUNT(CASE WHEN ad_clicked THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 
        2
    ) as ctr_percentage
FROM chat_logs
GROUP BY 
    DATE_TRUNC('day', timestamp),
    conversation_category,
    user_sentiment,
    country,
    device_type,
    ad_category;

-- Insert sample data function
CREATE OR REPLACE FUNCTION insert_sample_data()
RETURNS VOID AS $$
DECLARE
    sample_conversations JSONB[] := ARRAY[
        '{"id": "20f84baa-bd75-41d2-a793-8eca12e238d3", "messages": [{"content": "is that postgresql array declaration correct? declare a uuid[] := Array[''a1092a64-159f-45fa-a64a-d15f7e61693a'']", "role": "user"}, {"content": "The declaration in PostgreSQL is not correct due to the use of `:=` which is typically used for variable assignment in PL/pgSQL, not for array declarations directly. Instead, it should be written as `DECLARE my_uuids uuid[] := ARRAY[''a1092a64-159f-45fa-a64a-d15f7e61693a''];` if you are within a PL/pgSQL function or block. The `ARRAY` constructor should also be used instead of `Array`.", "role": "assistant"}]}',
        '{"id": "30f84baa-bd75-41d2-a793-8eca12e238d4", "messages": [{"content": "How do I optimize database queries for better performance?", "role": "user"}, {"content": "Here are key strategies for optimizing database queries: 1) Use proper indexing on frequently queried columns, 2) Avoid SELECT *, 3) Use LIMIT when appropriate, 4) Optimize JOIN operations, 5) Use query execution plans to identify bottlenecks.", "role": "assistant"}]}',
        '{"id": "40f84baa-bd75-41d2-a793-8eca12e238d5", "messages": [{"content": "What are the best practices for API design?", "role": "user"}, {"content": "Best practices for API design include: 1) Use RESTful principles, 2) Implement proper HTTP status codes, 3) Version your APIs, 4) Use consistent naming conventions, 5) Implement proper authentication and authorization, 6) Provide comprehensive documentation, 7) Handle errors gracefully.", "role": "assistant"}]}'
    ];
    conv_data JSONB;
BEGIN
    FOREACH conv_data IN ARRAY sample_conversations
    LOOP
        PERFORM process_conversation(conv_data);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS) for better security
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your authentication needs)
CREATE POLICY "Enable read access for all users" ON chat_logs FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON chat_logs FOR INSERT WITH CHECK (true);

-- Create a function to get analytics data (similar to current app structure)
CREATE OR REPLACE FUNCTION get_analytics_data(
    search_text TEXT DEFAULT NULL,
    sentiment_filter TEXT[] DEFAULT NULL,
    category_filter TEXT[] DEFAULT NULL,
    country_filter TEXT[] DEFAULT NULL,
    device_filter TEXT[] DEFAULT NULL,
    ad_clicked_filter BOOLEAN DEFAULT NULL,
    limit_count INTEGER DEFAULT 1000,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    user_message TEXT,
    assistant_message TEXT,
    user_sentiment TEXT,
    ad_message TEXT,
    ad_clicked BOOLEAN,
    conversation_category TEXT,
    country TEXT,
    device_type TEXT,
    ad_category TEXT,
    timestamp TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cl.id,
        cl.user_message,
        cl.assistant_message,
        cl.user_sentiment,
        cl.ad_message,
        cl.ad_clicked,
        cl.conversation_category,
        cl.country,
        cl.device_type,
        cl.ad_category,
        cl.timestamp
    FROM chat_logs cl
    WHERE 
        (search_text IS NULL OR 
         cl.user_message ILIKE '%' || search_text || '%' OR 
         cl.assistant_message ILIKE '%' || search_text || '%' OR
         cl.ad_message ILIKE '%' || search_text || '%')
        AND (sentiment_filter IS NULL OR cl.user_sentiment = ANY(sentiment_filter))
        AND (category_filter IS NULL OR cl.conversation_category = ANY(category_filter))
        AND (country_filter IS NULL OR cl.country = ANY(country_filter))
        AND (device_filter IS NULL OR cl.device_type = ANY(device_filter))
        AND (ad_clicked_filter IS NULL OR cl.ad_clicked = ad_clicked_filter)
    ORDER BY cl.timestamp DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Run sample data insertion
SELECT insert_sample_data();
