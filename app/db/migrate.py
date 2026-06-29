from pathlib import Path

from app.core.db import get_connection


class MigrationRunner:
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def create_migration_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP DEFAULT NOW()
            )
        """)
        self.conn.commit()

    def is_executed(self, version: str) -> bool:
        self.cur.execute("""
            SELECT 1
            FROM schema_migrations
            WHERE version = %s
        """, (version,))

        return self.cur.fetchone() is not None

    def mark_executed(self, version: str):
        self.cur.execute("""
            INSERT INTO schema_migrations(version)
            VALUES (%s)
        """, (version,))

    def run(self):
        self.create_migration_table()

        migration_dir = Path(
            __file__
        ).parent / "migrations"

        files = sorted(
            migration_dir.glob("*.sql")
        )

        if not files:
            print("No migrations found.")
            return

        for file in files:
            version = file.name

            if self.is_executed(version):
                print(f"SKIP  {version}")
                continue

            print(f"RUN   {version}")

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:
                sql = f.read()

            try:
                self.cur.execute(sql)
                self.mark_executed(version)
                self.conn.commit()

                print(f"DONE  {version}")

            except Exception as e:
                self.conn.rollback()

                print(
                    f"FAILED {version}"
                )
                raise e

        print("Migration completed.")

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    runner = MigrationRunner()

    try:
        runner.run()
    finally:
        runner.close()