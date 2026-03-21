import pandas as pd
import json
import os


def export_to_csv(df: pd.DataFrame, filename="output.csv"):
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/{filename}"

    df.to_csv(file_path, index=False)
    return file_path


def export_dict_to_json(data: dict, filename="output.json"):
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/{filename}"

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    return file_path