import pandas as pd
import os
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
ALLOWED_EXTENSIONS = {"csv", "xlsx"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/",methods=["GET"])
def send_ui():
    return jsonify({
        "message":"hello brother"
    })
@app.route("/upload_file",methods=["POST"])
def run_profiling_pipeline():
 try:
    # check if a file is uploaded
    if "file" not in request.files:
        return  jsonify({
            'error':"No files is provided"}),400
    # this allows only one file to be uploaded at a time
    if  len(request.files.getlist("file"))!=1:
        return  jsonify({
            'error':"Please upload only one file at a time"}),400
    file=request.files["file"]
    file_name=file.filename
    # check is file_name is not empty
    if file_name=="":
        return  jsonify({
            'error':"No file is selected"}),400
    # Secure filename
    file_name = secure_filename(file.filename)
    extension=Path(file_name).suffix.lower()
   
    if extension not in [".csv",".xlsx"]:
        return jsonify({
            'error':"Invalid file format. Please upload a CSV or Excel file"}),400
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
    file.save(file_path)
    # Step 1: Profile dataset
    profile = profile_data(file_path)

    # Step 2: Convert to text for LLM
    summary_text = profile_to_text(profile)

    # Step 3: Generate AI insights
    insights = generate_insights(summary_text)

    return {
        "profile": profile,
        "insights": insights
    }
 except Exception as e:
    return jsonify({"error": f"{e}"}),500

# this code block will generate data visualixation
def run_visualization_pipeline(file_path: str, user_query: str):
 try:
    # Load data
    ext= Path(file_path).suffix
    
    if ext == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8')
    elif ext == '.xlsx':
            df = pd.read_excel(file_path)
    else:
            ValueError("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None

    # Step 1: Get chart spec from LLM
    spec = generate_chart_spec(user_query, list(df.columns))

    print("\nGenerated Spec:")
    print(spec)

    # Step 2: Generate chart
    fig = generate_chart(df, spec)

    # Save chart (since no UI yet)
    fig.write_html("output_chart.html")

    print("\nChart saved as output_chart.html")

    return spec
 except Exception as e:
    print("Error in visualization pipeline:", str(e))
    return None
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