"""Core logic: ask questions about the churn database in plain English.
The LLM (Claude) writes a read-only SQL query, we run it safely, then the LLM
explains the result in simple words."""
import re
import sqlite3
import pandas as pd
import anthropic

MODEL = "claude-sonnet-5-5"
DB_PATH = "churn.db"

SCHEMA = """Table: customers (one row per bank customer, 10,000 rows)
- CustomerId        integer  unique id
- CreditScore       integer  350-850
- Geography         text     'France' | 'Germany' | 'Spain'
- Gender            text     'Male' | 'Female'
- Age               integer  years
- Tenure            integer  years with bank (0-10)
- Balance           real     account balance
- NumOfProducts     integer  1-4
- HasCrCard         integer  1 = yes, 0 = no
- IsActiveMember    integer  1 = yes, 0 = no
- EstimatedSalary   real
- Exited            integer  1 = customer churned (left), 0 = stayed
Churn rate = AVG(Exited). Use SQLite syntax."""

SQL_SYSTEM = f"""You convert questions into ONE read-only SQLite query for this database.
{SCHEMA}
Rules: output ONLY the SQL, no explanation, no markdown fences. Use SELECT only.
Limit raw row listings to 50 rows. Round percentages to 1 decimal."""

SUMMARY_SYSTEM = ("You are a bank data analyst. Using the question, the SQL and the result table, "
                  "answer in 2-4 plain sentences. Mention the key numbers. Do not invent data.")

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex)\b", re.I)


def is_safe_sql(sql: str) -> bool:
    """Allow a single SELECT / WITH query only."""
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        return False
    if not re.match(r"^(select|with)\b", s, re.I):
        return False
    return not FORBIDDEN.search(s)


def clean_sql(text: str) -> str:
    return re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.M).strip()


def run_query(sql: str) -> pd.DataFrame:
    if not is_safe_sql(sql):
        raise ValueError("Only a single read-only SELECT query is allowed.")
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)   # read-only connection
    try:
        return pd.read_sql_query(sql, con)
    finally:
        con.close()


def _ask(client, system, content, max_tokens=500):
    msg = client.messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                 messages=[{"role": "user", "content": content}])
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def ask_database(question: str, client=None):
    """Returns (sql, dataframe, answer_text)."""
    client = client or anthropic.Anthropic()      # reads ANTHROPIC_API_KEY
    sql = clean_sql(_ask(client, SQL_SYSTEM, question))
    df = run_query(sql)
    table = df.head(30).to_csv(index=False)
    answer = _ask(client, SUMMARY_SYSTEM,
                  f"Question: {question}\nSQL: {sql}\nResult (CSV):\n{table}", 300)
    return sql, df, answer
