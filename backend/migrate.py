"""
Simple forward-only migration runner.
Tracks applied migrations in a _migrations table.
"""

import os
import sys
import time
import glob
import psycopg

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://landline:landline@localhost:5432/landline",
)


def wait_for_db(max_retries: int = 30):
    for attempt in range(max_retries):
        try:
            conn = psycopg.connect(DATABASE_URL)
            conn.close()
            return
        except psycopg.OperationalError:
            print(f"  Waiting for database... ({attempt + 1}/{max_retries})")
            time.sleep(1)
    print("Database not available — exiting.")
    sys.exit(1)


def run_migrations():
    wait_for_db()

    conn = psycopg.connect(DATABASE_URL, autocommit=True)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            filename VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT now()
        )
    """)

    migration_dir = os.path.join(os.path.dirname(__file__), "migrations")
    files = sorted(glob.glob(os.path.join(migration_dir, "*.sql")))

    for filepath in files:
        filename = os.path.basename(filepath)
        row = conn.execute(
            "SELECT 1 FROM _migrations WHERE filename = %s", [filename]
        ).fetchone()
        if row:
            print(f"  skip  {filename}")
            continue

        print(f"  apply {filename} ...")
        with open(filepath) as f:
            conn.execute(f.read())
        conn.execute(
            "INSERT INTO _migrations (filename) VALUES (%s)", [filename]
        )

    conn.close()
    print("Migrations complete.")


if __name__ == "__main__":
    run_migrations()
