from sqlalchemy import text

from db.engine import engine


ALTER_STATEMENTS = [

    """
    ALTER TABLE issues
    ADD COLUMN assigned_user_id INT NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN sla_deadline DATETIME NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN investigation_started_at DATETIME NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN resolved_at DATETIME NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN closed_at DATETIME NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN resolution_notes TEXT NULL
    """,

    """
    ALTER TABLE issues
    ADD COLUMN resolution_status VARCHAR(50) NULL
    """,

]


def column_exists(connection, column_name):

    result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'issues'
            AND COLUMN_NAME = :column_name
            """
        ),
        {
            "column_name": column_name
        },
    )

    return result.scalar() > 0


COLUMN_DEFINITIONS = {
    "assigned_user_id": """
        ALTER TABLE issues
        ADD COLUMN assigned_user_id INT NULL
    """,

    "sla_deadline": """
        ALTER TABLE issues
        ADD COLUMN sla_deadline DATETIME NULL
    """,

    "investigation_started_at": """
        ALTER TABLE issues
        ADD COLUMN investigation_started_at DATETIME NULL
    """,

    "resolved_at": """
        ALTER TABLE issues
        ADD COLUMN resolved_at DATETIME NULL
    """,

    "closed_at": """
        ALTER TABLE issues
        ADD COLUMN closed_at DATETIME NULL
    """,

    "resolution_notes": """
        ALTER TABLE issues
        ADD COLUMN resolution_notes TEXT NULL
    """,

    "resolution_status": """
        ALTER TABLE issues
        ADD COLUMN resolution_status VARCHAR(50) NULL
    """,
}


def migrate():

    print("=" * 60)
    print("IntelliResolve Phase 5 Migration")
    print("=" * 60)

    with engine.begin() as connection:

        for column, statement in COLUMN_DEFINITIONS.items():

            if column_exists(
                connection,
                column,
            ):

                print(
                    f"[SKIP] {column} already exists"
                )

            else:

                connection.execute(
                    text(statement)
                )

                print(
                    f"[ADD] {column}"
                )

    print("\nMigration completed.")


if __name__ == "__main__":
    migrate()