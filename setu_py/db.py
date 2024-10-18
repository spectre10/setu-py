from psycopg2 import pool
import logging

# DATABASE_URL = "postgresql://watch_user:localtest@localhost:5432/watch_prod_db"
DATABASE_URL = "postgresql://prod_user:GiRtSarFzrf9eGBa@watch-production-1-replica.cnh2gcqstmc3.us-east-1.rds.amazonaws.com:5432/prod_db"

db_pool = None

class Database:
    def __init__(self):
        self.minconn = 1  # Minimum number of connections to keep in the pool
        self.maxconn = 100  # Maximum number of connections in the pool

    def initialize_pool(self):
        global db_pool
        try:
            db_pool = pool.SimpleConnectionPool(
                self.minconn, self.maxconn, DATABASE_URL
            )
            if db_pool:
                logging.info("Connection pool created successfully")
        except Exception as e:
            logging.error(f"Error creating connection pool: {e}")
            raise

    def get_connection(self):
        try:
            return db_pool.getconn()
        except Exception as e:
            logging.error(f"Error getting connection from pool: {e}")
            raise

    def return_connection(self, conn):
        try:
            db_pool.putconn(conn)
        except Exception as e:
            logging.error(f"Error returning connection to pool: {e}")
            raise

    def close_pool(self):
        global db_pool
        if db_pool:
            db_pool.closeall()
            logging.info("Connection pool closed")
