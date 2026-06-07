import time
import random
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from database.db_connection import get_db_instance
from config import Config
from langchain_core.callbacks import BaseCallbackHandler

class SQLTrackingCallbackHandler(BaseCallbackHandler):
    """
    Callback handler to track and collect generated SQL queries 
    during agent execution.
    """
    def __init__(self):
        super().__init__()
        self.executed_queries = []

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "")
        # Capture the query sent to the SQL database execution tool
        if tool_name == "sql_db_query" or "query" in tool_name.lower():
            self.executed_queries.append(input_str.strip())

def extract_text_content(content) -> str:
    """
    Safely extracts text content from Google Generative AI responses,
    handling list of parts or raw strings.
    """
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        return "".join(text_parts).strip()
    return str(content).strip()

class CompactSQLAgent:
    """
    An optimized, low-token SQL Agent that dynamically routes database schemas,
    recovers from query execution errors through a self-correction loop,
    and handles API rate limits using exponential backoff.
    """
    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        # Dictionary of tables and descriptions to guide routing
        self.tables_directory = {
            "customers": "unique customer details (names, emails, phone, city)",
            "products": "product names, categories, and unit prices",
            "orders": "links customers to products (quantities, dates, transaction records)",
            "stores": "physical retail store locations",
            "employees": "staff names, positions, salaries, and linked stores",
            "reviews": "ratings and comments on products submitted by customers",
            "suppliers": "vendor details supplying products",
            "inventory": "stock quantities and reorder levels for products",
            "shipments": "carrier names and delivery statuses for orders",
            "payments": "amount paid, payment methods, and statuses for orders",
            "promotions": "discount codes, start/end dates, and discount percentages",
            "returns": "product return reasons and authorization statuses"
        }

    def _call_llm_with_retry(self, prompt: str, max_retries: int = 5) -> str:
        """
        Executes an LLM call wrapping rate limit exceptions (429) 
        with exponential backoff and jitter.
        """
        for i in range(max_retries):
            try:
                raw_response = self.llm.invoke(prompt)
                return extract_text_content(raw_response.content)
            except Exception as e:
                err_msg = str(e)
                # Check for rate limit status (429 / RESOURCE_EXHAUSTED)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if i == max_retries - 1:
                        raise e
                    sleep_time = (2 ** i) + random.uniform(0.1, 1.0)
                    print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
        raise Exception("Failed to execute LLM request due to rate limit errors.")

    def select_relevant_tables(self, question: str) -> list:
        """
        Schema Routing step: Asks Gemini to select only the tables 
        relevant to the user's question.
        """
        tables_info = "\n".join([f"- {name}: {desc}" for name, desc in self.tables_directory.items()])
        prompt = (
            "You are a database router. Given the user question, identify which of the tables listed below "
            "are needed to write a MySQL query to answer the question.\n\n"
            f"Available Tables:\n{tables_info}\n\n"
            f"User Question: {question}\n\n"
            "Rules:\n"
            "- Output only a comma-separated list of the relevant table names.\n"
            "- Do not include markdown code block wrappers, descriptions, or other text.\n"
            "- If no tables are relevant, output: none\n\n"
            "Relevant Tables:"
        )
        
        response = self._call_llm_with_retry(prompt).lower().strip()
        if "none" in response or not response:
            return []
            
        # Parse table names
        selected = [t.strip() for t in re.split(r'[\s,]+', response) if t.strip()]
        # Intersect with available tables to guarantee valid names
        valid_tables = [t for t in selected if t in self.tables_directory]
        return valid_tables

    def self_correct_sql(self, question: str, sql: str, error_msg: str, schema_info: str) -> str:
        """
        SQL Self-Correction: Submits the broken query and database error 
        to the LLM for correction.
        """
        print(f"\n[Self-Correction] Attempting to fix query. Last error: {error_msg}")
        prompt = (
            "You are a MySQL database expert. The previous MySQL query generated to answer the user's question "
            "failed with a database syntax or execution error. Given the schema and error description, correct "
            "the SQL query.\n\n"
            f"Database Schema:\n{schema_info}\n\n"
            f"User Question: {question}\n"
            f"Failed SQL Query: {sql}\n"
            f"Database Error: {error_msg}\n\n"
            "Rules:\n"
            "- Output ONLY the corrected valid MySQL SELECT query. Do not include markdown wraps (like ```sql), explanations, or trailing semicolons.\n"
            "- You must ONLY use SELECT statements.\n\n"
            "Corrected MySQL Query:"
        )
        
        corrected_sql = self._call_llm_with_retry(prompt)
        return self._clean_sql(corrected_sql)

    def _clean_sql(self, sql: str) -> str:
        """
        Cleans markdown formatting and comments from the SQL string.
        """
        if sql.startswith("```"):
            lines = sql.split("\n")
            cleaned_lines = []
            for line in lines:
                if not line.strip().startswith("```"):
                    cleaned_lines.append(line)
            sql = "\n".join(cleaned_lines)
        return sql.strip().rstrip(";")

    def invoke(self, input_dict: dict, config: dict = None) -> dict:
        question = input_dict.get("input", "")
        
        # 1. Perform Schema Routing (Table Selection)
        selected_tables = self.select_relevant_tables(question)
        if not selected_tables:
            # Fallback to all tables if none were resolved
            selected_tables = list(self.tables_directory.keys())
            
        print(f"\n[Schema Routing] Routed tables for query: {selected_tables}")
        
        # 2. Retrieve schemas ONLY for the selected tables
        schema_info = self.db.get_table_info(table_names=selected_tables)
        
        # 3. Call LLM to generate the initial SELECT query
        sql_generation_prompt = (
            "You are a MySQL database expert. Given the database schema below, write a single valid "
            "MySQL SELECT query that retrieves the data necessary to answer the user's question.\n\n"
            f"Database Schema:\n{schema_info}\n\n"
            f"User Question: {question}\n\n"
            "Rules:\n"
            "- Output ONLY the raw SQL query. Do not include markdown code block wrappers (like ```sql), explanations, or trailing semicolons.\n"
            "- You must ONLY use SELECT statements. Never execute write operations (INSERT, UPDATE, DELETE, DROP, ALTER, etc.).\n"
            "- If the question cannot be answered with the schema, output an empty string.\n\n"
            "MySQL SELECT Query:"
        )
        
        sql_response = self._call_llm_with_retry(sql_generation_prompt)
        sql = self._clean_sql(sql_response)
        
        if not sql:
            return {"output": "Data not available in the database."}
            
        # Log the initial query trigger for callbacks
        if config and "callbacks" in config:
            for callback in config["callbacks"]:
                if hasattr(callback, "on_tool_start"):
                    callback.on_tool_start({"name": "sql_db_query"}, sql)

        # 4. Execute the SQL query safely on the database (with self-correction retry)
        try:
            query_result = self.db.run(sql)
        except Exception as e:
            # First attempt failed. Try self-correction.
            sql = self.self_correct_sql(question, sql, str(e), schema_info)
            # Log corrected query to callbacks
            if config and "callbacks" in config:
                for callback in config["callbacks"]:
                    if hasattr(callback, "on_tool_start"):
                        callback.on_tool_start({"name": "sql_db_query"}, sql)
            # Retry execution
            query_result = self.db.run(sql)
            
        # 5. Call LLM to format the response based strictly on the query result
        synthesis_prompt = (
            "You are a helpful database AI agent. Synthesize a professional, concise answer to the "
            "user's question based strictly on the SQL query results. Follow these rules:\n"
            "1. If no data was returned, say: 'Data not available in the database.'\n"
            "2. Do not fabricate, guess, or estimate any numbers, dates, or values not in the results.\n\n"
            f"Question: {question}\n"
            f"SQL Executed: {sql}\n"
            f"Query Result:\n{query_result}\n\n"
            "Answer:"
        )
        
        agent_response = self._call_llm_with_retry(synthesis_prompt)
        return {"output": agent_response}

def get_sql_agent():
    """
    Initializes and returns the optimized CompactSQLAgent.
    """
    llm = ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0.0
    )
    db = get_db_instance()
    return CompactSQLAgent(llm, db)

def format_agent_output(output) -> str:
    """
    Cleans and extracts natural language text from responses.
    """
    if isinstance(output, list):
        text_parts = []
        for part in output:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "".join(text_parts).strip()
    return str(output).strip()
