import os
import sys
import traceback
import sqlalchemy
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load dotenv explicitly
dotenv_loaded = load_dotenv()

from config import Config
from database.db_connection import get_db_instance
from services.report_generator import ReportGenerator
from agents.sql_agent import get_sql_agent

print("==================================================")
print("     SYSTEM DIAGNOSTIC & VERIFICATION RUNNER     ")
print("==================================================")

def get_masked_key(key):
    if not key:
        return "Not Configured / None"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]} (Length: {len(key)})"

# --- TEST 1: Dotenv & Configurations ---
print("\n[TEST 1] Environment and Configuration Loading")
try:
    print(f"Dotenv loaded explicitly by python: {dotenv_loaded}")
    raw_env_key = os.getenv("GEMINI_API_KEY")
    print(f"Raw GEMINI_API_KEY from os.getenv: {get_masked_key(raw_env_key)}")
    print(f"Config class GEMINI_API_KEY: {get_masked_key(Config.GEMINI_API_KEY)}")
    print(f"Environment variable matches config key: {raw_env_key == Config.GEMINI_API_KEY}")
    print(f"Configured Model Name: {Config.MODEL_NAME}")
    print("PASS")
except Exception as e:
    print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")

# --- TEST 2: Database Connectivity & SQLAlchemy ---
print("\n[TEST 2] Database Connection & SQL Execution")
db_conn_success = False
try:
    db = get_db_instance()
    engine = db._engine
    print(f"Database Engine configured: {engine}")
    
    # Verify connection pool and execution manually
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("SELECT 1")).fetchone()
        print(f"Manual 'SELECT 1' execution output: {result}")
        db_conn_success = True
    print("PASS")
except Exception as e:
    print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")

# --- TEST 3: Schema & Table Discovery ---
print("\n[TEST 3] Table & Schema Discovery")
if db_conn_success:
    try:
        tables = db.get_usable_table_names()
        print(f"Usable Tables Discovered: {tables}")
        
        # Test loading schema info for a table
        if tables:
            sample_table = tables[0]
            schema_info = db.get_table_info([sample_table])
            print(f"Schema loading test for table '{sample_table}': SUCCESS (Length of schema text: {len(schema_info)})")
        else:
            raise ValueError("No tables discovered in database.")
        print("PASS")
    except Exception as e:
        print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")
else:
    print("SKIP (Database connection failed)")

# --- TEST 4: Direct Gemini API Call (Outside LangChain) ---
print("\n[TEST 4] Direct Gemini API Connectivity")
direct_api_success = False
try:
    import google.generativeai as genai
    genai.configure(api_key=Config.GEMINI_API_KEY)
    
    # List models to verify support
    print("Attempting to list available models on active key...")
    supported_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            supported_models.append(m.name)
    print(f"Available Model Endpoints: {supported_models[:5]} (Total: {len(supported_models)})")
    
    # Try calling the configured model directly
    model_name = Config.MODEL_NAME
    # Langchain uses model names like gemini-2.5-flash. Standard SDK prefixes with models/
    clean_model_name = model_name if model_name.startswith("models/") else f"models/{model_name}"
    
    print(f"Sending direct generateContent request to '{clean_model_name}'...")
    model = genai.GenerativeModel(clean_model_name)
    response = model.generate_content("Ping")
    print(f"Direct Response Content: '{response.text.strip()}'")
    direct_api_success = True
    print("PASS")
except Exception as e:
    print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")

# --- TEST 5: LangChain Gemini Connection ---
print("\n[TEST 5] LangChain Gemini connection")
langchain_api_success = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0.0
    )
    print(f"LangChain ChatGoogleGenerativeAI initialized with model '{Config.MODEL_NAME}'")
    res = llm.invoke("Hello, answer with 'Pong'")
    print(f"LangChain Response Content: '{res.content.strip()}'")
    langchain_api_success = True
    print("PASS")
except Exception as e:
    print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")

# --- TEST 6: SQL Agent Initialization & Generation ---
print("\n[TEST 6] SQL Agent Pipeline and Generation")
if langchain_api_success and db_conn_success:
    try:
        agent = get_sql_agent()
        print("SQL Agent initialized.")
        
        # Test routing and SQL Generation step
        test_q = "How many customers are there?"
        print(f"Testing SQL generation for user query: '{test_q}'")
        
        from agents.sql_agent import SQLTrackingCallbackHandler
        handler = SQLTrackingCallbackHandler()
        res = agent.invoke({"input": test_q}, config={"callbacks": [handler]})
        print(f"Agent Output: {res.get('output')}")
        print(f"Executed SQL: {handler.executed_queries}")
        print("PASS")
    except Exception as e:
        print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")
else:
    print("SKIP (Database or LangChain initialization failed)")

# --- TEST 7: Report Generator Integration ---
print("\n[TEST 7] Report Generator Verification")
if db_conn_success:
    try:
        rg = ReportGenerator()
        print("Report Generator initialized.")
        
        # Test Report Query execution without Gemini (Step 6 Report Generator request)
        print("Executing report SQL query manually (without Gemini)...")
        # Let's run a sample report mapping
        query_sales = (
            "SELECT p.product_name, p.category, "
            "SUM(o.quantity) AS total_units_sold, "
            "SUM(o.quantity * p.price) AS total_revenue "
            "FROM orders o "
            "JOIN products p ON o.product_id = p.product_id "
            "GROUP BY p.product_name, p.category "
            "ORDER BY total_revenue DESC"
        )
        df = rg._execute_sql(query_sales)
        print(f"Manual SQL Execution: PASS (Retrieved {len(df)} rows)")
        
        # Test full report generation (with Gemini translation)
        print("Executing full report generation (with Gemini)...")
        res_rep = rg.generate_report("Sales")
        print(f"Report Summary: '{res_rep['summary'][:150]}...'")
        print("PASS")
    except Exception as e:
        print(f"FAIL\nERROR DETAILS:\n{traceback.format_exc()}")
else:
    print("SKIP (Database connection failed)")

print("\n==================================================")
print("             DIAGNOSTICS COMPLETED                ")
print("==================================================")
