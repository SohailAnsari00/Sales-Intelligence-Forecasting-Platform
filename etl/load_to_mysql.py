import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Load cleaned data
df = pd.read_csv("data/processed/sales_data_cleaned.csv")

# MySQL connection

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# Load data into MySQL
df.to_sql("sales_transactions", con=engine, if_exists="replace", index=False)

print(f"Successfully loaded {len(df)} rows into MySQL.")