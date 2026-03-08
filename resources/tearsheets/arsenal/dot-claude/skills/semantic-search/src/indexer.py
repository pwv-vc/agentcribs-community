#!/usr/bin/env python3
"""AST-based code indexing for Python files."""

import ast
import os
from typing import List, Dict, Any
from pathlib import Path

def extract_code_elements(file_path: str) -> List[Dict[str, Any]]:
    """Extract functions and classes from a Python file using AST."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    elements = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            elements.append(_extract_function(node, file_path))
        elif isinstance(node, ast.ClassDef):
            elements.append(_extract_class(node, file_path))
    
    return elements

def _extract_function(node: ast.FunctionDef, file_path: str) -> Dict[str, Any]:
    """Extract function information from AST node."""
    # Build signature
    args = []
    for arg in node.args.args:
        args.append(arg.arg)
    
    signature = f"def {node.name}({', '.join(args)})"
    
    # Extract docstring
    docstring = ""
    if (node.body and isinstance(node.body[0], ast.Expr) 
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)):
        docstring = node.body[0].value.value
    
    return {
        'file_path': file_path,
        'element_name': node.name,
        'element_type': 'function',
        'signature': signature,
        'docstring': docstring,
        'line_number': node.lineno
    }

def _extract_class(node: ast.ClassDef, file_path: str) -> Dict[str, Any]:
    """Extract class information from AST node."""
    # Build signature with base classes
    bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
    signature = f"class {node.name}"
    if bases:
        signature += f"({', '.join(bases)})"
    
    # Extract docstring
    docstring = ""
    if (node.body and isinstance(node.body[0], ast.Expr) 
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)):
        docstring = node.body[0].value.value
    
    return {
        'file_path': file_path,
        'element_name': node.name,
        'element_type': 'class',
        'signature': signature,
        'docstring': docstring,
        'line_number': node.lineno
    }

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in directory recursively."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    
    return python_files