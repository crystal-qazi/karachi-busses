import mysql.connector
from flask import current_app


def get_db_connection():
    """Create a MySQL connection using the active Flask app configuration."""
    return mysql.connector.connect(**current_app.config["DB_CONFIG"])
