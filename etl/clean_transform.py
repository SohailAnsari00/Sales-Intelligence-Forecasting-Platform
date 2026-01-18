import pandas as pd
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "sales_data_baseline.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sales_data_cleaned.csv"


def clean_transform_data():
    # Load baseline data
    df = pd.read_csv(INPUT_PATH)

    print("✅ Baseline data loaded")
    print(f"Initial shape: {df.shape}\n")

    # -----------------------------
    # 1. Handle missing CustomerID
    # -----------------------------
    df = df.dropna(subset=["customerid"])
    print(f"After removing missing customer IDs: {df.shape}")

    # -----------------------------
    # 2. Remove cancelled transactions
    # (Invoices starting with 'C')
    # -----------------------------
    df = df[~df["invoiceno"].str.startswith("C")]
    print(f"After removing cancellations: {df.shape}")

    # -----------------------------
    # 3. Remove invalid quantities & prices
    # -----------------------------
    df = df[(df["quantity"] > 0) & (df["unitprice"] > 0)]
    print(f"After removing invalid quantity/price: {df.shape}")

    # -----------------------------
    # 4. Convert InvoiceDate to datetime
    # -----------------------------
    df["invoicedate"] = pd.to_datetime(df["invoicedate"])

    # -----------------------------
    # 5. Feature Engineering
    # -----------------------------
    df["revenue"] = df["quantity"] * df["unitprice"]
    df["year"] = df["invoicedate"].dt.year
    df["month"] = df["invoicedate"].dt.month
    df["day"] = df["invoicedate"].dt.day
    df["day_of_week"] = df["invoicedate"].dt.day_name()

    # -----------------------------
    # 6. Save cleaned dataset
    # -----------------------------
    df.to_csv(OUTPUT_PATH, index=False)

    print("\n✅ Cleaned & feature-engineered data saved")
    print(f"Final shape: {df.shape}")


if __name__ == "__main__":
    clean_transform_data()
