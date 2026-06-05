import streamlit as st
from agents.sql_agent import get_sql_agent, SQLTrackingCallbackHandler, format_agent_output
from services.report_generator import ReportGenerator
from database.query_validator import is_read_only_query
from config import Config
import time
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Database AI Agent",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS (Premium ChatGPT-like dark UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0F172A !important;
        color: #FFFFFF;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #334155;
        width: 280px !important;
    }

    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Chat Messages styling */
    .stChatMessage {
        padding: 1.5rem 1rem !important;
        border-bottom: 1px solid #1E293B !important;
        background-color: transparent !important;
        animation: fadeIn 0.3s ease-out forwards;
    }

    div[data-testimonial="assistant"] {
        background-color: #1E293B !important;
    }

    /* Welcome text styling */
    .welcome-text {
        text-align: center;
        margin-top: 15vh;
        font-size: 28px;
        font-weight: 700;
        color: #CBD5E1;
    }
    
    .subtitle-text {
        text-align: center;
        margin-top: 5px;
        font-size: 16px;
        color: #64748B;
        margin-bottom: 5vh;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Custom classes for reports */
    .report-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .report-header {
        font-size: 22px;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 10px;
    }

    /* Hide Streamlit default tags */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0F172A;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "agent" not in st.session_state:
    try:
        st.session_state.agent = get_sql_agent()
    except Exception as e:
        st.error("Failed to initialize SQL Agent. Please check database connection and environment settings.")
        st.stop()

if "report_gen" not in st.session_state:
    try:
        st.session_state.report_gen = ReportGenerator()
    except Exception as e:
        st.error("Failed to initialize Report Generator. Please check database connection and environment settings.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_report" not in st.session_state:
    st.session_state.active_report = None

# --- Sidebar Content ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #3B82F6; font-size: 20px; font-weight: 700; margin-bottom: 20px;'>💾 Database Agent</h2>", unsafe_allow_html=True)
    
    # New Chat / Reset Button
    if st.button("＋ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.active_report = None
        # Re-initialize the agent to clear context
        st.session_state.agent = get_sql_agent()
        st.rerun()

    st.markdown("<hr style='border: 0.5px solid #334155; margin: 15px 0;'/>", unsafe_allow_html=True)

    # Developer settings
    st.markdown("<div style='color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;'>DEVELOPER TOOLS</div>", unsafe_allow_html=True)
    show_sql = st.toggle("🔍 Show Generated SQL", value=True)
    show_raw_tables = st.toggle("📊 Show Tables in Chat", value=True)

    st.markdown("<hr style='border: 0.5px solid #334155; margin: 15px 0;'/>", unsafe_allow_html=True)

    # Report Generator Controls
    st.markdown("<div style='color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 10px;'>REPORT GENERATOR</div>", unsafe_allow_html=True)
    
    report_options = [
        "Select Report...", 
        "Sales Summary", 
        "Customer Analysis", 
        "Product Performance", 
        "Revenue Breakdown", 
        "Category Breakdown", 
        "Inventory Overview", 
        "Monthly performance"
    ]
    
    selected_report_opt = st.selectbox("Generate standard report", options=report_options, index=0)
    
    if selected_report_opt != "Select Report...":
        report_map = {
            "Sales Summary": "Sales",
            "Customer Analysis": "Customer",
            "Product Performance": "Product",
            "Revenue Breakdown": "Revenue",
            "Category Breakdown": "Category",
            "Inventory Overview": "Inventory",
            "Monthly performance": "Monthly"
        }
        
        # Trigger report generation
        with st.spinner(f"Generating {selected_report_opt}..."):
            try:
                report_type = report_map[selected_report_opt]
                st.session_state.active_report = st.session_state.report_gen.generate_report(report_type)
                # Reset standard messages when report is shown to avoid clutter
                st.session_state.messages = []
            except Exception as e:
                st.error("An error occurred while generating the report. Please verify database availability.")

# --- Main Canvas Layout ---

# 1. Report View mode
if st.session_state.active_report:
    report = st.session_state.active_report
    
    # Back button to return to chat
    if st.button("← Back to Chat"):
        st.session_state.active_report = None
        st.rerun()
        
    st.markdown(f"<div class='report-header'>{report['title']}</div>", unsafe_allow_html=True)
    
    # Summary Card
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Summary")
    st.write(report['summary'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Metrics and Insights Columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='report-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.subheader("Key Metrics")
        st.markdown(report['metrics'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='report-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.subheader("Derived Insights")
        st.markdown(report['insights'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Tabular Output
    st.subheader("Tabular Output")
    st.dataframe(report['table'], use_container_width=True)

# 2. Regular Chat view mode
else:
    # Header Welcome screen if no history
    if not st.session_state.messages:
        st.markdown('<div class="welcome-text">Database AI Agent</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-text">Ask natural language questions about your database tables.</div>', unsafe_allow_html=True)
    else:
        # Display Message History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Show auxiliary data if present in message history
                if "sql" in msg and show_sql:
                    st.code(msg["sql"], language="sql")
                if "df_dict" in msg and show_raw_tables:
                    df = pd.DataFrame(msg["df_dict"])
                    st.dataframe(df, use_container_width=True)

    # Input Box logic
    if prompt := st.chat_input("Message AI Assistant..."):
        # Display user input
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Process Response
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown("*(Analyzing schema and generating query...)*")
            
            # Setup tracking callback
            handler = SQLTrackingCallbackHandler()
            
            try:
                # Invoke SQL agent with tracking callback
                result = st.session_state.agent.invoke(
                    {"input": prompt},
                    config={"callbacks": [handler]}
                )
                
                response_text = format_agent_output(result["output"])
                status_placeholder.markdown(response_text)
                
                # Log message session
                message_data = {"role": "assistant", "content": response_text}
                
                # Capture generated SQL if any query tool was used
                if handler.executed_queries:
                    joined_sql = "\n\n".join(handler.executed_queries)
                    message_data["sql"] = joined_sql
                    if show_sql:
                        st.code(joined_sql, language="sql")
                    
                    # Capture and display tabular representation of the executed SELECT queries
                    # Fetch last executed SELECT query for display
                    last_query = handler.executed_queries[-1]
                    if is_read_only_query(last_query):
                        try:
                            df_result = st.session_state.report_gen._execute_sql(last_query)
                            if not df_result.empty:
                                message_data["df_dict"] = df_result.to_dict()
                                if show_raw_tables:
                                    st.dataframe(df_result, use_container_width=True)
                        except Exception:
                            pass
                            
                st.session_state.messages.append(message_data)
                
            except Exception as e:
                error_msg = str(e)
                # Safe check for database write violations caught by SecureSQLDatabase or native database errors
                if "read-only access" in error_msg.lower() or "access denied" in error_msg.lower() or "privilege" in error_msg.lower():
                    response_text = "This assistant has read-only access to the database and is not permitted to perform data modifications."
                else:
                    response_text = "I encountered an issue querying the database. Please try rephrasing your question or checking query parameters."
                
                status_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
