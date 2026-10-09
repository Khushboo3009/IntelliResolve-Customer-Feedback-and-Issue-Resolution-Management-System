from sqlalchemy import text
from db.engine import engine

def mysql_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "MySQL connection is healthy."
    except Exception as exc:
        return False, str(exc)

def database_table_count():
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE()"
            ))
            return int(result.scalar() or 0)
    except Exception:
        return 0
