import time
from typing import Dict, Generator, Tuple

import docker
import psycopg2
import pytest
from psycopg2.errors import OperationalError

from app.backend.store import Store
from app.backend.store.db import Pool
from app.backend.store.migration import Migration


@pytest.fixture(scope="session")
def postgres_container() -> (
    Generator[
        Tuple[docker.models.containers.Container, Dict[str, str]], None, None
    ]
):
    """Start a Postgres container with pgvector for testing"""
    client = docker.from_env()

    postgres_config = {
        "host": "localhost",
        "port": None,
        "dbname": "testdb",
        "user": "test",
        "password": "test",
    }

    # Pull and start container
    container = client.containers.run(
        "pgvector/pgvector:pg17",
        environment={
            "POSTGRES_DB": postgres_config["dbname"],
            "POSTGRES_USER": postgres_config["user"],
            "POSTGRES_PASSWORD": postgres_config["password"],
        },
        ports={"5432/tcp": None},  # Random port
        detach=True,
    )

    # Wait for container to be ready with proper retry logic
    max_retries = 10
    retry_delay = 1

    for i in range(max_retries):
        try:
            container.reload()  # Refresh container info
            port = container.ports["5432/tcp"][0]["HostPort"]
            postgres_config["port"] = port

            # Try to connect to verify database is ready
            conn = psycopg2.connect(
                host="localhost",
                port=port,
                dbname="testdb",
                user="test",
                password="test",
                connect_timeout=3,
            )
            conn.close()
            break
        except (OperationalError, KeyError) as e:
            if i == max_retries - 1:
                container.stop()
                container.remove()
                pytest.fail(
                    f"Could not connect to postgres container: {str(e)}"
                )
            time.sleep(retry_delay)

    yield (postgres_container, postgres_config)

    # Cleanup
    container.stop()
    container.remove()


@pytest.fixture(scope="session")
def db_pool(postgres_container) -> Pool:
    """Create a database pool for testing"""

    container, postgres_config = postgres_container

    try:
        pool = Pool(
            host=postgres_config["host"],
            port=postgres_config["port"],
            dbname=postgres_config["dbname"],
            user=postgres_config["user"],
            password=postgres_config["password"],
        )

        # Run migrations using Migration class
        with pool.get_transaction() as transaction:
            # Enable vector extension with timeout
            transaction.execute("SET statement_timeout = '10s'")
            transaction.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        migration = Migration(pool)
        assert migration.run_migrations()

        return pool
    except Exception as e:
        pytest.fail(f"Failed to initialize test database: {str(e)}")


@pytest.fixture(scope="session")
def store(db_pool: Pool) -> Store:
    return Store(db_pool)