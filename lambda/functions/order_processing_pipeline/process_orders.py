import pandas as pd
from dotenv import load_dotenv
import os 
import time

from helpers import validate_schema, validate_rows, transform_orders

load_dotenv()

BUCKET_PATH = os.getenv("RAW_BUCKET_PATH")
PROCESSED_PATH = os.getenv("PROCESSED_PATH")
REJECTED_PATH = os.getenv("REJECTED_PATH")
SCHEMA = os.getenv("SCHEMA").split(",")
required_fields = os.getenv("REQUIRED_FIELDS").split(",")


def handler(event, context):
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

    schema_passed, schema_message = validate_schema(final_df, SCHEMA)
    fields_passed, fields_message = validate_rows(final_df, required_fields)
    final_df = transform_orders(final_df)

    today = time.strftime("%Y-%m-%d")

    if (
        schema_passed and fields_passed
    ):
        print("Valid dataframe")
        final_df.to_parquet(f"{PROCESSED_PATH}{today}/processed_orders.parquet")
    else:
        print("Rejected dataframe")
        final_df.to_parquet(f"{REJECTED_PATH}{today}/rejected_orders.parquet")
        if not schema_passed:
            print(f"Schema validation failed: {schema_message}")
        if not fields_passed:
            print(f"Rows validation failed: {fields_message}")
