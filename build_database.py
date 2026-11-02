"""Load the churn CSV into a SQLite database (churn.db, table: customers).
Works with the Kaggle Churn_Modelling.csv too: change CSV_FILE below."""
import sqlite3
import pandas as pd

CSV_FILE = "bank_churn_dataset.csv"      # or "Churn_Modelling.csv"
df = pd.read_csv(CSV_FILE).drop(columns=["RowNumber", "Surname"], errors="ignore")

con = sqlite3.connect("churn.db")
df.to_sql("customers", con, if_exists="replace", index=False)
con.close()
print(f"churn.db created: table 'customers' with {len(df)} rows, {len(df.columns)} columns")
