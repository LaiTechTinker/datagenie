import pandas as pd

def detect_missing_values(df: pd.DataFrame):
    missing = df.isnull().sum()
    total_rows = len(df)

    suggestions = []

    for col, count in missing.items():
        if count > 0:
            percent = (count / total_rows) * 100

            if percent < 10:
                strategy = "fill with median" if df[col].dtype != "object" else "fill with mode"
            elif percent < 30:
                strategy = "consider filling or dropping rows"
            else:
                strategy = "consider dropping column"

            suggestions.append({
                "type": "missing_values",
                "column": col,
                "missing_count": int(count),
                "percentage": round(percent, 2),
                "suggestion": strategy
            })

    return suggestions


def detect_duplicates(df: pd.DataFrame):
    dup_count = df.duplicated().sum()

    if dup_count > 0:
        return [{
            "type": "duplicates",
            "count": int(dup_count),
            "suggestion": "remove duplicate rows"
        }]

    return []


def detect_outliers(df: pd.DataFrame):
    suggestions = []

    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        count = len(outliers)

        if count > 0:
            suggestions.append({
                "type": "outliers",
                "column": col,
                "count": int(count),
                "lower_bound": float(lower),
                "upper_bound": float(upper),
                "suggestion": "consider removing or capping outliers"
            })

    return suggestions


def generate_cleaning_report(df: pd.DataFrame):
    report = {
        "missing_values": detect_missing_values(df),
        "duplicates": detect_duplicates(df),
        "outliers": detect_outliers(df)
    }

    return report
def format_report_for_table(report: dict):
    table = []

    # Missing values
    for item in report["missing_values"]:
        table.append({
            "issue_type": "missing_values",
            "column": item["column"],
            "count": item["missing_count"],
            "percentage": item["percentage"],
            "suggestion": item["suggestion"]
        })

    # Duplicates
    for item in report["duplicates"]:
        table.append({
            "issue_type": "duplicates",
            "column": "ALL",
            "count": item["count"],
            "percentage": None,
            "suggestion": item["suggestion"]
        })

    # Outliers
    for item in report["outliers"]:
        table.append({
            "issue_type": "outliers",
            "column": item["column"],
            "count": item["count"],
            "percentage": None,
            "suggestion": item["suggestion"]
        })

    return table
# cleaning the data based on the report generated
def clean_dataframe(df: pd.DataFrame):
    df = df.copy()

    # 1. Remove duplicates
    df = df.drop_duplicates()

    # 2. Handle missing values
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype != "object":
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

    # 3. Handle outlier
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df[col] = df[col].clip(lower, upper)

    return df