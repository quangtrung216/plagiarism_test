from __future__ import annotations

from typing import Optional

from .config import MILVUS_ALIAS, MILVUS_HOST, MILVUS_PORT


def connect_milvus(
    *,
    host: str = MILVUS_HOST,
    port: int = MILVUS_PORT,
    alias: str = MILVUS_ALIAS,
) -> str:
    """Connect to Milvus via pymilvus and return the connection alias.

    Environment variables:
      - MILVUS_HOST (default: localhost)
      - MILVUS_PORT (default: 19530)
      - MILVUS_ALIAS (default: default)
    """

    try:
        from pymilvus import connections  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Missing dependency 'pymilvus'. Install it in your venv, e.g. 'pip install pymilvus'."
        ) from e

    connections.connect(alias=alias, host=host, port=str(port))
    return alias


def disconnect_milvus(alias: str = MILVUS_ALIAS) -> None:
    try:
        from pymilvus import connections  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Missing dependency 'pymilvus'. Install it in your venv, e.g. 'pip install pymilvus'."
        ) from e

    connections.disconnect(alias=alias)
