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
    An optimized, low-token SQL Agent that replaces the verbose LangChain SQL Agent.
    It generates and executes database queries in exactly 2 API calls.
    """
    def __init__(self, llm, db):
        self.llm = llm
        self.db = db

    def invoke(self, input_dict: dict, config: dict = None) -> dict:
        question = input_dict.get("input", "")
        
        # 1. Retrieve the database schemas to provide context to the LLM
        schema_info = self.db.get_table_info()
        
        # 2. Call LLM to generate the raw SQL SELECT query in one shot
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
        
        try:
            raw_response = self.llm.invoke(sql_generation_prompt)
            sql_response = extract_text_content(raw_response.content)
            
            # Clean markdown code blocks if the LLM generates them
            sql = sql_response
            if sql.startswith("```"):
                lines = sql.split("\n")
                cleaned_lines = []
                for line in lines:
                    if not line.strip().startswith("```"):
                        cleaned_lines.append(line)
                sql = "\n".join(cleaned_lines)
            sql = sql.strip().rstrip(";")
            
            if not sql:
                return {"output": "Data not available in the database."}
                
            # Log the executed query to any callbacks (like the tracking handler)
            if config and "callbacks" in config:
                for callback in config["callbacks"]:
                    if hasattr(callback, "on_tool_start"):
                        callback.on_tool_start({"name": "sql_db_query"}, sql)

            # 3. Execute the SQL query safely on the database
            # SecureSQLDatabase wrapper will block it if it's not a SELECT query
            query_result = self.db.run(sql)
            
            # 4. Call LLM to format the response based strictly on the query result
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
            
            raw_synthesis = self.llm.invoke(synthesis_prompt)
            agent_response = extract_text_content(raw_synthesis.content)
            return {"output": agent_response}
            
        except Exception as e:
            # Propagate error message to be handled in the UI
            raise e

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
