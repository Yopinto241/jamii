import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="huduma_connect",
        user="postgres",
        password="3698",
        host="localhost",
        port="5432"
    )
    return conn