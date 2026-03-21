import pandas as pd
import plotly.express as px

def apply_aggregation(df, spec):
    agg = spec.get("aggregation", "none")
    x = spec.get("x_column")
    y = spec.get("y_column")

    if agg == "none" or y is None:
        return df

    if agg == "sum":
        return df.groupby(x)[y].sum().reset_index()

    elif agg == "mean":
        return df.groupby(x)[y].mean().reset_index()

    elif agg == "count":
        return df.groupby(x)[y].count().reset_index()

    return df


def generate_chart(df: pd.DataFrame, spec: dict):
    chart_type = spec.get("chart_type")
    x = spec.get("x_column")
    y = spec.get("y_column")

    df_processed = apply_aggregation(df, spec)

    if chart_type == "line":
        fig = px.line(df_processed, x=x, y=y)

    elif chart_type == "bar":
        fig = px.bar(df_processed, x=x, y=y)

    elif chart_type == "scatter":
        fig = px.scatter(df_processed, x=x, y=y)

    elif chart_type == "histogram":
        fig = px.histogram(df_processed, x=x)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return fig