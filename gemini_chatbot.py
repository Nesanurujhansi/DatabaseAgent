import google.generativeai as genai
from config import Config

class GeminiChatbot:
    """
    Core Chatbot class to interact with Google Gemini API.
    Handles conversation history and response generation.
    """
    
    def __init__(self):
        # Validate configuration before initializing
        Config.validate_config()
        
        # Configure the Generative AI library with the provided API key
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Initialize the model with system instructions
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            system_instruction=Config.SYSTEM_INSTRUCTION
        )
        
        # Start a chat session with empty history
        # Gemini SDK manages history automatically when using start_chat()
        self.chat_session = self.model.start_chat(history=[])

    def get_response(self, user_input: str) -> str:
        """
        Sends user input to Gemini and returns the generated response.
        
        Args:
            user_input (str): The message from the user.
            
        Returns:
            str: The AI-generated response.
        """
        if not user_input.strip():
            return "Please enter a valid message."

        try:
            # Send message to the chat session
            response = self.chat_session.send_message(user_input)
            
            # Return the text content of the response
            return response.text
            
        except Exception as e:
            # Handle specific error cases (Network, API issues, etc.)
            error_message = str(e)
            if "api_key" in error_message.lower():
                return "Error: Invalid API Key. Please check your .env file."
            elif "finish_reason" in error_message.lower():
                return "Error: The response was blocked by safety filters."
            else:
                return f"An unexpected error occurred: {error_message}"

    def get_history(self):
        """
        Returns the current conversation history.
        """
        return self.chat_session.history
