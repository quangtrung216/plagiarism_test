import os
from dotenv import load_dotenv
import psycopg2
from pathlib import Path


env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv()
print("PASS =", os.getenv("POSTGRES_PASSWORD"))  # test

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

print("Postgres OK")
