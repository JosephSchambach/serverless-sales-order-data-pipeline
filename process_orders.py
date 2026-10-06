import pandas as pd
from dotenv import load_dotenv
import os 

load_dotenv()

bucket_path = os.getenv("BUCKET_PATH")

df = pd.read_parquet(
    path=bucket_path,
    engine="fastparquet"
)

today = pd.Timestamp.now().strftime("%Y-%m-%d")

schema = df.dtypes
print("SCHEMA:")
print(schema)
print("ROWS:")
print(df.shape[0])


required_fields = ["order_id", "customer_id", "ordered_at", "product_sku", "status", "unit_price", "quantity", "discount_pct", "shipping_cost", "currency"]

def set_processed_status(df):
    missing_fields = df[required_fields].isna().any(axis=1)
    df["processed_status"] = missing_fields.map({True: "reject", False: "accept"})
    return df


set_processed_status(df)

df["net"] = df.apply(
    lambda row: (
        row["unit_price"] * row["quantity"]
        - row["unit_price"] * row["quantity"] * row["discount_pct"] / 100
        + row["shipping_cost"]
        if row["processed_status"] == "accept"
        else pd.NA
    ),
    axis=1,
)

print("NUM ACCEPTED: ", (df["processed_status"] == "accept").sum())
print("NUM REJECTED: ", (df["processed_status"] == "reject").sum())
print("NUM NA: ", df["net"].isna().sum())

