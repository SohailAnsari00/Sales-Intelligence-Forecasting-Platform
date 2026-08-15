import pandas as pd


# Base directory/ file paths

INPUT_PATH = "data/processed/sales_data_baseline.csv"
OUTPUT_PATH = "data/processed/sales_data_Cleaned.csv"


def clean_transform_data():

    # Load baseline data
    df = pd.read_csv(INPUT_PATH)

    print("Baseline data loaded")
    print(f"Initial shape: {df.shape}\n")


    #Remove cancelled transactions --- (Invoices starting with 'C')    
    df = df[~df["Invoice_No"].str.startswith(("C", "A"), na=False)]
    df["Invoice_No"] = df["Invoice_No"].astype(int)
    print(f"After removing cancellations: {df.shape}")


    #Stock_Code
    df = df[df["Stock_Code"].astype(str).str.match(r"^\d{5}")]  ## Keep only rows where StockCode starts with 5 digits
    df["Stock_Code"] = df["Stock_Code"].astype(str).str[:5].astype(int)
    print(f"After removing stock code: {df.shape}")


    #Remove invalid quantities & prices
    df = df[(df["Quantity"] > 0) & (df["Unit_Price"] > 0)]
    print(f"After removing invalid quantity/price: {df.shape}")


    # Handle missing CustomerID 
    df.dropna(subset=["Customer_Id"], inplace=True)  # this will remove the whole row where customer id is null
    df["Customer_Id"] = df["Customer_Id"].astype(int) #changes from float to int 
    print(f"After removing missing customer IDs: {df.shape}")


    #Convert InvoiceDate to datetime
    df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"])


    #Feature Engineering (adding new columns)
    df["Revenue"] = df["Quantity"] * df["Unit_Price"]
    df["Year"] = df["Invoice_Date"].dt.year
    df["Month"] = df["Invoice_Date"].dt.month
    df["Day"] = df["Invoice_Date"].dt.day
    df["Day_of_Week"] = df["Invoice_Date"].dt.day_name()

    # Returns the total count of exact duplicate rows
    duplicate_count = df.duplicated().sum()
    print(f"Total exact duplicates: {duplicate_count}")

    # Displays all copies of the exact duplicate rows then Drops the exact duplicates and updates the DataFrame and then Reset the index so row numbers are sequential again
    df[df.duplicated(keep=False)].sort_values(by=list(df.columns))
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    #Save cleaned dataset
    df.to_csv(OUTPUT_PATH, index=False)


    print("\n")
    print("Cleaned & feature-engineered data saved")
    print(f"Final shape: {df.shape}")


if __name__ == "__main__":
    clean_transform_data()
