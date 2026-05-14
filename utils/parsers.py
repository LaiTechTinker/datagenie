"""Parse uploaded CSV / XLSX files into rows + column metadata."""
from typing import Tuple, List, Dict, Any
import pandas as pd


def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "number"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    return "string"


def parse_file(path: str, filename: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    name = filename.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(path)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type. Use CSV or XLSX.")

    columns = [
        {"name": col, "type": _infer_type(df[col]), "missing": int(df[col].isna().sum())}
        for col in df.columns
    ]
    # Replace NaN with None for JSON safety
    rows = df.where(pd.notna(df), None).to_dict(orient="records")
    return rows, columns
