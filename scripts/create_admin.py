"""Create or update an administrator using an interactively entered password."""
from getpass import getpass
from pathlib import Path
import sys

import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
from config import Config  # noqa: E402


def main():
    username = input("Admin username: ").strip()
    if not username or len(username) > 80:
        print("Username must be 1-80 characters.")
        return 1
    password = getpass("Password (minimum 12 characters): ")
    confirm = getpass("Confirm password: ")
    if len(password) < 12 or password != confirm:
        print("Passwords must match and contain at least 12 characters.")
        return 1

    password_hash = generate_password_hash(password)
    connection = mysql.connector.connect(**Config.DB_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO admin_users (username, password_hash, role, is_active)
            VALUES (%s, %s, 'super_admin', 1)
            ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash),
                                    role='super_admin', is_active=1
        """, (username, password_hash))
        connection.commit()
        cursor.close()
        print(f"Administrator '{username}' is ready.")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
