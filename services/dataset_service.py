import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
from models import dataset as ds_model
from utils.errors import ApiError
from utils.parsers import parse_file
from utils.S3 import upload_file_to_s3,delete_file_from_s3

ALLOWED = {".csv", ".xlsx", ".xls"}


def upload(user_id: str, file_storage) -> dict:
    if not file_storage or not file_storage.filename:
        raise ApiError("No file provided", 400)
    fname = secure_filename(file_storage.filename)
    ext = os.path.splitext(fname)[1].lower()
    if ext not in ALLOWED:
        raise ApiError("Unsupported file type. Use CSV or XLSX.", 400)

    stored_name = f"{uuid.uuid4().hex}{ext}"
    temp_path = os.path.join(Config.UPLOAD_DIR, stored_name)
    file_storage.save(temp_path)
    try:
        rows, columns = parse_file(temp_path, fname)
    except Exception as e:
        os.remove(temp_path)
        raise ApiError(f"Failed to parse file: {e}", 400)

    s3_key = f"datasets/{user_id}/{stored_name}"

    try:
        s3_url = upload_file_to_s3(temp_path, s3_key)
    except RuntimeError as e:
        raise ApiError(str(e), 500)
    finally:
        os.remove(temp_path)  #  clean up temp file

    doc = ds_model.create(user_id, fname, rows, columns, s3_url)
    return ds_model.serialize(doc, include_rows=True)

    # try:
    #     rows, columns = parse_file(temp_path, fname)
    # except Exception as e:
    #     os.remove(path)
    #     raise ApiError(f"Failed to parse file: {e}", 400)

    # doc = ds_model.create(user_id, fname, rows, columns, path)
    # return ds_model.serialize(doc, include_rows=True)


def list_user(user_id: str) -> list:
    return [ds_model.serialize(d) for d in ds_model.list_for_user(user_id)]


def get(user_id: str, dataset_id: str) -> dict:
    d = ds_model.get(user_id, dataset_id)
    if not d:
        raise ApiError("Dataset not found", 404)
    return ds_model.serialize(d, include_rows=True, max_rows=200)


# def delete(user_id: str, dataset_id: str):
#     d = ds_model.get(user_id, dataset_id)
#     if not d:
#         raise ApiError("Dataset not found", 404)
#     if d.get("file_path") and os.path.exists(d["file_path"]):
#         try:
#             os.remove(d["file_path"])
#         except OSError:
#             pass
#     ds_model.delete(user_id, dataset_id)
def delete(user_id: str, dataset_id: str):
    d = ds_model.get(user_id, dataset_id)
    if not d:
        raise ApiError("Dataset not found", 404)

    file_path = d.get("file_path")
    if file_path and file_path.startswith("https://"):
        # extract the S3 key from the URL
        # URL format: https://{bucket}.s3.{region}.amazonaws.com/{key}
        s3_key = file_path.split(".amazonaws.com/")[-1]
        try:
            delete_file_from_s3(s3_key)
        except RuntimeError:
            pass  # don't block deletion if S3 removal fails

    ds_model.delete(user_id, dataset_id)