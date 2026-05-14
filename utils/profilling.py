import pandas as pd
# this code block below classify columns into numeric, categorical, datetime, and boolean based on simple heuristics
def classify_columns(df):
    profile_types = {
        "numeric": [],
        "categorical": [],
        "boolean": [],
        "datetime": []
    }
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            profile_types["numeric"].append(col)
        elif pd.api.types.is_bool_dtype(dtype):
            profile_types["boolean"].append(col)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            profile_types["datetime"].append(col)
        else:
            profile_types["categorical"].append(col)
    return profile_types

def refine_types(df, profile_types, threshold=10):
    for col in profile_types["numeric"][:]:
        if df[col].nunique() < threshold:
            profile_types["numeric"].remove(col)
            profile_types["categorical"].append(col)
    return profile_types
# this code block creates profiling for the user dataset
def profile_data(df: pd.DataFrame) -> dict:
  
    profile = {}
    profile["shape"] = df.shape
    profile["columns"] = list(df.columns)
    profile["dtypes"] = df.dtypes.astype(str).to_dict()
    profile["missing_values"] = df.isnull().sum().to_dict()
    profile["unique_values"] = df.nunique().to_dict()
    profile["summary_stats"] = df.describe(include="all").fillna("").to_dict()
    
    
    numeric_df = df.select_dtypes(include="number")
    profile["correlation"] = numeric_df.corr().to_dict() if not numeric_df.empty else {}
    
    column_types = classify_columns(df)
    column_types = refine_types(df, column_types)
    profile["column_types"] = column_types
    
    return profile
def profile_to_text(profile: dict) -> str:
    
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
    return '\\n'.join(text)