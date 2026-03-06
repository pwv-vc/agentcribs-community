#!/usr/bin/env python3
"""CLI for semantic code search using PostgreSQL/pgvector - FOLLOWS SPEC."""

import sys
import argparse
from typing import Dict, List, Tuple, Any

from indexer import find_python_files, extract_code_elements
from embeddings import generate_embedding, create_searchable_text
from database import VectorDB, ProductionDB, ConfigurableTableSearch, load_table_config
import os

def cmd_index(args):
    """Index Python files with vector embeddings."""
    print(f"Indexing Python files in {args.directory}...")
    db = VectorDB()
    
    if args.clear:
        db.clear_all()
        print("Cleared existing index")
    
    python_files = find_python_files(args.directory)
    total_elements = 0
    
    for file_path in python_files:
        print(f"Processing {file_path}...")
        elements = extract_code_elements(file_path)
        
        for element in elements:
            # Create searchable text for embedding
            searchable_text = create_searchable_text(
                element['element_name'], 
                element['signature'], 
                element['docstring']
            )
            
            # Generate vector embedding
            embedding = generate_embedding(searchable_text)
            
            if embedding:
                db.insert(
                    file_path=element['file_path'],
                    name=element['element_name'],
                    element_type=element['element_type'], 
                    signature=element['signature'],
                    docstring=element['docstring'],
                    embedding=embedding
                )
                total_elements += 1
    
    print(f"Indexed {total_elements} elements from {len(python_files)} files")
    db.close()

def cmd_find(args):
    """Find code elements using semantic vector search."""
    db = VectorDB()
    
    # Generate embedding for search query
    query_embedding = generate_embedding(args.query)
    
    if not query_embedding:
        print("Failed to generate embedding for query")
        return
    
    # Perform vector similarity search
    results = db.search_similar(query_embedding, args.limit)
    
    if not results:
        print("No results found")
        db.close()
        return
    
    print(f"\nFound {len(results)} results:")
    print("-" * 80)
    
    for i, (element, score) in enumerate(results, 1):
        print(f"{i}. {element['element_name']} (score: {score:.3f})")
        print(f"   File: {element['file_path']}")
        print(f"   Type: {element['element_type']}")
        print(f"   Signature: {element['signature']}")
        if element['docstring']:
            docstring_preview = element['docstring'][:80]
            if len(element['docstring']) > 80:
                docstring_preview += "..."
            print(f"   Docstring: {docstring_preview}")
        print()
    
    db.close()

def cmd_stats(args):
    """Show indexing statistics."""
    db = VectorDB()
    stats = db.stats()

    print("Code Search Statistics:")
    print(f"Total elements: {stats['total_elements']}")
    print(f"Functions: {stats['functions']}")
    print(f"Classes: {stats['classes']}")
    print(f"Files indexed: {stats['unique_files']}")

    db.close()


def cmd_list_tables(args):
    """List configured searchable tables."""
    config = load_table_config()
    tables = config.get("tables", {})

    if not tables:
        print("No tables configured. Create a tables.yaml file.")
        return

    print("Configured searchable tables:")
    print("-" * 60)

    for name, table_config in tables.items():
        print(f"\n  find-{name}")
        print(f"    Table: {table_config['table']}")
        print(f"    Description: {table_config.get('description', 'No description')}")
        filters = table_config.get("filters", {})
        if filters.get("time_column"):
            default_hours = filters.get("default_hours", 168)
            print(f"    Time filter: --hours (default: {default_hours})")
        if filters.get("confidence_column"):
            default_conf = filters.get("default_min_confidence", 0.0)
            print(f"    Confidence filter: --confidence (default: {default_conf})")

    print()


def cmd_search_table(args):
    """Generic search for any configured table."""
    table_name = args.table_name

    print(f"Searching {table_name} for: {args.query}")

    # Show filter info
    config = load_table_config()
    tables = config.get("tables", {})
    if table_name not in tables:
        print(f"Error: Table '{table_name}' not configured.")
        print(f"Available tables: {list(tables.keys())}")
        return

    table_config = tables[table_name]
    filters = table_config.get("filters", {})

    if hasattr(args, 'hours') and args.hours is not None:
        print(f"Time range: last {args.hours} hours")
    if hasattr(args, 'confidence') and args.confidence is not None:
        print(f"Min confidence: {args.confidence}")

    print("-" * 80)

    query_embedding = generate_embedding(args.query)
    if not query_embedding:
        print("Failed to generate embedding for query")
        return

    db = ConfigurableTableSearch()
    results = db.search(
        table_name,
        query_embedding,
        limit=args.limit,
        hours=getattr(args, 'hours', None),
        min_confidence=getattr(args, 'confidence', None)
    )

    if not results:
        print("No results found")
        db.close()
        return

    print(f"\nFound {len(results)} results:\n")

    for i, (row, score) in enumerate(results, 1):
        # Format output dynamically based on available columns
        header_parts = [f"[{score:.3f}]"]

        # Try common identity columns
        if 'sender_name' in row:
            header_parts.append(row['sender_name'])
        elif 'person_name' in row:
            header_parts.append(row['person_name'])

        # Try type columns
        if 'conversation_type' in row:
            header_parts.append(f"({row['conversation_type']})")
        elif 'fact_type' in row:
            header_parts.append(f"- {row['fact_type']}")

        print(f"{i}. {' '.join(header_parts)}")

        # Show timestamp if present
        for ts_col in ['provider_timestamp', 'created_at']:
            if ts_col in row and row[ts_col]:
                ts = row[ts_col]
                if hasattr(ts, 'strftime'):
                    ts = ts.strftime("%Y-%m-%d %H:%M")
                print(f"   Time: {ts}")
                break

        # Show confidence if present
        if 'confidence' in row:
            print(f"   Confidence: {row['confidence']:.2f}")

        # Show content
        content = row.get('content', '')
        if not content:
            # Try other content-like columns
            for col in ['fact', 'summary', 'text']:
                if col in row and row[col]:
                    content = row[col]
                    break

        if content:
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   {content}")

        print()

    db.close()


# Legacy commands for backwards compatibility
def cmd_find_messages(args):
    """Search production messages semantically (legacy command)."""
    args.table_name = "messages"
    cmd_search_table(args)


def cmd_find_facts(args):
    """Search production facts semantically (legacy command)."""
    args.table_name = "facts"
    cmd_search_table(args)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Semantic code search tool")
    subparsers = parser.add_subparsers(dest='command')

    # Index command
    index_parser = subparsers.add_parser('index', help='Index Python files')
    index_parser.add_argument('directory', help='Directory to index')
    index_parser.add_argument('--clear', action='store_true', help='Clear existing index')
    index_parser.set_defaults(func=cmd_index)

    # Find command (code search)
    find_parser = subparsers.add_parser('find', help='Search for code semantically')
    find_parser.add_argument('query', help='Search query')
    find_parser.add_argument('--limit', type=int, default=5, help='Number of results')
    find_parser.set_defaults(func=cmd_find)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # List tables command
    list_tables_parser = subparsers.add_parser(
        'list-tables',
        help='List configured searchable tables'
    )
    list_tables_parser.set_defaults(func=cmd_list_tables)

    # Dynamically register commands for each configured table
    config = load_table_config()
    tables = config.get("tables", {})

    for table_name, table_config in tables.items():
        cmd_name = f"find-{table_name}"
        description = table_config.get("description", f"Search {table_name} semantically")
        filters = table_config.get("filters", {})

        table_parser = subparsers.add_parser(cmd_name, help=description)
        table_parser.add_argument('query', help='Search query')
        table_parser.add_argument('--limit', type=int, default=10, help='Number of results')

        # Add filter arguments based on config
        if filters.get("time_column"):
            default_hours = filters.get("default_hours", 168)
            table_parser.add_argument(
                '--hours',
                type=int,
                default=default_hours,
                help=f'Search last N hours (default: {default_hours})'
            )

        if filters.get("confidence_column"):
            default_conf = filters.get("default_min_confidence", 0.6)
            table_parser.add_argument(
                '--confidence',
                type=float,
                default=default_conf,
                help=f'Min confidence (default: {default_conf})'
            )

        # Use closure to capture table_name
        def make_handler(tname):
            def handler(args):
                args.table_name = tname
                cmd_search_table(args)
            return handler

        table_parser.set_defaults(func=make_handler(table_name))

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()