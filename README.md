# Database AI Chatbot 

A professional Database AI Agent built with Python, Streamlit, and Google Gemini API. This agent allows users to query MySQL databases using natural language and automatically generates structured business reports, while strictly enforcing read-only database access and maintaining low token usage.

## How It Works

The project translates natural language queries into accurate SQL statements, executes those queries against a MySQL database, and synthesizes the data into human-readable text or comprehensive reports. By using a custom token-optimized agent (`CompactSQLAgent`), it bypasses the overhead of traditional conversational loop agents. 

### Workflow
1. **User Input:** The user asks a question (e.g., "What is the revenue generated from Electronics category") or requests a report via the Streamlit UI.
2. **Routing:** 
   - If the user selects the **Agent Chat**, the `CompactSQLAgent` constructs an optimized prompt including the schema and sends it to Gemini to generate the precise SQL query.
   - If the user requests a **Report**, the `ReportGenerator` constructs queries for the specific report type (Sales, Customers, Products, etc.).
3. **Execution & Validation:** The SQL query is passed to the `SecureSQLDatabase` and `QueryValidator`.
   - The query is strictly checked to ensure it only performs `SELECT` operations.
   - Any write/modification query (`INSERT`, `UPDATE`, `DROP`, etc.) is immediately blocked.
4. **Data Retrieval:** The read-only query is executed against the MySQL database.
5. **Output Generation:** 
   - For agent queries, the raw SQL results are sent back to Gemini to synthesize a human-readable answer.
   - For reports, the results are formatted into a markdown report with a generated summary and metrics, and displayed as a Dataframe.
6. **Display:** The results, along with the raw SQL and execution traces, are shown on the Streamlit dashboard.

## Tech Stack
- **Frontend / UI:** [Streamlit](https://streamlit.io/) (for the interactive dashboard)
- **Backend Languages:** Python 3.x
- **LLM / AI:** Google GenAI SDK (`gemini-2.5-flash`)
- **Database:** MySQL
- **Database Connection Framework:** SQLAlchemy & PyMySQL
- **Environment Management:** `python-dotenv`

## Database Schema

The database consists of **6 normalized tables**:

1. **`customers`**: Stores unique customer information.
   - `customer_id` (INT, PRIMARY KEY)
   - `customer_name` (VARCHAR)
   - `email` (VARCHAR, UNIQUE)
   - `phone` (VARCHAR)
   - `city` (VARCHAR)

2. **`products`**: Stores product and pricing information.
   - `product_id` (INT, PRIMARY KEY)
   - `product_name` (VARCHAR, UNIQUE)
   - `category` (VARCHAR)
   - `price` (DECIMAL)

3. **`orders`**: Links customers to products (transaction records).
   - `order_id` (INT, PRIMARY KEY)
   - `customer_id` (INT, FOREIGN KEY)
   - `product_id` (INT, FOREIGN KEY)
   - `quantity` (INT)
   - `order_date` (TIMESTAMP)

4. **`stores`**: Tracks physical store locations.
   - `store_id` (INT, PRIMARY KEY)
   - `store_name` (VARCHAR)
   - `city` (VARCHAR)

5. **`employees`**: Tracks staff members and links them to specific stores.
   - `employee_id` (INT, PRIMARY KEY)
   - `name` (VARCHAR)
   - `position` (VARCHAR)
   - `salary` (DECIMAL)
   - `store_id` (INT, FOREIGN KEY)

6. **`reviews`**: Customer feedback and ratings for products.
   - `review_id` (INT, PRIMARY KEY)
   - `product_id` (INT, FOREIGN KEY)
   - `customer_id` (INT, FOREIGN KEY)
   - `rating` (INT, 1 to 5)
   - `comment` (TEXT)
   - `review_date` (TIMESTAMP)

## How Outputs Are Generated
Outputs are generated in two passes for maximum security and token efficiency:
1. **SQL Generation:** Gemini generates raw SQL based on the database schema.
2. **Synthesis:** The Python backend executes the validated SQL, retrieves the rows, and sends the raw data back to Gemini to translate into a natural, conversational response (or to summarize a report).

## Limitations
- **Read-Only Access:** The assistant cannot modify data, update records, or create new tables.
- **Context Limits:** Extremely large database query results might exceed the LLM's token limit during the synthesis phase (results are intentionally capped at 50 rows).
- **SQL Dialect:** Specifically optimized for MySQL dialects.
- **Local DB Requirement:** Requires a locally running MySQL server to test and operate.

## Security Conditions
The project implements a **Multi-layered Read-Only Security Protocol**:
- **Prompt-Level Blocking is Removed:** To prevent false positives where questions like "delete" (e.g. "which customer deleted their account?") were blocked by the prompt.
- **Database Execution Level Protection (`QueryValidator`):** Uses rigorous Regex rules to intercept the final SQL query right before execution. 
- It actively intercepts and aborts any query containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`, `GRANT`, `REVOKE`, etc.
- **Connection Level:** Strongly recommended to configure the MySQL user in `.env` with `GRANT SELECT ONLY` privileges as the final defense layer.

## How to Run the Project Sequentially

Follow these terminal commands sequentially to set up and run the project from scratch:

**1. Create a Virtual Environment (Optional but recommended):**
```bash
python -m venv venv
venv\Scripts\activate
```

**2. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**3. Set up the Environment Variables:**
Ensure you have a `.env` file in the root directory (copy from `.env.example`).
```env
GEMINI_API_KEY=your_gemini_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=customerss
DB_PORT=3306
```

**4. Setup the Database Schema (Create tables):**
```bash
python database/create_normalized_tables.py
```

**5. Populate Dummy Data into the Database:**
```bash
python database/populate_normalized_data.py
```

**6. Test the AI Connection and Logic Configuration:**
*(This script validates that Gemini can connect, read schema, and generate reports without errors)*
```bash
python test_gemini.py
```

**7. Run the Web Interface (Streamlit Application):**
```bash
streamlit run app.py
```

After running the final command, open your browser and navigate to `http://localhost:8501`.
