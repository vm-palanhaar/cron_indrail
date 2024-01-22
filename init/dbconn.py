import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DatabaseConn:
    conn = None

    def __init__(self) -> None:
        self.__connectDb()
    
    def __connectDb(self) -> None:
        print("(DB) Connecting PostgreSQL")

        # PostgreSQL parameters
        db_params = {
            "database": os.getenv("DB_1_PGSQL_NAME"),
            "user": os.getenv("DB_1_PGSQL_USER"),
            "password": os.getenv("DB_1_PGSQL_PWD"),
            "host": os.getenv("DB_1_PGSQL_HOST"),
            "port": os.getenv("DB_1_PGSQL_PORT"),
        }

        try:
            self.conn = psycopg2.connect(**db_params)
            print("(DB) PostgreSQL connection successful")
        
        except (Exception, psycopg2.Error) as error:
            print("(DB) Error connecting to the database:", error)

    def closeConn(self) -> None:
        if self.conn:
            self.conn.close()
            print("(DB) PostgreSQL connection closed")
