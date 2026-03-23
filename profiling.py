import pandas as pd
from pathlib import Path

def profile_data(df:pd.DataFrame) -> dict:
 try:
    profile = {}

    # Basic info
    profile["shape"] = df.shape
    profile["columns"] = list(df.columns)
    profile["dtypes"] = df.dtypes.astype(str).to_dict()

    # Missing values
    profile["missing_values"] = df.isnull().sum().to_dict()

    # Unique values
    profile["unique_values"] = df.nunique().to_dict()
    # info
    # profile["info"] = df.info()

    # Summary statistics
    profile["summary_stats"] = df.describe(include="all").fillna("").to_dict()

    # Correlation (only numeric)
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        profile["correlation"] = numeric_df.corr().to_dict()
    else:
        profile["correlation"] = {}

    return profile
 except Exception as e:
    print(f"Error profiling data: {e}")
    return None

def profile_to_text(profile: dict) -> str:
    """Convert profile dict into text for LLM"""
    text = []

    text.append(f"Dataset shape: {profile['shape']}")
    text.append(f"Columns: {profile['columns']}")
    text.append(f"Data types: {profile['dtypes']}")

    text.append("Missing values:")
    text.append(str(profile["missing_values"]))

    text.append("Unique values:")
    text.append(str(profile["unique_values"]))

    text.append("Summary stats:")
    text.append(str(profile["summary_stats"]))

    text.append("Correlations:")
    text.append(str(profile["correlation"]))

    return "\n".join(text)