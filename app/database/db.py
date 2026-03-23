import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set!")

def get_connection():
    """Return a new PostgreSQL connection"""
    return psycopg2.connect(DATABASE_URL)