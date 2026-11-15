"""Apply pending SQL migrations in filename order."""
from pathlib import Path
import sys

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from config import Config  # noqa: E402


def split_sql_statements(sql_text: str) -> list[str]:
    # Migration files deliberately avoid semicolons inside quoted strings.
    return [part.strip() for part in sql_text.split(";") if part.strip()]


def main() -> int:
    connection = None
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        cursor.execute("SELECT migration_name FROM schema_migrations")
        applied = {row[0] for row in cursor.fetchall()}

        for migration_path in sorted((ROOT / "migrations").glob("*.sql")):
            if migration_path.name in applied:
                print(f"SKIP {migration_path.name} (already applied)")
                continue

            print(f"APPLY {migration_path.name}")
            try:
                for statement in split_sql_statements(migration_path.read_text(encoding="utf-8")):
                    cursor.execute(statement)
                cursor.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                    (migration_path.name,),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

        cursor.close()
        print("Migrations are up to date.")
        return 0
    except mysql.connector.Error as exc:
        print(f"Database migration failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Could not read migration files: {exc}", file=sys.stderr)
        return 1
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
