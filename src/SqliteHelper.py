import sqlite3
import logging
import os
from config import DB_PATH


class SqliteHelper:

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.setup_logging()
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database and create table
        self.connect()
        self.create_table()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.logger.info("Database connection established")
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")

    def execute(self, query, params=None):
        try:
            if not self.conn:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(f"Query executed successfully: {query}")
        except sqlite3.Error as e:
            self.logger.error(f"Query execution error: {e}")
            raise

    def fetch_all(self, query, params=None):
        try:
            if not self.conn:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Fetch error: {e}")
            raise

    def fetch_one(self, query, params=None):
        try:
            if not self.conn:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"Fetch error: {e}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_table(self):
        try:
            self.execute("""
                CREATE TABLE IF NOT EXISTS xe_gui(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    so_xe TEXT NOT NULL,
                    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.logger.info("Table xe_gui created or already exists")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table: {e}")
            raise

    def edit(self, query):  # INSERT & UPDATE
        try:
            self.execute(query)
            self.logger.info(f"Edit operation successful: {query}")
        except sqlite3.Error as e:
            self.logger.error(f"Edit operation failed: {e}")
            raise

    def select(self, query):  # SELECT
        try:
            return self.fetch_all(query)
        except sqlite3.Error as e:
            self.logger.error(f"Select operation failed: {e}")
            raise

    def getLastRowId(self):
        try:
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error getting last row ID: {e}")
            raise


# Create a singleton instance
db = SqliteHelper()

#test.edit("INSERT INTO xe_gui (so_xe) VALUES ('XXXXX-XXXX')")
#test.edit("UPDATE users SET name='jack' WHERE name = 'john'")
#print(test.select("SELECT * FROM xe_gui"))
