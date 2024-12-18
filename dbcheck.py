import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def check_database_connection():
    try:
        # Establish a connection to the database
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print("Error connecting to the database:", e)

if __name__ == "__main__":
    check_database_connection()