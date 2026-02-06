import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt


# Database Connection
engine = create_engine("postgresql+psycopg2://postgres:nazma786@localhost:5432/sales_warehouse")


#Load Monthly Revenue Data

query = """
SELECT
    year,
    month,
    SUM(revenue) AS monthly_revenue
FROM sales_transactions
GROUP BY year, month
ORDER BY year, month;
"""

df = pd.read_sql(query, engine)

# Create a time index
df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-01")
df = df.sort_values("date")

print("Monthly data loaded")
print(df.head())


#Feature Engineering
df["time_index"] = np.arange(len(df))
X = df[["time_index"]]
y = df["monthly_revenue"]


#Train Model
model = LinearRegression()
model.fit(X, y)

print("\n Model trained")


#Evaluate Model
y_pred = model.predict(X)

mae = mean_absolute_error(y, y_pred)
rmse = mean_squared_error(y, y_pred) ** 0.5


print(f"\n MAE: {mae:.2f}")
print(f" RMSE: {rmse:.2f}")


#Forecast Future Revenue (Next 6 Months)
future_steps = 6
last_index = df["time_index"].max()

future_index = np.arange(last_index + 1, last_index + future_steps + 1).reshape(-1, 1)
future_forecast = model.predict(future_index)

future_df = pd.DataFrame({
    "month_index": future_index.flatten(),
    "forecasted_revenue": future_forecast
})

print("\n Forecast for Next 6 Months")
print(future_df)


#Visualization

plt.figure(figsize=(10, 5))
plt.plot(df["date"], y, label="Actual Revenue")
plt.plot(df["date"], y_pred, linestyle="--", label="Predicted Revenue")
plt.title("Sales Revenue Forecasting")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.legend()
plt.tight_layout()
plt.show()

print("\n Sales Forecasting Completed")
