import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:3698@localhost:5432/huduma_connect")

def get_connection():
    """Return a new PostgreSQL connection"""
    return psycopg2.connect(DATABASE_URL)