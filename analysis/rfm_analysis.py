import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

query = """
SELECT
    Customer_Id,
    Invoice_No,
    Invoice_Date,
    Revenue
FROM sales_transactions
"""

df = pd.read_sql(query, engine)

# Convert Invoice_Date from string to datetime
df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"])

print(df.head())
print(f"Rows loaded: {len(df)}")

# Reference date: one day after the last transaction
reference_date = pd.Timestamp("2011-12-10")

# Find each customer's most recent purchase
last_purchase = (df.groupby("Customer_Id")["Invoice_Date"].max().reset_index())

# Calculate recency in days
last_purchase["Recency"] = (reference_date - last_purchase["Invoice_Date"]).dt.days

print(last_purchase.head(10))

# Calculate frequency: number of unique invoices per customer

frequency = (df.groupby("Customer_Id")["Invoice_No"].nunique().reset_index())

frequency.rename(columns={"Invoice_No": "Frequency"}, inplace=True)

print(frequency.head(10))

# Calculate monetary value: total revenue per customer
monetary = (df.groupby("Customer_Id")["Revenue"].sum().reset_index())

monetary.rename(columns={"Revenue": "Monetary"}, inplace=True)

print(monetary.head(10))

# Combine Recency, Frequency, and Monetary
rfm = last_purchase[["Customer_Id", "Recency"]].merge(frequency, on="Customer_Id").merge(monetary,on="Customer_Id")

print("\nRFM Dataset:")
print(rfm.head(10))

print("\nRFM Shape:")
print(rfm.shape)

print("\nRFM Statistics:")
print(rfm[["Recency", "Frequency", "Monetary"]].describe())

# RFM scoring using quantiles
rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels=[5, 4, 3, 2, 1]
)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

print("\nRFM Scores:")
print(
    rfm[
        [
            "Customer_Id",
            "Recency",
            "Frequency",
            "Monetary",
            "R_Score",
            "F_Score",
            "M_Score"
        ]
    ].head(10)
)

rfm["RFM_Score"] = (
    rfm["R_Score"].astype(int)
    + rfm["F_Score"].astype(int)
    + rfm["M_Score"].astype(int)
)

print("\nTop RFM Customers:")
print(
    rfm.sort_values("RFM_Score", ascending=False)[
        [
            "Customer_Id",
            "Recency",
            "Frequency",
            "Monetary",
            "R_Score",
            "F_Score",
            "M_Score",
            "RFM_Score"
        ]
    ].head(10)
)

print("\nRFM Score Distribution:")
print(rfm["RFM_Score"].value_counts().sort_index())

# Features used for customer segmentation
rfm_features = rfm[["Recency", "Frequency", "Monetary"]]

# Scale the RFM features
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_features)

print("\nScaled RFM data:")
print(rfm_scaled[:5])

from sklearn.metrics import silhouette_score

# Test different numbers of clusters
inertia = []
silhouette_scores = []

for k in range(2, 9):
    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(rfm_scaled)

    inertia.append(kmeans.inertia_)
    silhouette_scores.append(
        silhouette_score(rfm_scaled, labels)
    )

print("\nKMeans Evaluation:")

for k, inertia_value, silhouette_value in zip(
    range(2, 9),
    inertia,
    silhouette_scores
):
    print(
        f"K={k} | "
        f"Inertia={inertia_value:.2f} | "
        f"Silhouette={silhouette_value:.4f}"
    )

# Final KMeans model
kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

print("\nCluster Distribution:")
print(rfm["Cluster"].value_counts().sort_index())

print("\nCluster Characteristics:")

cluster_summary = (
    rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]]
    .mean()
    .round(2)
)

print(cluster_summary)