import pandas as pd


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



def profile_data2(df: pd.DataFrame) -> dict:
    try:
        profile = {}

       
        profile["shape"] = df.shape
        profile["columns"] = list(df.columns)
        profile["dtypes"] = df.dtypes.astype(str).to_dict()
        profile["missing_values"] = df.isnull().sum().to_dict()
        profile["unique_values"] = df.nunique().to_dict()
        profile["summary_stats"] = df.describe(include="all").fillna("").to_dict()

        numeric_df = df.select_dtypes(include="number")
        profile["correlation"] = numeric_df.corr().to_dict() if not numeric_df.empty else {}

        # 
        column_types = classify_columns(df)
        column_types = refine_types(df, column_types)

        profile["column_types"] = column_types

        return profile

    except Exception as e:
        print(f"Error profiling data: {e}")
        return None