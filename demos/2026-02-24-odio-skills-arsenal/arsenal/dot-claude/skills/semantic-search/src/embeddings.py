#!/usr/bin/env python3
"""Embedding generation for semantic code search."""

import sys
import os
from typing import Optional

# Standalone implementation - no external dependencies
USING_MAIN_CODEBASE = False

def sanitize_text_for_embedding(text: str) -> str:
    """Simple text sanitization without emoji dependency."""
    if not text:
        return ""
    text = str(text).lower()
    text = " ".join(text.split())
    import re
    text = re.sub(r"[^\w\s.,!?-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_embedding(text: str, *, raise_on_error: bool = False) -> Optional[list[float]]:
    """Generate embeddings using OpenAI API."""
    sanitized = sanitize_text_for_embedding(text)
    if not sanitized:
        return [0.0] * 1536
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    import openai
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=sanitized
    )
    return response.data[0].embedding

def create_searchable_text(element_name: str, signature: str, docstring: str) -> str:
    """Create searchable text from code element components."""
    parts = [element_name, signature]
    if docstring:
        parts.append(docstring)
    return " ".join(filter(None, parts))


# Export the functions for compatibility
__all__ = ['generate_embedding', 'sanitize_text_for_embedding', 'create_searchable_text']