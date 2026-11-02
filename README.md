# Bank Churn Assistant (LLM + database)

Ask questions about the churn database in plain English. The LLM writes a safe,
read-only SQL query, the database runs it, and the LLM explains the result.

    pip install -r requirements.txt
    python build_database.py
    export ANTHROPIC_API_KEY="your-key"      (Windows: set ANTHROPIC_API_KEY=your-key)
    streamlit run app.py

Get an API key at console.anthropic.com.
Safety: only single SELECT queries are allowed and the database is opened read-only.
