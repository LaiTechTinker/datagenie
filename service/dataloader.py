import pandas as pd
import os
import uuid

UPLOAD_FOLDER = "uploads"

def save_file(file):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    return file_id, filepath


def load_data(filepath):
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file format")

    return df


def get_preview(df, n=5):
    return df.head(n).to_dict(orient="records")


def get_columns(df):
    return df.columns.tolist()