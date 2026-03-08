#!/usr/bin/env python3
"""PostgreSQL/pgvector database operations - REUSES existing patterns."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import psycopg2
import psycopg2.extras
import yaml

class VectorDB:
    """PostgreSQL/pgvector database for semantic code search."""
    
    def __init__(self):
        self.conn = None
        self._connect()
        self._ensure_schema()
    
    def _connect(self):
        """Connect to PostgreSQL using existing patterns."""
        db_url = os.getenv("DATABASE_URL", "postgresql://codesearch:codesearch@postgres:5432/codesearch")
        self.conn = psycopg2.connect(db_url)
        self.conn.autocommit = True
    
    def _ensure_schema(self):
        """Create tables if they don't exist."""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create table with vector embeddings
            cur.execute("""
                CREATE TABLE IF NOT EXISTS code_elements (
                    id SERIAL PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    element_name TEXT NOT NULL,
                    element_type TEXT NOT NULL,
                    signature TEXT,
                    docstring TEXT,
                    searchable_text TEXT,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create vector similarity index
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_code_elements_embedding 
                ON code_elements USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
    
    def clear_all(self):
        """Clear all indexed code elements."""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM code_elements")
    
    def insert(self, file_path: str, name: str, element_type: str, 
               signature: str, docstring: str, embedding: List[float]) -> None:
        """Insert code element with embedding vector."""
        from embeddings import create_searchable_text
        
        searchable_text = create_searchable_text(name, signature, docstring)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO code_elements 
                (file_path, element_name, element_type, signature, docstring, searchable_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (file_path, name, element_type, signature, docstring, searchable_text, embedding))
    
    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar code elements using vector similarity."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Use cosine similarity search with pgvector
            cur.execute("""
                SELECT 
                    file_path, element_name, element_type, signature, docstring,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM code_elements 
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, limit))
            
            results = []
            for row in cur.fetchall():
                element = dict(row)
                similarity_score = element.pop('similarity_score')
                results.append((element, float(similarity_score)))
            
            return results
    
    def stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM code_elements")
            total = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM code_elements WHERE element_type = 'function'")
            functions = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM code_elements WHERE element_type = 'class'")
            classes = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT file_path) FROM code_elements")
            files = cur.fetchone()[0]
            
            return {
                'total_elements': total,
                'functions': functions, 
                'classes': classes,
                'unique_files': files
            }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def load_table_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load table configuration from YAML file."""
    if config_path is None:
        # Try multiple locations:
        # 1. /app/tables.yaml (Docker mount)
        # 2. tables.yaml in the skill directory (local development)
        candidates = [
            Path("/app/tables.yaml"),
            Path(__file__).parent.parent / "tables.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break
        else:
            return {"tables": {}}

    config_path = Path(config_path)
    if not config_path.exists():
        return {"tables": {}}

    with open(config_path) as f:
        return yaml.safe_load(f) or {"tables": {}}


class ConfigurableTableSearch:
    """
    Generic semantic search for any table with vector embeddings.

    Configuration is loaded from tables.yaml which defines:
    - Table name and alias
    - Content and embedding columns
    - JOINs for enriching results
    - Display columns
    - Optional filters (time, confidence, etc.)
    """

    def __init__(self, config_path: Optional[str] = None):
        self.conn = None
        self.config = load_table_config(config_path)
        self._connect()

    def _connect(self):
        """Connect to production PostgreSQL using environment variables."""
        host = os.getenv("PROD_PGHOST")
        port = os.getenv("PROD_PGPORT", "5432")
        database = os.getenv("PROD_PGDATABASE")
        user = os.getenv("PROD_PGUSER")
        password = os.getenv("PROD_PGPASSWORD")
        sslmode = os.getenv("PROD_PGSSLMODE", "require")

        if not all([host, database, user, password]):
            raise ValueError(
                "Production database credentials not configured. "
                "Set PGHOST, PGDATABASE, PGUSER, PGPASSWORD in arsenal/.env"
            )

        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode=sslmode
        )

    def get_available_tables(self) -> Dict[str, Dict[str, Any]]:
        """Return configured tables and their metadata."""
        return self.config.get("tables", {})

    def search(
        self,
        table_name: str,
        query_embedding: List[float],
        limit: int = 10,
        hours: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search a configured table by semantic similarity.

        Args:
            table_name: Name of the table config (e.g., "messages", "facts")
            query_embedding: Vector embedding of the search query
            limit: Maximum number of results
            hours: Time filter (if table has time_column configured)
            min_confidence: Confidence filter (if table has confidence_column configured)

        Returns:
            List of (row_dict, similarity_score) tuples
        """
        tables = self.config.get("tables", {})
        if table_name not in tables:
            raise ValueError(f"Table '{table_name}' not configured. Available: {list(tables.keys())}")

        table_config = tables[table_name]
        table = table_config["table"]
        embedding_col = table_config["embedding_column"]
        # Use explicit alias from config, or default to first letter of table name
        alias = table_config.get("alias", table[0])
        display_cols = table_config.get("display_columns", [f"{alias}.id", f"{alias}.{table_config['content_column']}"])
        joins = table_config.get("joins", [])
        filters = table_config.get("filters", {})

        # Build SELECT clause
        select_cols = ", ".join(display_cols)
        select_clause = f"{select_cols}, 1 - ({alias}.{embedding_col} <=> %s::vector) as similarity_score"

        # Build FROM clause with JOINs
        from_clause = f"{table} {alias}"
        if joins:
            from_clause += " " + " ".join(joins)

        # Build WHERE clause
        where_conditions = [f"{alias}.{embedding_col} IS NOT NULL"]
        params = [query_embedding]

        # Add time filter if configured and provided
        time_col = filters.get("time_column")
        if time_col:
            effective_hours = hours if hours is not None else filters.get("default_hours", 168)
            where_conditions.append(f"{alias}.{time_col} >= NOW() - INTERVAL '%s hours'")
            params.append(effective_hours)

        # Add confidence filter if configured and provided
        conf_col = filters.get("confidence_column")
        if conf_col:
            effective_conf = min_confidence if min_confidence is not None else filters.get("default_min_confidence", 0.0)
            where_conditions.append(f"{alias}.{conf_col} >= %s")
            params.append(effective_conf)

        where_clause = " AND ".join(where_conditions)

        # Build ORDER BY and LIMIT
        order_clause = f"{alias}.{embedding_col} <=> %s::vector"
        params.append(query_embedding)
        params.append(limit)

        # Build full query
        query = f"""
            SELECT {select_clause}
            FROM {from_clause}
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT %s
        """

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)

            results = []
            for row in cur.fetchall():
                data = dict(row)
                score = float(data.pop('similarity_score'))
                results.append((data, score))

            return results

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Convenience alias with typed helper methods
class ProductionDB(ConfigurableTableSearch):
    """Production database search with convenience methods for common tables."""

    def search_messages(
        self,
        query_embedding: List[float],
        limit: int = 10,
        hours: int = 168
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search messages by semantic similarity."""
        return self.search("messages", query_embedding, limit=limit, hours=hours)

    def search_facts(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_confidence: float = 0.6
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search person facts by semantic similarity."""
        return self.search("facts", query_embedding, limit=limit, min_confidence=min_confidence)