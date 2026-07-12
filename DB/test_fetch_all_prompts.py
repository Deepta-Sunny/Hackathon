"""
Test utility: fetch all prompt records from DuckDB and print what is loaded.

Usage:
  python DB/test_fetch_all_prompts.py
  python DB/test_fetch_all_prompts.py --db-path BACKEND/chat_memory.db --full-text
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import duckdb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch all prompt records from DuckDB SeedPromptEntries")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parents[1] / "BACKEND" / "chat_memory.db"),
        help="Path to DuckDB file (default: BACKEND/chat_memory.db)",
    )
    parser.add_argument(
        "--json-out",
        default=str(Path(__file__).resolve().parent / "seed_prompts_dump.json"),
        help="Output path for JSON dump",
    )
    parser.add_argument(
        "--full-text",
        action="store_true",
        help="Print full prompt text. By default, text is truncated to 220 chars.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of rows to display and dump",
    )
    return parser.parse_args()


def normalize_json_field(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def main() -> int:
    args = parse_args()

    db_path = Path(args.db_path).resolve()
    if not db_path.exists():
        print(f"[ERROR] DuckDB file not found: {db_path}")
        return 1

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        tables = [row[0] for row in con.execute("SHOW TABLES").fetchall()]
        if "SeedPromptEntries" not in tables:
            print("[ERROR] Table 'SeedPromptEntries' was not found in the DB.")
            print(f"[INFO] Available tables: {tables}")
            return 1

        count_query = "SELECT COUNT(*) FROM SeedPromptEntries"
        total_rows = con.execute(count_query).fetchone()[0]

        print(f"[INFO] DB Path: {db_path}")
        print(f"[INFO] Total seed prompts in SeedPromptEntries: {total_rows}")

        dataset_rows = con.execute(
            """
            SELECT COALESCE(dataset_name, 'NULL') AS dataset_name, COUNT(*) AS prompt_count
            FROM SeedPromptEntries
            GROUP BY dataset_name
            ORDER BY prompt_count DESC, dataset_name
            """
        ).fetchall()

        print("\n[INFO] Prompt counts by dataset_name:")
        for dataset_name, prompt_count in dataset_rows:
            print(f"  - {dataset_name}: {prompt_count}")

        base_query = """
            SELECT
                id,
                name,
                dataset_name,
                value,
                description,
                source,
                added_by,
                date_added,
                groups,
                parameters
            FROM SeedPromptEntries
            ORDER BY date_added DESC, name NULLS LAST
        """
        params = []
        if args.limit is not None and args.limit > 0:
            base_query += " LIMIT ?"
            params.append(args.limit)

        rows = con.execute(base_query, params).fetchall()

        dump_records = []
        print(f"\n[INFO] Displaying {len(rows)} prompt records:\n")
        for idx, row in enumerate(rows, 1):
            (
                prompt_id,
                name,
                dataset_name,
                value,
                description,
                source,
                added_by,
                date_added,
                groups,
                parameters,
            ) = row

            shown_text = value if args.full_text else (value[:220] + "..." if len(value) > 220 else value)

            print(f"[{idx}] id={prompt_id}")
            print(f"    dataset_name: {dataset_name}")
            print(f"    name: {name}")
            print(f"    source: {source} | added_by: {added_by} | date_added: {date_added}")
            print(f"    prompt: {shown_text}")
            if description:
                desc = description if len(description) <= 240 else description[:240] + "..."
                print(f"    description: {desc}")
            print(f"    groups: {normalize_json_field(groups)}")
            print(f"    parameters: {normalize_json_field(parameters)}")
            print("-" * 120)

            dump_records.append(
                {
                    "id": str(prompt_id),
                    "name": name,
                    "dataset_name": dataset_name,
                    "value": value,
                    "description": description,
                    "source": source,
                    "added_by": added_by,
                    "date_added": str(date_added),
                    "groups": normalize_json_field(groups),
                    "parameters": normalize_json_field(parameters),
                }
            )

        json_out = Path(args.json_out).resolve()
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(dump_records, indent=2, ensure_ascii=True), encoding="utf-8")
        print(f"\n[OK] Wrote JSON dump: {json_out}")

    finally:
        con.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
