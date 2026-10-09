from sqlalchemy import text

from db.engine import engine


def migrate():

    print("=" * 60)
    print("IntelliResolve - Phase 7 Migration")
    print("=" * 60)

    sql = """
    CREATE TABLE IF NOT EXISTS live_alerts (

        id INT AUTO_INCREMENT PRIMARY KEY,

        alert_type VARCHAR(100)
            NOT NULL,

        severity VARCHAR(30)
            NOT NULL DEFAULT 'medium',

        title VARCHAR(255)
            NOT NULL,

        message TEXT NULL,

        issue_id INT NULL,

        department_id INT NULL,

        status VARCHAR(50)
            NOT NULL DEFAULT 'active',

        created_at DATETIME
            DEFAULT CURRENT_TIMESTAMP,

        acknowledged_at DATETIME NULL,

        resolved_at DATETIME NULL,

        INDEX idx_alert_status(status),

        INDEX idx_alert_issue(issue_id),

        INDEX idx_alert_department(department_id),

        FOREIGN KEY(issue_id)
            REFERENCES issues(id),

        FOREIGN KEY(department_id)
            REFERENCES departments(id)
    )
    """

    with engine.begin() as connection:

        connection.execute(
            text(sql)
        )

    print(
        "[READY] live_alerts"
    )

    print(
        "Phase 7 migration completed."
    )


if __name__ == "__main__":
    migrate()