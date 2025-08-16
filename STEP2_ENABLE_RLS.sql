-- Step 2: Run this SQL AFTER the CSV upload completes to re-enable security

-- Re-enable RLS for chat_logs table
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

-- Verify RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'chat_logs';

-- Check that policies are still in place
SELECT schemaname, tablename, policyname, cmd, permissive, roles, qual, with_check
FROM pg_policies 
WHERE tablename = 'chat_logs';

-- Count the uploaded records
SELECT COUNT(*) as total_records FROM chat_logs;
