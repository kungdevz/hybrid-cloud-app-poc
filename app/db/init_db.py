#!/usr/bin/env python
"""
Database initialization script.
Reads init.sql and executes it against the database using pyodbc.
Handles GO batch separators that pyodbc doesn't natively support.
"""
import os
import re
import sys

import pyodbc


def _resolve_init_sql_path() -> str:
    """Resolve the path to init.sql based on the current profile.

    Returns:
        Absolute path to the init.sql file.

    Raises:
        FileNotFoundError: If the resolved path does not exist.
    """
    profile = os.getenv('PROFILE', os.getenv('APP_PROFILE', 'production')).lower()

    if profile == 'production':
        relative = './init.sql'
    else:
        relative = '../db/init-scripts/init.sql'

    path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), relative)
    )

    print("Resolve init sql path is : " + path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"init.sql not found at {path}")

    return path


def _split_batches(sql: str) -> list[str]:
    """Split a SQL script on GO batch separators.

    Args:
        sql: Raw SQL script content.

    Returns:
        List of individual SQL batches with GO lines removed.
    """
    batches = re.split(r'^\s*GO\s*$', sql, flags=re.MULTILINE | re.IGNORECASE)
    return [b.strip() for b in batches if b.strip()]


def run_init_sql() -> bool:
    """Execute init.sql against the database using pyodbc.

    Connects to master first (so CREATE DATABASE works), then splits
    the script on GO separators and runs each batch sequentially.

    Returns:
        True if all batches executed successfully, False otherwise.
    """
    from config import get_odbc_connection_string

    try:
        sql_path = _resolve_init_sql_path()
        print(f"init_sql >>> {sql_path}")

        with open(sql_path, 'r') as f:
            sql_content = f.read()

        batches = _split_batches(sql_content)
        if not batches:
            print("No SQL batches found in init.sql")
            return False

        conn_str = get_odbc_connection_string(database='master')
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        for i, batch in enumerate(batches, start=1):
            try:
                cursor.execute(batch)
                print(f"Batch {i}/{len(batches)} executed OK")
            except pyodbc.Error as e:
                print(f"Batch {i}/{len(batches)} failed: {e}", file=sys.stderr)

        cursor.close()
        conn.close()
        print("Database initialization complete.")
        return True

    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return False
    except pyodbc.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        return False
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    run_init_sql()
