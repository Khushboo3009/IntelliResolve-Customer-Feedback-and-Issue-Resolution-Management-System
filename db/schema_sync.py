"""Idempotent schema synchronizer for existing MySQL development databases.

SQLAlchemy's create_all() creates missing tables but does not add missing columns to
existing tables. This module safely adds columns that are present in the current ORM
models but missing from an existing database. It intentionally does not drop columns
or change existing column types.
"""
from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateColumn
from sqlalchemy.dialects import mysql
from db.engine import Base, engine


def _column_sql(column):
    compiled = str(CreateColumn(column).compile(dialect=mysql.dialect()))
    # Existing populated tables can reject NOT NULL additions without defaults.
    # Make added columns nullable; ORM/application defaults still apply on inserts.
    compiled = compiled.replace(" NOT NULL", " NULL")
    compiled = compiled.replace(" PRIMARY KEY", "")
    compiled = compiled.replace(" UNIQUE", "")
    return compiled


def sync_schema(verbose=True):
    inspector = inspect(engine)
    added = []
    skipped = []
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                skipped.append(f"table {table.name} created by create_all")
                continue
            existing = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                sql = f"ALTER TABLE `{table.name}` ADD COLUMN {_column_sql(column)}"
                connection.execute(text(sql))
                added.append(f"{table.name}.{column.name}")
                if verbose:
                    print(f"[ADD] {table.name}.{column.name}")
    if verbose:
        if not added:
            print("[OK] Database schema already matches current models.")
        else:
            print(f"[OK] Added {len(added)} missing column(s).")
    return added


if __name__ == "__main__":
    sync_schema()
