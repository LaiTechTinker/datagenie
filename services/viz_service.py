"""Suggest charts and compute aggregated chart data from a dataset."""
from collections import Counter
from models import dataset as ds_model
from utils.errors import ApiError


def suggestions(user_id: str, dataset_id: str) -> dict:
    d = ds_model.get(user_id, dataset_id)
    if not d:
        raise ApiError("Dataset not found", 404)
    rows = d.get("rows", [])
    cols = d.get("columns", [])
    numeric = [c["name"] for c in cols if c["type"] == "number"]
    categorical = [c["name"] for c in cols if c["type"] == "string"]

    charts = []
    # Histogram of first numeric column
    if numeric:
        col = numeric[0]
        values = [r[col] for r in rows if isinstance(r.get(col), (int, float))]
        if values:
            mn, mx = min(values), max(values)
            bins = 10
            step = (mx - mn) / bins if mx > mn else 1
            buckets = [0] * bins
            for v in values:
                idx = min(int((v - mn) / step), bins - 1) if step else 0
                buckets[idx] += 1
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {col}",
                "data": [{"bin": f"{mn + i*step:.1f}", "count": c} for i, c in enumerate(buckets)],
            })

    # Bar chart of first categorical
    if categorical:
        col = categorical[0]
        counts = Counter(r.get(col) for r in rows if r.get(col) is not None)
        top = counts.most_common(10)
        charts.append({
            "type": "bar",
            "title": f"Top values of {col}",
            "data": [{"label": str(k), "value": v} for k, v in top],
        })

    # Scatter of first two numeric
    if len(numeric) >= 2:
        x, y = numeric[0], numeric[1]
        pts = [{"x": r[x], "y": r[y]} for r in rows
               if isinstance(r.get(x), (int, float)) and isinstance(r.get(y), (int, float))]
        charts.append({"type": "scatter", "title": f"{x} vs {y}", "data": pts[:500]})

    return {"charts": charts}
