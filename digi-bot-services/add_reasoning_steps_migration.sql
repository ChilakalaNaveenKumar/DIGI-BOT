-- Add reasoning_steps column to messages table
-- This stores the thinking steps as JSON for frontend reconstruction

ALTER TABLE messages ADD COLUMN reasoning_steps JSONB DEFAULT NULL;

-- Add index for better query performance on reasoning_steps
CREATE INDEX idx_messages_reasoning_steps ON messages USING GIN (reasoning_steps) WHERE reasoning_steps IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN messages.reasoning_steps IS 'JSON array of reasoning steps including thinking steps and tool calls (web_search, code_execution, etc.)';
