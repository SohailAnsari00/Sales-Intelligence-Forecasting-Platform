import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

OUTPUT_PATH = Path("data/processed/rfm_customer_segments.csv")

REFERENCE_DATE = pd.Timestamp("2011-12-10")
FINAL_K = 4


# --------------------------------------------------
# Database
# --------------------------------------------------

def create_db_engine():
    """Create SQLAlchemy engine for MySQL connection."""

    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    


def load_transaction_data(engine):
    """Load required transaction columns from MySQL."""

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

    return df


# --------------------------------------------------
# RFM Calculation
# --------------------------------------------------

def calculate_rfm(df):
    """Calculate Recency, Frequency and Monetary values."""

    last_purchase = df.groupby("Customer_Id")["Invoice_Date"].max().reset_index()

    last_purchase["Recency"] = (REFERENCE_DATE - last_purchase["Invoice_Date"]).dt.days

    frequency = df.groupby("Customer_Id")["Invoice_No"].nunique().reset_index().rename(columns={"Invoice_No": "Frequency"})

    monetary = df.groupby("Customer_Id")["Revenue"].sum().reset_index().rename(columns={"Revenue": "Monetary"})
    

    rfm = last_purchase[["Customer_Id", "Recency"]].merge(frequency, on="Customer_Id").merge(monetary, on="Customer_Id")

    return rfm


# --------------------------------------------------
# RFM Scoring
# --------------------------------------------------

def calculate_rfm_scores(rfm):
    """Assign 1-5 scores to Recency, Frequency and Monetary."""

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

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(int)
        + rfm["F_Score"].astype(int)
        + rfm["M_Score"].astype(int)
    )

    return rfm


# --------------------------------------------------
# KMeans
# --------------------------------------------------

def evaluate_kmeans(rfm_scaled):
    """Evaluate KMeans for K values from 2 to 8."""

    results = []

    for k in range(2, 9):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(rfm_scaled)

        results.append({
            "K": k,
            "Inertia": model.inertia_,
            "Silhouette": silhouette_score(
                rfm_scaled,
                labels
            )
        })

    return pd.DataFrame(results)


def apply_kmeans(rfm):
    """Scale RFM features and apply final KMeans model."""

    features = rfm[
        ["Recency", "Frequency", "Monetary"]
    ]

    scaler = StandardScaler()

    rfm_scaled = scaler.fit_transform(features)

    model = KMeans(
        n_clusters=FINAL_K,
        random_state=42,
        n_init=10
    )

    rfm["Cluster"] = model.fit_predict(rfm_scaled)

    return rfm


# --------------------------------------------------
# Business Segmentation
# --------------------------------------------------

def assign_segment_labels(rfm):
    """Assign business-friendly labels to KMeans clusters."""

    cluster_labels = {
        0: "Regular Customers",
        1: "At-Risk / Inactive",
        2: "VIP Customers",
        3: "High-Value Customers"
    }

    rfm["Segment"] = rfm["Cluster"].map(cluster_labels)

    return rfm


# --------------------------------------------------
# Cluster Analysis
# --------------------------------------------------

def calculate_cluster_summary(rfm):
    """Calculate customer and revenue statistics by cluster."""

    summary = (
        rfm.groupby("Cluster")["Monetary"]
        .agg(["count", "sum", "mean"])
        .rename(columns={
            "count": "Customer_Count",
            "sum": "Total_Revenue",
            "mean": "Average_Revenue"
        })
    )

    summary["Revenue_Pct"] = (
        summary["Total_Revenue"]
        / rfm["Monetary"].sum()
        * 100
    ).round(2)

    return summary


# --------------------------------------------------
# Validation
# --------------------------------------------------

def validate_rfm(rfm):
    """Validate the final RFM dataset."""

    if rfm["Customer_Id"].duplicated().any():
        raise ValueError(
            "Duplicate Customer_Id values found."
        )

    if rfm[["Recency", "Frequency", "Monetary"]].isna().any().any():
        raise ValueError(
            "Missing values found in RFM data."
        )

    if len(rfm) == 0:
        raise ValueError(
            "RFM dataset is empty."
        )


# --------------------------------------------------
# Main Pipeline
# --------------------------------------------------

def main():

    print("Starting RFM analysis...")

    engine = create_db_engine()

    df = load_transaction_data(engine)

    print(f"Loaded {len(df):,} transaction rows.")

    rfm = calculate_rfm(df)

    print(
        f"Calculated RFM for "
        f"{len(rfm):,} customers."
    )

    rfm = calculate_rfm_scores(rfm)

    # Scale RFM features
    features = rfm[
        ["Recency", "Frequency", "Monetary"]
    ]

    scaler = StandardScaler()

    rfm_scaled = scaler.fit_transform(features)

    # Evaluate possible K values
    evaluation = evaluate_kmeans(rfm_scaled)

    print("\nKMeans Evaluation:")
    print(evaluation.round(4).to_string(index=False))

    # Apply final KMeans model
    rfm = apply_kmeans(rfm)

    # Assign business labels
    rfm = assign_segment_labels(rfm)

    # Validate final dataset
    validate_rfm(rfm)

    # Cluster summary
    cluster_summary = calculate_cluster_summary(rfm)

    print("\nCluster Summary:")
    print(cluster_summary.round(2))

    # Save final dataset
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    rfm.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nRFM analysis completed successfully."
    )

    print(
        f"Saved output to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()











# import os
# import pandas as pd
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_score
# from sklearn.preprocessing import StandardScaler

# load_dotenv()

# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")
# host = os.getenv("DB_HOST")
# port = os.getenv("DB_PORT")
# database = os.getenv("DB_NAME")

# engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# query = """
# SELECT
#     Customer_Id,
#     Invoice_No,
#     Invoice_Date,
#     Revenue
# FROM sales_transactions
# """

# df = pd.read_sql(query, engine)

# # Convert Invoice_Date from string to datetime
# df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"])

# print(df.head())
# print(f"Rows loaded: {len(df)}")

# # Reference date: one day after the last transaction
# reference_date = pd.Timestamp("2011-12-10")

# # Find each customer's most recent purchase
# last_purchase = (df.groupby("Customer_Id")["Invoice_Date"].max().reset_index())

# # Calculate recency in days
# last_purchase["Recency"] = (reference_date - last_purchase["Invoice_Date"]).dt.days

# print(last_purchase.head(10))

# # Calculate frequency: number of unique invoices per customer

# frequency = (df.groupby("Customer_Id")["Invoice_No"].nunique().reset_index())

# frequency.rename(columns={"Invoice_No": "Frequency"}, inplace=True)

# print(frequency.head(10))

# # Calculate monetary value: total revenue per customer
# monetary = (df.groupby("Customer_Id")["Revenue"].sum().reset_index())

# monetary.rename(columns={"Revenue": "Monetary"}, inplace=True)

# print(monetary.head(10))

# # Combine Recency, Frequency, and Monetary
# rfm = last_purchase[["Customer_Id", "Recency"]].merge(frequency, on="Customer_Id").merge(monetary,on="Customer_Id")

# print("\nRFM Dataset:")
# print(rfm.head(10))

# print("\nRFM Shape:")
# print(rfm.shape)

# print("\nRFM Statistics:")
# print(rfm[["Recency", "Frequency", "Monetary"]].describe())

# # RFM scoring using quantiles
# rfm["R_Score"] = pd.qcut(
#     rfm["Recency"],
#     5,
#     labels=[5, 4, 3, 2, 1]
# )

# rfm["F_Score"] = pd.qcut(
#     rfm["Frequency"].rank(method="first"),
#     5,
#     labels=[1, 2, 3, 4, 5]
# )

# rfm["M_Score"] = pd.qcut(
#     rfm["Monetary"].rank(method="first"),
#     5,
#     labels=[1, 2, 3, 4, 5]
# )

# print("\nRFM Scores:")
# print(
#     rfm[
#         [
#             "Customer_Id",
#             "Recency",
#             "Frequency",
#             "Monetary",
#             "R_Score",
#             "F_Score",
#             "M_Score"
#         ]
#     ].head(10)
# )

# rfm["RFM_Score"] = (
#     rfm["R_Score"].astype(int)
#     + rfm["F_Score"].astype(int)
#     + rfm["M_Score"].astype(int)
# )

# print("\nTop RFM Customers:")
# print(
#     rfm.sort_values("RFM_Score", ascending=False)[
#         [
#             "Customer_Id",
#             "Recency",
#             "Frequency",
#             "Monetary",
#             "R_Score",
#             "F_Score",
#             "M_Score",
#             "RFM_Score"
#         ]
#     ].head(10)
# )

# print("\nRFM Score Distribution:")
# print(rfm["RFM_Score"].value_counts().sort_index())

# # Features used for customer segmentation
# rfm_features = rfm[["Recency", "Frequency", "Monetary"]]

# # Scale the RFM features
# scaler = StandardScaler()
# rfm_scaled = scaler.fit_transform(rfm_features)

# print("\nScaled RFM data:")
# print(rfm_scaled[:5])

# from sklearn.metrics import silhouette_score

# # Test different numbers of clusters
# inertia = []
# silhouette_scores = []

# for k in range(2, 9):
#     kmeans = KMeans(
#         n_clusters=k,
#         random_state=42,
#         n_init=10
#     )

#     labels = kmeans.fit_predict(rfm_scaled)

#     inertia.append(kmeans.inertia_)
#     silhouette_scores.append(
#         silhouette_score(rfm_scaled, labels)
#     )

# print("\nKMeans Evaluation:")

# for k, inertia_value, silhouette_value in zip(
#     range(2, 9),
#     inertia,
#     silhouette_scores
# ):
#     print(
#         f"K={k} | "
#         f"Inertia={inertia_value:.2f} | "
#         f"Silhouette={silhouette_value:.4f}"
#     )

# # Final KMeans model
# kmeans = KMeans(
#     n_clusters=4,
#     random_state=42,
#     n_init=10
# )

# rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

# print("\nCluster Distribution:")
# print(rfm["Cluster"].value_counts().sort_index())

# print("\nCluster Characteristics:")

# cluster_summary = (rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean().round(2))

# print(cluster_summary)

# cluster_labels = {
#     0: "Regular Customers",
#     1: "At-Risk / Inactive",
#     2: "VIP Customers",
#     3: "High-Value Customers"
# }

# rfm["Segment"] = rfm["Cluster"].map(cluster_labels)

# print("\nFinal Customer Segments:")
# print(
#     rfm[
#         [
#             "Customer_Id",
#             "Recency",
#             "Frequency",
#             "Monetary",
#             "RFM_Score",
#             "Cluster",
#             "Segment"
#         ]
#     ].head(20)
# )

# print("\nVIP Customers:")

# print(
#     rfm[rfm["Cluster"] == 2][
#         [
#             "Customer_Id",
#             "Recency",
#             "Frequency",
#             "Monetary",
#             "RFM_Score"
#         ]
#     ].sort_values("Monetary", ascending=False)
# )

# cluster_revenue = (
#     rfm.groupby("Cluster")["Monetary"]
#     .agg(["count", "sum", "mean"])
#     .round(2)
# )

# print("\nCluster Revenue Contribution:")
# print(cluster_revenue)

# cluster_revenue["Revenue_Pct"] = (
#     cluster_revenue["sum"] / rfm["Monetary"].sum() * 100
# ).round(2)

# print("\nCluster Revenue Contribution:")
# print(cluster_revenue)