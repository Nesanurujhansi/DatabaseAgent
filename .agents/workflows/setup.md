---
description: Setup and run the Gemini AI Chatbot
---

1. Ensure Python 3 is installed.
// turbo
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Prepare the environment file:
   ```powershell
   copy .env.example .env
   ```
4. **Action Required**: Open the `.env` file and replace `your_api_key_here` with your actual Google Gemini API key.
5. Run the SQL Agent (CLI):
   ```powershell
   python main.py
   ```
6. **(OR)** Run the Database AI Dashboard:
   ```powershell
   streamlit run app.py
   ```
