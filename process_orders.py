import pandas as pd
from dotenv import load_dotenv
import os 
import time

load_dotenv()

BUCKET_PATH = os.getenv("BUCKET_PATH")
SCHEMA = os.getenv("SCHEMA").split(",")
required_fields = os.getenv("REQUIRED_FIELDS").split(",")

final_df = pd.DataFrame()

for file in os.listdir(BUCKET_PATH):
    file_to_process = os.path.join(BUCKET_PATH, file)

    df = pd.read_parquet(
        path=file_to_process,
        engine="fastparquet"
    )
    
    df["processed_at"] = pd.Timestamp.now()
    df["source_file"] = file


    schema = df.dtypes
    print("SCHEMA:")
    print(schema)
    print("ROWS:")
    print(df.shape[0])
    
    final_df = pd.concat([final_df, df], ignore_index=True)

def validate_schema(df, schema):
    # check for missing required fields in the schema
    missing_fields = [field for field in schema if field not in df.columns]
    if missing_fields:
        return False, f"Missing required fields in schema: {missing_fields}"
    
    return True, "Valid schema"

def validate_rows(df, required_fields):
    # check for rows missing required fields
    if df[required_fields].isna().any(axis=1).any():
        return False, "Missing required fields"
    
    # check for invalid quantity
    if (df["quantity"] <= 0).any() or (df["quantity"].isna().any()) or (df["quantity"].dtype not in  ["int32", "int64"]):
        return False, "Invalid quantity"
    
    # check for missing timestamp
    if df["ordered_at"].isna().any():
        return False, "Missing timestamp"
    
    # check for invalid discount percentage
    if (df["discount_pct"] < 0).any() or (df["discount_pct"] > 100).any() or (df["discount_pct"].isna().any()):
        return False, "Invalid discount percentage"
    
    return True, "Valid rows"

schema_passed, schema_message = validate_schema(final_df, SCHEMA)
fields_passed, fields_message = validate_rows(final_df, required_fields)

if (
    schema_passed and fields_passed
):
    print("Valid dataframe")
else:
    print("Rejected dataframe")
    if not schema_passed:
        print(f"Schema validation failed: {schema_message}")
    if not fields_passed:
        print(f"Rows validation failed: {fields_message}")

# final_df["net"] = final_df.apply(
#     lambda row: (
#         row["unit_price"] * row["quantity"]
#         - row["unit_price"] * row["quantity"] * row["discount_pct"] / 100
#         + row["shipping_cost"]
#         if row["processed_status"] == "accept"
#         else pd.NA
#     ),
#     axis=1,
# )

