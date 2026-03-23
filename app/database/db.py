import os
import psycopg2

# Get the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Optional: test connection
cursor.execute("SELECT 1;")
print(cursor.fetchone())  # should print (1,)