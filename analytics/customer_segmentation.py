import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Database connection

engine = create_engine("postgresql+psycopg2://postgres:nazma786@localhost:5432/sales_warehouse")


# Load required data
query = """
SELECT
    customerid,
    invoicedate,
    revenue
FROM sales_transactions
WHERE customerid IS NOT NULL;
"""

df = pd.read_sql(query, engine)

# Convert invoicedate to datetime (Python thinks invoicedate is a STRING (text), not a datetime. So we need to convert it)
df["invoicedate"] = pd.to_datetime(df["invoicedate"])

print("Data loaded for segmentation")
print(df.head())


# Reference date (last invoice date + 1 day)
reference_date = df["invoicedate"].max() + timedelta(days=1)


# RFM calculation
rfm = df.groupby("customerid").agg({
    "invoicedate": lambda x: (reference_date - x.max()).days,
    "customerid": "count",
    "revenue": "sum"
}).rename(columns={
    "invoicedate": "recency",
    "customerid": "frequency",
    "revenue": "monetary"
})

print("\n RFM Table Created")
print(rfm.head())


# Scaling data (important for ML)
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)


# KMeans clustering
kmeans = KMeans(n_clusters=4, random_state=42)
rfm["cluster"] = kmeans.fit_predict(rfm_scaled)

print("\n Customers segmented into clusters")
print(rfm.head())


# Save segmentation results
rfm.to_csv("data/processed/customer_segments.csv")

print("\n Customer segmentation completed")
