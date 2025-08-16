-- Step 1: Run this SQL in your Supabase SQL Editor to allow CSV upload

-- First, let's check the current RLS status
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'chat_logs';

-- Temporarily disable RLS for chat_logs table
ALTER TABLE chat_logs DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'chat_logs';

-- Optional: Check existing policies
SELECT schemaname, tablename, policyname, cmd, permissive, roles, qual, with_check
FROM pg_policies 
WHERE tablename = 'chat_logs';

-- You can now run the Python upload script
-- After upload, re-enable RLS with:
-- ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;
