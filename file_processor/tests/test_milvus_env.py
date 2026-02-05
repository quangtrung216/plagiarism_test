import os
from dotenv import load_dotenv
from pathlib import Path

from pymilvus import connections, db, utility

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

print("HOST =", os.getenv("MILVUS_HOST"))
print("PORT =", os.getenv("MILVUS_PORT"))
print("DB   =", os.getenv("MILVUS_DB"))

# Connect
connections.connect(
    alias="default",
    host=os.getenv("MILVUS_HOST"),
    port=os.getenv("MILVUS_PORT")
)

print("Connected to Milvus")

# Use database
db_name = os.getenv("MILVUS_DB")

if db_name:
    db.using_database(db_name)

print("Using DB:", db_name)

# List collections
cols = utility.list_collections()

print("Collections:", cols)
