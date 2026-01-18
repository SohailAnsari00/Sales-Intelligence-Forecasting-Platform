import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path


# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent


# Cleaned data path
DATA_PATH = BASE_DIR / "data" / "processed" / "sales_data_cleaned.csv"


# PostgreSQL connection
engine = create_engine("postgresql+psycopg2://postgres:nazma786@localhost:5432/sales_warehouse")

def load_data_to_postgres():
    df = pd.read_csv(DATA_PATH)

    df.to_sql(
        name="sales_transactions",
        con=engine,
        if_exists="replace",   # overwrite during development
        index=False
    )

    print("Data is successfully loaded into PostgreSQL (sales_transactions table)")

if __name__ == "__main__":
    load_data_to_postgres()
