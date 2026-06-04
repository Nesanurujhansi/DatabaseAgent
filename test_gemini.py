import os
import sys
sys.path.insert(0, r'c:\chatbot')

from agents.sql_agent import get_sql_agent, SQLTrackingCallbackHandler
from services.report_generator import ReportGenerator

with open("output.log", "w") as f:
    try:
        # Test 1: Agent query on normalized schema
        f.write("=== Test 1: Agent Query (Normalized Schema) ===\n")
        agent = get_sql_agent()
        handler = SQLTrackingCallbackHandler()
        
        result = agent.invoke(
            {"input": "How many customers are there and how many unique products exist?"},
            config={"callbacks": [handler]}
        )
        f.write(f"Result: {result['output']}\n")
        f.write(f"SQL: {handler.executed_queries}\n\n")
        
        # Test 2: Report on normalized schema
        f.write("=== Test 2: Sales Report (JOIN queries) ===\n")
        rg = ReportGenerator()
        report = rg.generate_report("Sales")
        f.write(f"Title: {report['title']}\n")
        f.write(f"Rows in table: {len(report['table'])}\n")
        f.write(f"Summary: {report['summary'][:200]}\n\n")
        
        f.write("All tests passed!\n")
        
    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n")
        traceback.print_exc(file=f)
