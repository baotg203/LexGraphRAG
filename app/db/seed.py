from pathlib import Path
import importlib.util

from app.core.db import get_connection


class SeederRunner:
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def create_seed_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_seeders (
                name VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP DEFAULT NOW()
            )
        """)
        self.conn.commit()

    def is_executed(self, name: str) -> bool:
        self.cur.execute("""
            SELECT 1
            FROM schema_seeders
            WHERE name = %s
        """, (name,))

        return self.cur.fetchone() is not None

    def mark_executed(self, name: str):
        self.cur.execute("""
            INSERT INTO schema_seeders(name)
            VALUES (%s)
        """, (name,))

    def load_seeder(self, path: Path):
        spec = importlib.util.spec_from_file_location(
            path.stem,
            path
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def run(self):
        self.create_seed_table()

        seeder_dir = (
            Path(__file__).parent
            / "seeders"
        )

        files = sorted(
            seeder_dir.glob("*_seeder.py")
        )

        if not files:
            print("No seeders found.")
            return

        for file in files:
            name = file.name

            if self.is_executed(name):
                print(f"SKIP  {name}")
                continue

            print(f"RUN   {name}")

            try:
                module = self.load_seeder(file)

                if not hasattr(module, "run"):
                    raise Exception(
                        f"{name} must define run(cur)"
                    )

                module.run(self.cur)

                self.mark_executed(name)

                self.conn.commit()

                print(f"DONE  {name}")

            except Exception as e:
                self.conn.rollback()

                print(f"FAILED {name}")

                raise e

        print("Seed completed.")

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    runner = SeederRunner()

    try:
        runner.run()
    finally:
        runner.close()