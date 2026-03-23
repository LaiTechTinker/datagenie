import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Flask,jsonify,request
from flask_cors import CORS
from pathlib import Path
from Data_insights import generate_insights
from profiling import profile_data,profile_to_text
from visagent import generate_chart_spec
from VisualCreator import apply_aggregation, generate_chart
from Data_cleaning import generate_cleaning_report
from Cleaningsum import explain_cleaning
from Mlengine import run_automl
from Mlexplanation import explain_results

# let initiate flask here
app=Flask(__name__)
CORS(app)
# Folder to store uploads
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = ["csv", "xlsx"]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
file_store={}  # In-memory store for file_id to file_path mapping
# this is an helper function for loading the dataframe based on file_id, this will be used in all pipelines to load the data for processing
def load_dataframe(file_id):
    if file_id not in file_store:
        raise ValueError("Invalid file_id")

    file_path = file_store[file_id]
    ext = Path(file_path).suffix.lower()

    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".xlsx":
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")
@app.route("/",methods=["GET"])
def send_ui():
    return jsonify({
        "message":"hello brother"
    })
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(file.filename)
        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Only CSV and XLSX allowed"}), 400

        # Generate unique file_id
        file_id = str(uuid.uuid4())

        # Save file
        saved_name = f"{file_id}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, saved_name)
        file.save(file_path)

        # Store mapping
        file_store[file_id] = file_path

        return jsonify({
            "message": "File uploaded successfully",
            "file_id": file_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/profiling",methods=["POST"])
def run_profiling_pipeline():
 try:
  
    data=request.get_json()
    file_id=data.get("file_id")
    df=load_dataframe(file_id)
    # Step 1: Profile dataset
    profile = profile_data(df=df)

    # Step 2: Convert to text for LLM
    summary_text = profile_to_text(profile)

    # Step 3: Generate AI insights
    insights = generate_insights(summary_text)

    return jsonify({
        "profile": profile,
        "insights": insights
    })
 except Exception as e:
    return jsonify({"error": f"{e}"}),500

# this code block will generate data visualixation
@app.route("/visualize", methods=["POST"])
def visualize():
    try:
        data = request.get_json()

        file_id = data.get("file_id")
        user_query = data.get("query")

        if not file_id or not user_query:
            return jsonify({"error": "file_id and query are required"}), 400

        # Load dataframe (reuse your earlier helper)
        df = load_dataframe(file_id)

        # Step 1: Generate chart spec (LLM)
        spec = generate_chart_spec(user_query, list(df.columns))

        # Step 2: Generate chart (Plotly)
        fig = generate_chart(df, spec)

        #  Convert to HTML for inserting in frontend
        chart_html = fig.to_html(full_html=False)

        return jsonify({
            "spec": spec,
            "chart": chart_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# this code block will run the data cleaning pipeline

def run_cleaning_pipeline(file_path: str):
    df = pd.read_csv(file_path)

    # Step 1: Detect issues
    report = generate_cleaning_report(df)

    # Step 2: AI explanation (optional)
    explanation = explain_cleaning(report)
    return {
        "report": report,
        "explanation": explanation
    }
# this code block is for running the Ml pipeline

def run_ml_pipeline(file_path: str, target_column: str):
    df = pd.read_csv(file_path)

    result = run_automl(df, target_column)

    explanation = explain_results(result)

    return {
        "result": result,
        "explanation": explanation
    }

# app server starting
if __name__ =="__main__":
    app.run(debug=True)