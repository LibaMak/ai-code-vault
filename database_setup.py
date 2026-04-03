import os
from typing import Optional

import mysql.connector
from mysql.connector import Error


def load_env_file(env_path: str) -> None:
    """Load key-value pairs from a local .env file into process environment."""
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Prefer .env values for deterministic local setup behavior.
            os.environ[key] = value


def get_db_config() -> dict:
    """Read MySQL configuration from environment variables."""
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "ai_code_vault"),
    }


def create_database_if_missing() -> None:
    """Create the target database if it does not already exist."""
    cfg = get_db_config()
    db_name = cfg["database"]

    connection = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
    )
    cursor = connection.cursor()

    # Database name cannot be a parameter placeholder in MySQL connector,
    # so keep it server-side quoted and sourced from trusted configuration.
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")

    cursor.close()
    connection.close()


def create_tables(connection: mysql.connector.MySQLConnection) -> None:
    """Create required tables for Category 8 (Database Tables)."""
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            content_chunk LONGTEXT NOT NULL,
            vector_embedding_blob LONGBLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_documents_user_id (user_id),
            CONSTRAINT fk_documents_users
                FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query TEXT NOT NULL,
            response_time DECIMAL(6,3) NOT NULL,
            confidence_score DECIMAL(5,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """
    )

    connection.commit()
    cursor.close()


def create_user(
    connection: mysql.connector.MySQLConnection,
    email: str,
    hashed_password: str,
    role: str,
) -> int:
    """Insert a user with a parameterized query (Category 9 security)."""
    cursor = connection.cursor()
    sql = "INSERT INTO users (email, hashed_password, role) VALUES (%s, %s, %s)"
    cursor.execute(sql, (email, hashed_password, role))
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    return user_id


def create_document(
    connection: mysql.connector.MySQLConnection,
    user_id: int,
    filename: str,
    content_chunk: str,
    vector_embedding_blob: Optional[bytes],
) -> int:
    """Insert a document row with parameterized values (Category 9 security)."""
    cursor = connection.cursor()
    sql = (
        "INSERT INTO documents "
        "(user_id, filename, content_chunk, vector_embedding_blob) "
        "VALUES (%s, %s, %s, %s)"
    )
    cursor.execute(sql, (user_id, filename, content_chunk, vector_embedding_blob))
    connection.commit()
    doc_id = cursor.lastrowid
    cursor.close()
    return doc_id


def create_audit_log(
    connection: mysql.connector.MySQLConnection,
    query: str,
    response_time: float,
    confidence_score: float,
) -> int:
    """Insert audit log row with a parameterized query (Category 9 security)."""
    cursor = connection.cursor()
    sql = (
        "INSERT INTO audit_log (query, response_time, confidence_score) "
        "VALUES (%s, %s, %s)"
    )
    cursor.execute(sql, (query, response_time, confidence_score))
    connection.commit()
    log_id = cursor.lastrowid
    cursor.close()
    return log_id


def main() -> None:
    """Entry point: create DB (if needed) and required tables."""
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        load_env_file(env_path)
        create_database_if_missing()
        cfg = get_db_config()

        connection = mysql.connector.connect(**cfg)
        if connection.is_connected():
            create_tables(connection)
            print("Database setup complete: users, documents, audit_log tables are ready.")

        connection.close()

    except Error as exc:
        print(f"MySQL setup failed: {exc}")


if __name__ == "__main__":
    main()
