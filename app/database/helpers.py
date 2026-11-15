from contextlib import contextmanager

from app.database.connection import get_db_connection


@contextmanager
def cursor_context(dictionary=True, commit=False):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield connection, cursor
        if commit:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
