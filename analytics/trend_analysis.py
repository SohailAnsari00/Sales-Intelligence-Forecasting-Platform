import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL connection
engine = create_engine(
    "postgresql+psycopg2://postgres:nazma786@localhost:5432/sales_warehouse"
)

# Monthly revenue trend
query = """
SELECT
    year,
    month,
    SUM(revenue) AS monthly_revenue
FROM sales_transactions
GROUP BY year, month
ORDER BY year, month;
"""

df_monthly = pd.read_sql(query, engine)

print("✅ Monthly revenue data loaded")
print(df_monthly.head())
