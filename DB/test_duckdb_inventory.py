"""
Test utility: inspect DuckDB tables, schema, and row counts.

Usage:
  python DB/test_duckdb_inventory.py
  python DB/test_duckdb_inventory.py --db-path BACKEND/chat_memory.db
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect DuckDB inventory and table schemas")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parents[1] / "BACKEND" / "chat_memory.db"),
        help="Path to DuckDB file (default: BACKEND/chat_memory.db)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()

    if not db_path.exists():
        print(f"[ERROR] DuckDB file not found: {db_path}")
        return 1

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        tables = [row[0] for row in con.execute("SHOW TABLES").fetchall()]
        if not tables:
            print(f"[INFO] No tables found in {db_path}")
            return 0

        print(f"[INFO] DB Path: {db_path}")
        print(f"[INFO] Tables ({len(tables)}): {', '.join(tables)}\n")

        for table_name in tables:
            row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            columns = con.execute(f"DESCRIBE {table_name}").fetchall()

            print(f"[TABLE] {table_name}")
            print(f"  row_count: {row_count}")
            print("  columns:")
            for col_name, col_type, nullable, key, default, extra in columns:
                print(
                    f"    - {col_name} | type={col_type} | null={nullable} "
                    f"| key={key} | default={default} | extra={extra}"
                )
            print()

    finally:
        con.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
