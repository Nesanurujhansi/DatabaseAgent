import os
import sys
from agents.sql_agent import get_sql_agent, SQLTrackingCallbackHandler
from database.query_validator import is_read_only_query

def clear_screen():
    """
    Clears the terminal screen based on the OS.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """
    Entry point for the Database AI Agent CLI application.
    """
    clear_screen()
    print("==========================================")
    print("      Welcome to Database AI Agent        ")
    print("==========================================")
    print("Type 'exit' to end the conversation.")
    print("Type 'clear' to reset screen.\n")

    try:
        # Initialize the SQL Agent
        agent = get_sql_agent()
        print("Agent: Hello! I am your database assistant. How can I help you query your database today?\n")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to initialize Database AI Agent: {e}")
        sys.exit(1)

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Agent: Goodbye! Have a great day!")
            break
        
        # Check for clear command
        if user_input.lower() == "clear":
            clear_screen()
            print("Screen cleared. Continue chatting or type 'exit'.\n")
            continue

        # Handle empty input
        if not user_input:
            continue



        try:
            handler = SQLTrackingCallbackHandler()
            # Get response from the agent
            result = agent.invoke(
                {"input": user_input},
                config={"callbacks": [handler]}
            )
            
            print(f"\nAgent: {result['output']}")
            
            # Print tracked SQL queries
            if handler.executed_queries:
                print("\n[Generated SQL Queries]:")
                for q in handler.executed_queries:
                    print(f"  {q}")
            print()
            
        except Exception as e:
            error_msg = str(e)
            if "read-only access" in error_msg.lower():
                print("\nAgent: This assistant has read-only access to the database.\n")
            else:
                print(f"\nAn error occurred: {error_msg}\n")

if __name__ == "__main__":
    main()
