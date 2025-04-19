from __future__ import annotations

import logging
import os
import re
from typing import List, Optional

from app.backend.store.db import Pool, Transaction

logger = logging.getLogger(__name__)


class Migration:
    """
    Handles database migrations by executing SQL scripts in order.
    """

    def __init__(self, db_pool: Pool, migrations_dir: Optional[str] = None):
        """
        Initialize the migration handler.

        Args:
            db_pool: Database connection pool
            migrations_dir: Directory containing migration files (defaults to
                'migrations' in the same directory)
        """
        self.db_pool = db_pool

        # Default migrations directory is 'migrations' in the same directory as
        # this file
        if migrations_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.migrations_dir = os.path.join(current_dir, "migrations")
        else:
            self.migrations_dir = migrations_dir

    def _get_migration_files(self) -> List[str]:
        """
        Get a sorted list of migration files from the migrations directory.

        Returns:
            List of migration file paths sorted by filename
        """
        if not os.path.exists(self.migrations_dir):
            raise FileNotFoundError(
                f"Migrations directory not found: {self.migrations_dir}"
            )

        migration_files = []
        for file in os.listdir(self.migrations_dir):
            if file.endswith(".sql"):
                migration_files.append(os.path.join(self.migrations_dir, file))

        # Sort files by their numeric prefix
        return sorted(
            migration_files,
            key=lambda f: self._get_migration_number(os.path.basename(f)),
        )

    def _get_migration_number(self, filename: str) -> int:
        """
        Extract the migration number from a filename.

        Args:
            filename: Migration filename (e.g., '01.user.sql')

        Returns:
            Migration number as integer
        """
        match = re.match(r"^(\d+)", filename)
        if match:
            return int(match.group(1))
        return float("inf")  # Files without numbers will be last

    def _read_migration_file(self, file_path: str) -> str:
        """
        Read the contents of a migration file.

        Args:
            file_path: Path to the migration file

        Returns:
            SQL content of the migration file
        """
        with open(file_path, "r") as f:
            return f.read()

    def _execute_migration(
        self, transaction: Transaction, sql: str, file_path: str
    ) -> bool:
        """
        Execute a migration SQL script.

        Args:
            transaction: Database transaction
            sql: SQL script to execute
            file_path: Path to the migration file (for logging)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Execute the SQL script
            success = transaction.execute(sql)
            if not success:
                logger.error(
                    "Failed to execute migration: "
                    f"{os.path.basename(file_path)}"
                )
                return False
            logger.info(
                "Successfully executed migration: "
                f"{os.path.basename(file_path)}"
            )
            return success
        except Exception as e:
            logger.error(
                "Error executing migration "
                f"{os.path.basename(file_path)}: {str(e)}"
            )
            raise

    def run_migrations(self) -> bool:
        """
        Run all migrations in order.

        Returns:
            True if all migrations were successful

        Raises:
            Exception: If any migration fails
        """
        migration_files = self._get_migration_files()

        if not migration_files:
            logger.info("No migration files found.")
            return False

        logger.info(f"Found {len(migration_files)} migration files to execute")

        # Create a transaction for all migrations
        with self.db_pool.get_transaction() as transaction:
            try:
                # Create migrations table if it doesn't exist
                transaction.execute(
                    """
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL UNIQUE,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                )

                # Get already applied migrations
                applied_migrations = transaction.query(
                    "SELECT filename FROM migrations"
                )
                applied_filenames = {m["filename"] for m in applied_migrations}

                for file_path in migration_files:
                    filename = os.path.basename(file_path)

                    # Skip already applied migrations
                    if filename in applied_filenames:
                        logger.info(
                            f"Skipping already applied migration: {filename}"
                        )
                        continue

                    logger.info(f"Applying migration: {filename}")
                    sql = self._read_migration_file(file_path)

                    # Execute the migration
                    success = self._execute_migration(
                        transaction, sql, file_path
                    )
                    if not success:
                        raise Exception(
                            f"Migration failed: {os.path.basename(file_path)}"
                        )

                    # Record the migration as applied
                    transaction.insert("migrations", {"filename": filename})

                logger.info("All migrations completed successfully")
                return True

            except Exception as e:
                # Transaction will be rolled back automatically by the context
                # manager
                logger.error(f"Migration failed: {str(e)}")
                raise
