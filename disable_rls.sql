-- SQL commands to run in Supabase SQL Editor to allow data upload

-- Temporarily disable RLS for chat_logs table
ALTER TABLE chat_logs DISABLE ROW LEVEL SECURITY;

-- Or alternatively, create a more permissive policy temporarily
-- DROP POLICY IF EXISTS "Enable insert access for all users" ON chat_logs;
-- CREATE POLICY "Temporary bulk insert policy" ON chat_logs FOR INSERT WITH CHECK (true);

-- After upload, you can re-enable RLS:
-- ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;
