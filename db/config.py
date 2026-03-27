import os


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None or value == "" else value


# Milvus
MILVUS_HOST = _env("MILVUS_HOST", "localhost")
MILVUS_PORT = int(_env("MILVUS_PORT", "19530"))
MILVUS_ALIAS = _env("MILVUS_ALIAS", "default")

# Postgres
POSTGRES_HOST = _env("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(_env("POSTGRES_PORT", "5432"))
POSTGRES_DB = _env("POSTGRES_DB", "plagiarism")
POSTGRES_USER = _env("POSTGRES_USER", "plagiarism")
POSTGRES_PASSWORD = _env("POSTGRES_PASSWORD", "plagiarism")

# If you prefer a full DSN, set DATABASE_URL and it will be used.
DATABASE_URL = os.getenv("DATABASE_URL")
