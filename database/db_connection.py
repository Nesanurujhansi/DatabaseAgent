from sqlalchemy import create_engine
from langchain_community.utilities.sql_database import SQLDatabase
from database.query_validator import is_read_only_query
from config import Config

class SecureSQLDatabase(SQLDatabase):
    """
    A secure subclass of SQLDatabase that intercepts all database executions 
    to validate that only read-only queries are executed.
    """
    
    def run(self, command: str, fetch: str = "all", include_columns: bool = False, **kwargs) -> str:
        """
        Validates the SQL query before execution.
        Raises ValueError if query contains data modification statements.
        """
        if not is_read_only_query(command):
            raise ValueError("This assistant has read-only access to the database.")
            
        return super().run(command, fetch, include_columns, **kwargs)

def get_db_instance() -> SecureSQLDatabase:
    """
    Creates and returns a SecureSQLDatabase instance configured using 
    settings from the Config class.
    """
    # Build Connection URL (using PyMySQL connector for MySQL compatibility)
    connection_url = (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
        f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    )
    
    # Initialize SQLAlchemy connection engine
    engine = create_engine(connection_url)
    
    # Return secure database wrapper
    return SecureSQLDatabase(engine)
