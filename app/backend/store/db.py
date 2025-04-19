from __future__ import annotations

from threading import Lock
from typing import Any, Dict, List, Optional, Union

import psycopg2
from psycopg2 import pool
from psycopg2.extras import Json, RealDictCursor


class Pool:
    """
    A helper class that wraps PostgreSQL database operations with connection
    pooling. It can either be a global singleton-esque or a local instance
    """

    __instance: Optional[Pool] = None
    __lock = Lock()

    def __init__(
        self,
        connection_string: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_connections: int = 1,
        max_connections: int = 10,
    ):
        """
        Initialize the PostgreSQL database connection pool.

        Args:
            connection_string: PostgreSQL connection string. If None, will try
                to use environment variables.
            min_connections: Minimum number of connections to keep in the pool
            max_connections: Maximum number of connections allowed in the pool
        """
        if connection_string is None:
            # Try to build connection string from environment variables
            db_host = host or "localhost"
            db_port = port or "5432"
            db_name = dbname or "postgres"
            db_user = user or "postgres"
            db_password = password or ""

            connection_string = (
                f"postgresql://{db_user}:{db_password}@{db_host}:"
                f"{db_port}/{db_name}"
            )

        self.__connection_string = connection_string

        # Initialize the connection pool
        self.__pool = pool.ThreadedConnectionPool(
            min_connections, max_connections, self.__connection_string
        )

    @classmethod
    def get_instance(
        cls,
        connection_string: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_connections: int = 1,
        max_connections: int = 10,
    ) -> Pool:
        """Get the optional singleton instance of the Pool."""
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = Pool(
                        connection_string=connection_string,
                        host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password,
                        min_connections=min_connections,
                        max_connections=max_connections,
                    )
        return cls.__instance

    def __get_connection(self):
        """Get a connection from the pool."""
        return self.__pool.getconn()

    def get_transaction(self):
        """Get a new transaction with a dedicated connection from the pool."""
        conn = self.__get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return Transaction(conn, cursor, self.__pool)

    def __enter__(self):
        """Context manager support - returns a transaction."""
        return self.get_transaction()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - should never be called directly on Pool."""
        if exc_type:
            raise exc_type(exc_val)
        return False


class Transaction:
    """
    Represents a database transaction with its own connection and cursor.
    """

    def __init__(
        self,
        conn: psycopg2.extensions.connection,
        cursor: psycopg2.extensions.cursor,
        pool_instance: pool.ThreadedConnectionPool,
    ):
        self.__conn = conn
        self.__cursor = cursor
        self.__pool = pool_instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception occurred, commit the transaction
            self.__conn.commit()
        else:
            # An exception occurred, rollback the transaction
            self.__conn.rollback()

        # Close cursor
        self.__cursor.close()

        # Return the connection to the pool if we have a pool reference
        if self.__pool:
            self.__pool.putconn(self.__conn)
        else:
            self.__conn.close()

        # Don't suppress exceptions
        return False

    def execute(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Execute a query without returning results.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            True if successful, False otherwise
        """
        try:
            self.__cursor.execute(query, params)
            self.__conn.commit()
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            self.__conn.rollback()
            return False

    def query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            List of dictionaries representing the query results
        """
        try:
            self.__cursor.execute(query, params)
            results = self.__cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error executing query: {e}")
            self.__conn.rollback()
            return []

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """
        Insert a record into a table.

        Args:
            table: Table name
            data: Dictionary of column names and values

        Returns:
            ID of the inserted record if available, None otherwise
        """
        # Convert any dictionary values to JSONB format
        processed_data = {}
        for k, v in data.items():
            if isinstance(v, dict) or isinstance(v, list) and k != "sources":
                processed_data[k] = Json(v)
            elif isinstance(v, list) and k == "sources":
                # Special handling for sources array
                processed_data[k] = v
            else:
                processed_data[k] = v

        columns = ", ".join(f'"{col}"' for col in processed_data.keys())
        placeholders = ", ".join(["%s"] * len(processed_data))
        values = tuple(processed_data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES " f"({placeholders})"

        try:
            self.__cursor.execute(query, values)
            self.__conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            self.__conn.rollback()
            raise e

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        condition_params: tuple,
    ) -> int:
        """
        Update records in a table.

        Args:
            table: Table name
            data: Dictionary of column names and values to update
            condition: WHERE clause of the update statement
            condition_params: Parameters for the condition

        Returns:
            The affected row count
        """
        # Convert any dictionary values to JSONB format
        processed_data = {}
        for k, v in data.items():
            if isinstance(v, dict) or isinstance(v, list) and k != "sources":
                processed_data[k] = Json(v)
            elif isinstance(v, list) and k == "sources":
                # Special handling for sources array
                processed_data[k] = v
            else:
                processed_data[k] = v

        set_clause = ", ".join(
            [f'"{key}" = %s' for key in processed_data.keys()]
        )
        values = tuple(processed_data.values()) + condition_params

        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

        try:
            self.__cursor.execute(query, values)
            self.__conn.commit()
            return self.__cursor.rowcount
        except Exception as e:
            print(f"Error executing query: {e}")
            self.__conn.rollback()
            return 0

    def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        constraint: str,
    ) -> Optional[int]:
        """
        Upsert a record into a table (update if exists, insert if not).

        Args:
            table: Table name
            data: Dictionary of column names and values
            constraint: The unique constraint to use for conflict detection
                (e.g., "id", "email")

        Returns:
            ID of the upserted record if available, None otherwise
        """
        # Convert any dictionary values to JSONB format
        processed_data = {}
        for k, v in data.items():
            if isinstance(v, dict) or isinstance(v, list) and k != "sources":
                processed_data[k] = Json(v)
            elif isinstance(v, list) and k == "sources":
                # Special handling for sources array
                processed_data[k] = v
            else:
                processed_data[k] = v

        columns = ", ".join(f'"{col}"' for col in processed_data.keys())
        placeholders = ", ".join(["%s"] * len(processed_data))
        values = tuple(processed_data.values())

        update_clause = ", ".join(
            [f"{key} = EXCLUDED.{key}" for key in processed_data.keys()]
        )

        query = (
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
            f"ON CONFLICT ({constraint}) DO UPDATE SET {update_clause} "
            f"RETURNING id"
        )

        try:
            self.__cursor.execute(query, values)
            result = self.__cursor.fetchone()
            self.__conn.commit()
            return result["id"] if result else None
        except Exception as e:
            print(f"Error upserting data: {e}")
            self.__conn.rollback()
            return None

    def delete(self, table: str, condition: str, params: tuple) -> int:
        """
        Delete records from a table.

        Args:
            table: Table name
            condition: WHERE clause of the delete statement
            params: Parameters for the condition

        Returns:
            The affected row count
        """
        query = f"DELETE FROM {table} WHERE {condition}"

        try:
            self.__cursor.execute(query, params)
            self.__conn.commit()
            return self.__cursor.rowcount
        except Exception as e:
            print(f"Error executing query: {e}")
            self.__conn.rollback()
            return False

    def get_by_id(
        self, table: str, id_value: Union[int, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get a record by its ID.

        Args:
            table: Table name
            id_value: ID value to look up

        Returns:
            Dictionary representing the record, or None if not found
        """
        query = f"SELECT * FROM {table} WHERE id = %s"

        try:
            self.__cursor.execute(query, (id_value,))
            results = self.__cursor.fetchall()
            return results[0] if results else None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def vector_search(
        self,
        table: str,
        embedding_column: str,
        query_vector: List[float],
        limit: int = 10,
        distance_type: str = "l2",
        where_clause: Optional[str] = None,
        where_params: Optional[tuple] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using pgvector.

        Args:
            table: Table name
            embedding_column: Name of the vector column
            query_vector: Query vector as a list of floats
            limit: Maximum number of results to return
            distance_type: Type of distance to use ('l2', 'inner_product', or 'cosine')
            where_clause: Optional WHERE clause for additional filtering
            where_params: Parameters for the WHERE clause

        Returns:
            List of dictionaries containing the results
        """
        # Convert distance type to operator
        distance_ops = {"l2": "<->", "inner_product": "<#>", "cosine": "<=>"}
        operator = distance_ops.get(distance_type, "<->")

        # Build the query
        query = f"SELECT *, ({embedding_column} {operator} %s::vector) as distance FROM {table}"
        params = [query_vector]

        if where_clause:
            query += f" WHERE {where_clause}"
            if where_params:
                params.extend(where_params)

        query += f" ORDER BY ({embedding_column} {operator} %s::vector)"
        params.append(query_vector)  # Add query_vector again for ORDER BY

        if limit:
            query += f" LIMIT {limit}"

        try:
            self.__cursor.execute(query, params)
            return [dict(row) for row in self.__cursor.fetchall()]
        except Exception as e:
            print(f"Error executing vector search: {e}")
            return []
