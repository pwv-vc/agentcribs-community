-- Database initialization script for semantic code search
-- Creates pgvector extension and code_elements table

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create main table for code elements with vector embeddings
CREATE TABLE IF NOT EXISTS code_elements (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    element_name TEXT NOT NULL,
    element_type TEXT NOT NULL CHECK (element_type IN ('function', 'class')),
    signature TEXT,
    docstring TEXT,
    searchable_text TEXT,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_code_elements_file ON code_elements(file_path);
CREATE INDEX IF NOT EXISTS idx_code_elements_type ON code_elements(element_type);
CREATE INDEX IF NOT EXISTS idx_code_elements_name ON code_elements(element_name);

-- Create vector similarity index (IVFFlat with cosine distance)
CREATE INDEX IF NOT EXISTS idx_code_elements_embedding 
ON code_elements USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);