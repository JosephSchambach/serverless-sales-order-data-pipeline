import pandas as pd

def validate_schema(df: pd.DataFrame, schema: list):
    missing_fields = [field for field in schema if field not in df.columns]
    if missing_fields:
        return False, f"Missing required fields in schema: {missing_fields}"
    
    return True, "Valid schema"

def validate_rows(df: pd.DataFrame, required_fields: list):
    if df[required_fields].isna().any(axis=1).any():
        return False, "Missing required fields"
    
    if (df["quantity"] <= 0).any() or (df["quantity"].isna().any()) or (df["quantity"].dtype not in  ["int32", "int64"]):
        return False, "Invalid quantity"
    
    if df["ordered_at"].isna().any():
        return False, "Missing timestamp"
    
    if (df["discount_pct"] < 0).any() or (df["discount_pct"] > 100).any() or (df["discount_pct"].isna().any()):
        return False, "Invalid discount percentage"
    
    for field in ["refund_amount", "unit_price", "shipping_cost"]:
        if field not in df.columns or df[field].isna().any() or (df[field] < 0).any():
            return False, f"Invalid {field}"
    
    return True, "Valid rows"

def transform_orders(df: pd.DataFrame):
    df["net"] = df.apply(
        lambda row: (
            row["unit_price"] * row["quantity"]
            - row["unit_price"] * row["quantity"] * row["discount_pct"]
            + row["shipping_cost"]
            - row["refund_amount"]
        ),
        axis=1,
    )
    df["net"] = df["net"].round(2)
    
    df["gross_total"] = (df["unit_price"] * df["quantity"]).round(2)
    
    df["processed_at"] = pd.Timestamp.now()
    df["ordered_at"] = pd.to_datetime(df["ordered_at"])
    df["estimated_delivery_date"] = df["ordered_at"] + pd.to_timedelta(df["days_to_deliver"], unit="d")
    
    return df