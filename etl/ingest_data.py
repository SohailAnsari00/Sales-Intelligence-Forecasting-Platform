import pandas as pd

# File paths
RAW_DATA_PATH = "data/raw/sales_data.csv"
PROCESSED_DATA_PATH = "data/processed/sales_data_baseline.csv"

def ingest_data():
    # Load dataset
    df = pd.read_csv(RAW_DATA_PATH, encoding="latin1")

    print("✅ Data loaded successfully")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}\n")

    # Display schema
    print("📌 Data Types:")
    print(df.dtypes)
    print("\n")

    # Missing values check
    print("📌 Missing Values:")
    print(df.isnull().sum())
    print("\n")

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    print("✅ Column names standardized")
    print(df.columns.tolist())
    print("\n")

    # Save baseline processed file
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"✅ Baseline data saved to {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    ingest_data()
