-- ============================================================================
-- VECTOR DATABASE SETUP FOR DIGI SETU AI
-- ============================================================================
-- 
-- Adds vector functionality to existing database without breaking current structure
-- Uses text-embedding-3-large (3072 dimensions) for high-quality embeddings
--
-- ============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- VECTOR TABLES - INTEGRATED WITH EXISTING STRUCTURE
-- ============================================================================

-- 1) Core: one vector per message pair (user query + AI response)
CREATE TABLE IF NOT EXISTS message_vectors (
    id                TEXT PRIMARY KEY,                        -- vec:{conversation_id}:{message_id}
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id   INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id        TEXT NOT NULL,                           -- composite: user_msg_id:assistant_msg_id
    turn_index        INTEGER NOT NULL,                        -- order within conversation
    role_pair         TEXT NOT NULL DEFAULT 'user_assistant',
    ts                TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    snippet           TEXT,                                    -- short preview (first 500 chars)
    content_summary   TEXT,                                    -- "User: ... Assistant: ..."
    has_attachments   BOOLEAN NOT NULL DEFAULT FALSE,
    attachment_ids    INTEGER[] DEFAULT '{}',
    attachment_types  TEXT[] DEFAULT '{}',
    expires_at        TIMESTAMP WITH TIME ZONE,               -- 7-day expiry
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,          -- soft delete
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding         VECTOR(3072) NOT NULL                   -- text-embedding-3-large
);

-- 2) Rolling conversation summaries (every 5-10 turns)
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id                TEXT PRIMARY KEY,                        -- sum:{conversation_id}:{start_turn}-{end_turn}
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id   INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    start_turn        INTEGER NOT NULL,
    end_turn          INTEGER NOT NULL,
    summary_text      TEXT NOT NULL,
    snippet           TEXT,                                    -- short preview
    expires_at        TIMESTAMP WITH TIME ZONE,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding         VECTOR(3072) NOT NULL
);

-- 3) Attachments (enhanced existing structure)
CREATE TABLE IF NOT EXISTS attachments (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id   INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    message_id        TEXT,                                    -- nullable if uploaded outside chat
    original_filename VARCHAR(255) NOT NULL,
    stored_filename   VARCHAR(255) NOT NULL,
    file_type         VARCHAR(50) NOT NULL,                    -- image, document, audio
    mime_type         VARCHAR(100),
    file_size         INTEGER NOT NULL,
    storage_path      VARCHAR(500) NOT NULL,
    vector_id         VARCHAR(255),                            -- reference to vector DB
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at        TIMESTAMP WITH TIME ZONE,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- 4) Attachment vectors (per file chunk)
CREATE TABLE IF NOT EXISTS attachment_vectors (
    id                TEXT PRIMARY KEY,                        -- vec:{attachment_id}:{chunk_index}
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attachment_id     INTEGER NOT NULL REFERENCES attachments(id) ON DELETE CASCADE,
    conversation_id   INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    message_id        TEXT,                                    -- nullable
    file_type         VARCHAR(50) NOT NULL,
    chunk_index       INTEGER NOT NULL DEFAULT 0,
    snippet           TEXT,
    content_summary   TEXT,                                    -- extracted text summary
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at        TIMESTAMP WITH TIME ZONE,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding         VECTOR(3072) NOT NULL
);

-- 5) Message-Attachments junction table
CREATE TABLE IF NOT EXISTS message_attachments (
    message_id        TEXT NOT NULL,                           -- composite message ID
    attachment_id     INTEGER NOT NULL REFERENCES attachments(id) ON DELETE CASCADE,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (message_id, attachment_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- message_vectors indexes
CREATE INDEX IF NOT EXISTS mv_user_idx        ON message_vectors(user_id);
CREATE INDEX IF NOT EXISTS mv_conv_idx        ON message_vectors(conversation_id, turn_index);
CREATE INDEX IF NOT EXISTS mv_ts_idx          ON message_vectors(ts DESC);
CREATE INDEX IF NOT EXISTS mv_exp_idx         ON message_vectors(expires_at);
CREATE INDEX IF NOT EXISTS mv_active_idx      ON message_vectors(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS mv_meta_gin        ON message_vectors USING GIN (metadata);
CREATE INDEX IF NOT EXISTS mv_snip_trgm       ON message_vectors USING GIN (snippet gin_trgm_ops);

-- Vector similarity index (HNSW for high dimensions)
CREATE INDEX IF NOT EXISTS mv_embed_hnsw   ON message_vectors USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- conversation_summaries indexes
CREATE INDEX IF NOT EXISTS cs_conv_idx        ON conversation_summaries(conversation_id, start_turn, end_turn);
CREATE INDEX IF NOT EXISTS cs_exp_idx         ON conversation_summaries(expires_at);
CREATE INDEX IF NOT EXISTS cs_meta_gin        ON conversation_summaries USING GIN (metadata);
CREATE INDEX IF NOT EXISTS cs_embed_hnsw   ON conversation_summaries USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- attachments indexes
CREATE INDEX IF NOT EXISTS att_user_idx       ON attachments(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS att_conv_idx       ON attachments(conversation_id);
CREATE INDEX IF NOT EXISTS att_vector_idx     ON attachments(vector_id) WHERE vector_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS att_exp_idx        ON attachments(expires_at);

-- attachment_vectors indexes
CREATE INDEX IF NOT EXISTS av_user_idx        ON attachment_vectors(user_id);
CREATE INDEX IF NOT EXISTS av_att_idx         ON attachment_vectors(attachment_id, chunk_index);
CREATE INDEX IF NOT EXISTS av_conv_idx        ON attachment_vectors(conversation_id);
CREATE INDEX IF NOT EXISTS av_exp_idx         ON attachment_vectors(expires_at);
CREATE INDEX IF NOT EXISTS av_meta_gin        ON attachment_vectors USING GIN (metadata);
CREATE INDEX IF NOT EXISTS av_embed_hnsw   ON attachment_vectors USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- message_attachments indexes
CREATE INDEX IF NOT EXISTS ma_msg_idx         ON message_attachments(message_id);
CREATE INDEX IF NOT EXISTS ma_att_idx         ON message_attachments(attachment_id);

-- ============================================================================
-- TTL CLEANUP FUNCTIONS
-- ============================================================================

-- Function to clean up expired vectors
CREATE OR REPLACE FUNCTION cleanup_expired_vectors()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Soft delete expired vectors (grace period)
    UPDATE message_vectors 
    SET is_active = FALSE 
    WHERE expires_at < NOW() AND is_active = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Hard delete after grace period (1 day)
    DELETE FROM message_vectors 
    WHERE is_active = FALSE AND expires_at < NOW() - INTERVAL '1 day';
    
    -- Clean up expired summaries
    DELETE FROM conversation_summaries 
    WHERE expires_at < NOW();
    
    -- Clean up expired attachment vectors
    DELETE FROM attachment_vectors 
    WHERE expires_at < NOW();
    
    -- Clean up expired attachments
    DELETE FROM attachments 
    WHERE expires_at < NOW();
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER FUNCTIONS FOR VECTOR OPERATIONS
-- ============================================================================

-- Function to generate vector ID
CREATE OR REPLACE FUNCTION generate_vector_id(
    conv_id INTEGER,
    msg_id TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN 'vec:' || conv_id::TEXT || ':' || msg_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate summary ID
CREATE OR REPLACE FUNCTION generate_summary_id(
    conv_id INTEGER,
    start_turn INTEGER,
    end_turn INTEGER
) RETURNS TEXT AS $$
BEGIN
    RETURN 'sum:' || conv_id::TEXT || ':' || start_turn::TEXT || '-' || end_turn::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

-- Semantic search with user filter (last 30 days)
/*
WITH q AS (SELECT $1::vector AS qv, $2::integer AS uid, $3::timestamp AS since)
SELECT 
    id, 
    conversation_id, 
    message_id, 
    turn_index, 
    snippet,
    1 - (embedding <=> (SELECT qv FROM q)) AS similarity_score
FROM message_vectors
WHERE user_id = (SELECT uid FROM q)
  AND ts >= (SELECT since FROM q)
  AND is_active = TRUE
ORDER BY embedding <-> (SELECT qv FROM q)
LIMIT 10;
*/

-- Get conversation context (neighboring turns)
/*
SELECT *
FROM message_vectors
WHERE conversation_id = $1
  AND turn_index BETWEEN $2-2 AND $2+2
  AND is_active = TRUE
ORDER BY turn_index;
*/

-- Search within specific conversation
/*
WITH q AS (SELECT $1::vector AS qv, $2::integer AS cid)
SELECT 
    id, 
    message_id, 
    turn_index, 
    snippet,
    1 - (embedding <=> (SELECT qv FROM q)) AS similarity_score
FROM message_vectors
WHERE conversation_id = (SELECT cid FROM q)
  AND is_active = TRUE
ORDER BY embedding <-> (SELECT qv FROM q)
LIMIT 5;
*/

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================

/*
PERFORMANCE OPTIMIZATIONS:

1. EMBEDDING DIMENSION: 3072 (text-embedding-3-large)
   - High quality embeddings for better semantic search
   - Cost: $0.00013 per 1K tokens (very reasonable)

2. INDEXING STRATEGY:
   - IVFFlat for vector similarity (good balance of speed/accuracy)
   - GIN indexes for metadata and text search
   - Composite indexes for common query patterns

3. TTL MANAGEMENT:
   - 7-day expiry for active conversations
   - Soft delete with 1-day grace period
   - Automatic cleanup via scheduled function

4. QUERY PATTERNS:
   - User-scoped searches (privacy)
   - Conversation-scoped searches (context)
   - Time-based filtering (recent relevance)
   - Hybrid text + vector search

5. STORAGE EFFICIENCY:
   - Snippets for quick preview (avoid full content in vector table)
   - JSONB metadata for flexible attributes
   - Proper foreign key constraints for data integrity

EXPECTED PERFORMANCE:
- Vector search: <50ms for 10K vectors
- Context retrieval: <10ms
- Cleanup operations: Background, no user impact
*/
