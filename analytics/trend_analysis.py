import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Database Connection
engine = create_engine(
    "postgresql+psycopg2://postgres:nazma786@localhost:5432/sales_warehouse")

# Monthly Revenue Trend
monthly_query = """
SELECT
    year,
    month,
    SUM(revenue) AS monthly_revenue
FROM sales_transactions
GROUP BY year, month
ORDER BY year, month;
"""

df_monthly = pd.read_sql(monthly_query, engine)

print(" Monthly Revenue Trend")
print(df_monthly.head())

# Country-wise Revenue
country_query = """
SELECT
    country,
    SUM(revenue) AS total_revenue
FROM sales_transactions
GROUP BY country
ORDER BY total_revenue DESC;
"""

df_country = pd.read_sql(country_query, engine)

print("\n Country-wise Revenue")
print(df_country.head())


# Plot Monthly Trend
plt.figure(figsize=(10, 5))
plt.plot(df_monthly["month"], df_monthly["monthly_revenue"])
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()


# Plot Top 10 Countries
top_countries = df_country.head(10)

plt.figure(figsize=(10, 5))
plt.bar(top_countries["country"], top_countries["total_revenue"])
plt.title("Top 10 Countries by Revenue")
plt.xlabel("Country")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

print("\n Trend Analysis Completed")

