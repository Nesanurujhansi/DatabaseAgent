import pandas as pd
from database.db_connection import get_db_instance
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from langchain_core.prompts import PromptTemplate

class ReportGenerator:
    """
    Service class to handle direct database querying and formatting
    for standard business reports. Uses Gemini LLM to construct summaries
    and insights strictly from verified records.
    """
    
    def __init__(self):
        # Fetch the database wrapper
        self.db = get_db_instance()
        
        # Initialize Gemini LLM for summarization & insights
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            google_api_key=Config.GEMINI_API_KEY,
            temperature=0.0
        )

    def _execute_sql(self, query: str) -> pd.DataFrame:
        """
        Helper method to execute a raw SELECT query and return a DataFrame.
        """
        try:
            # Execute query using the SQLAlchemy engine
            engine = self.db._engine
            with engine.connect() as conn:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            raise ValueError(f"Failed to execute query for report: {e}")

    def generate_report(self, report_type: str) -> dict:
        """
        Generates a structured business report based on the report type.
        
        Returns:
            dict: {
                'title': str,
                'summary': str,
                'metrics': str,
                'table': pd.DataFrame,
                'insights': str
            }
        """
        # Determine the SQL query based on report type
        # All queries use JOINs across normalized tables: customers, products, orders
        if report_type == "Sales":
            title = "Sales Performance Report"
            query = (
                "SELECT p.product_name, p.category, "
                "SUM(o.quantity) AS total_units_sold, "
                "SUM(o.quantity * p.price) AS total_revenue "
                "FROM orders o "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY p.product_name, p.category "
                "ORDER BY total_revenue DESC"
            )
        elif report_type == "Customer":
            title = "Customer Analysis Report"
            query = (
                "SELECT c.customer_name, c.email, c.city, "
                "COUNT(o.order_id) AS orders_count, "
                "SUM(o.quantity) AS total_items_bought, "
                "SUM(o.quantity * p.price) AS total_spend "
                "FROM orders o "
                "JOIN customers c ON o.customer_id = c.customer_id "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY c.customer_name, c.email, c.city "
                "ORDER BY total_spend DESC"
            )
        elif report_type == "Product":
            title = "Product Popularity & Pricing Report"
            query = (
                "SELECT p.product_name, p.category, p.price, "
                "SUM(o.quantity) AS units_sold "
                "FROM orders o "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY p.product_name, p.category, p.price "
                "ORDER BY units_sold DESC"
            )
        elif report_type == "Revenue":
            title = "Revenue Analysis by Category"
            query = (
                "SELECT p.category, "
                "SUM(o.quantity * p.price) AS total_revenue, "
                "AVG(p.price) AS average_unit_price "
                "FROM orders o "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY p.category "
                "ORDER BY total_revenue DESC"
            )
        elif report_type == "Category":
            title = "Category Breakdown Summary"
            query = (
                "SELECT p.category, "
                "COUNT(DISTINCT p.product_name) AS unique_products_count, "
                "SUM(o.quantity) AS total_units_sold, "
                "SUM(o.quantity * p.price) AS category_revenue "
                "FROM orders o "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY p.category "
                "ORDER BY category_revenue DESC"
            )
        elif report_type == "Inventory":
            title = "Product Catalog & Inventory Overview"
            query = (
                "SELECT p.product_name, p.category, p.price "
                "FROM products p "
                "ORDER BY p.category, p.product_name"
            )
        elif report_type == "Monthly":
            title = "Geographic & Performance Summary"
            query = (
                "SELECT c.city, p.category, "
                "SUM(o.quantity) AS units_sold, "
                "SUM(o.quantity * p.price) AS total_sales "
                "FROM orders o "
                "JOIN customers c ON o.customer_id = c.customer_id "
                "JOIN products p ON o.product_id = p.product_id "
                "GROUP BY c.city, p.category "
                "ORDER BY total_sales DESC"
            )
        else:
            raise ValueError(f"Unknown report type: {report_type}")


        # Execute query and load into Pandas DataFrame
        df = self._execute_sql(query)
        
        # Guard clause for empty tables
        if df.empty:
            return {
                "title": title,
                "summary": "Data not available in the database.",
                "metrics": "- No active records found.",
                "table": df,
                "insights": "- No insights available."
            }

        # Convert DataFrame to markdown table format for LLM context
        table_markdown = df.to_markdown(index=False)

        # Structure strict prompt to prevent hallucinations
        prompt_template = PromptTemplate(
            input_variables=["title", "table_data"],
            template="""You are a professional database business analyst.
Generate a structured business report for the following table data:

Report Title: {title}

Data Table:
{table_data}

Provide your response in the following strict format:
---SUMMARY---
[A concise 2-3 sentence summary of the data/performance]

---METRICS---
- [Key metric 1 (e.g. Total Revenue, Total Units, etc. calculated from the data)]
- [Key metric 2]
- [Key metric 3]

---INSIGHTS---
- [Insight 1 derived strictly from the records]
- [Insight 2 derived strictly from the records]
- [Insight 3 derived strictly from the records]

Rules:
- Never guess, estimate, or assume values not present in the data.
- Only calculate and report values that are mathematically derived from the table data.
- Do not mention or fabricate columns that do not exist in the table.
"""
        )
        
        prompt = prompt_template.format(title=title, table_data=table_markdown)
        
        # Generate response using Gemini
        # We handle invocation safely
        raw_content = self.llm.invoke(prompt).content
        
        # Safely extract text from response (handles list-of-dicts or raw string)
        if isinstance(raw_content, list):
            text_parts = []
            for part in raw_content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            response = "".join(text_parts).strip()
        else:
            response = str(raw_content).strip()
        
        # Parse the structured sections from response
        summary = ""
        metrics = ""
        insights = ""
        
        parts = response.split("---")
        for part in parts:
            part = part.strip()
            if part.startswith("SUMMARY"):
                summary = part.replace("SUMMARY", "").strip().lstrip("-").strip()
            elif part.startswith("METRICS"):
                metrics = part.replace("METRICS", "").strip()
            elif part.startswith("INSIGHTS"):
                insights = part.replace("INSIGHTS", "").strip()

        # Fallback parsing in case the LLM did not use exact delimiters
        if not summary or not metrics or not insights:
            summary = response
            metrics = "Metrics summary derived from table."
            insights = "Insights summary derived from table."

        return {
            "title": title,
            "summary": summary,
            "metrics": metrics,
            "table": df,
            "insights": insights
        }
