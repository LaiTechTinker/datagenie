import pandas as pd
import os
import json
import uuid
import joblib
from werkzeug.utils import secure_filename
from flask import Flask,jsonify,request,send_file
from flask_cors import CORS
from pathlib import Path
from Data_insights import generate_insights
from profiling import profile_data,profile_to_text
from visagent import generate_chart_spec
from VisualCreator import  generate_chart
from Data_cleaning import clean_dataframe_with_actions, generate_cleaning_report,format_report_for_table
from Cleaningsum import explain_cleaning
from Mlengine import save_model, run_automl,preprocess_data
from Mlexplanation import explain_results

# let initiate flask here
app=Flask(__name__)
CORS(app)
# Folder to store uploads
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = [".csv", ".xlsx"]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
STORE_PATH = "file_store.json"

# Load store on startup
if os.path.exists(STORE_PATH):
    with open(STORE_PATH, "r") as f:
        file_store = json.load(f)
else:
    file_store = {}

def save_store():
    with open(STORE_PATH, "w") as f:
        json.dump(file_store, f)
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
@app.route("/summary",methods=["POST"])
def get_sum():
    data=request.get_json()
    file_id=data.get("file_id")
    df=load_dataframe(file_id)
    return jsonify({
        "rows":df.shape[0],
        "columns":df.shape[1]
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
        save_store()
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

@app.route("/analyze", methods=["POST"])
def analyze_data():
    try:
        data = request.get_json()
        file_id = data.get("file_id")

        df = load_dataframe(file_id)

        # Step 1: Generate report
        report = generate_cleaning_report(df)

        # Step 2: Convert to table format
        table_data = format_report_for_table(report)

        # Step 3: AI explanation (TEXT ONLY)
        explanation = explain_cleaning(report)

        return jsonify({
            "table": table_data,     # for frontend table
            # "explanation": explanation  # plain text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# this code block will initiate downloading of the cleaned data
@app.route("/clean", methods=["POST"])
def clean():
    try:
        data = request.get_json()
        file_id = data.get("file_id")
        actions=data.get("actions",[])  # List of cleaning actions from frontend

        df = load_dataframe(file_id)

        # Clean data
        cleaned_df = clean_dataframe_with_actions(df, actions)
        # Save cleaned file
        cleaned_filename = f"cleaned_{uuid.uuid4()}.csv"
        cleaned_path = os.path.join("cleaned_files", cleaned_filename)

        os.makedirs("cleaned_files", exist_ok=True)
        cleaned_df.to_csv(cleaned_path, index=False)

        # Return file for download
        return send_file(
            cleaned_path,
            as_attachment=True,
            download_name="cleaned_data.csv"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# this code block is for running the Ml pipeline

@app.route("/train", methods=["POST"])
def train():
    try:
        data = request.get_json()

        file_id = data.get("file_id")
        target = data.get("target")
        models = data.get("models")
        problem_override = data.get("problem_type")

        df = load_dataframe(file_id)

        result = run_automl(df, target, models, problem_override)

        # Save best model
        model_id, _ = save_model(result["best_model_obj"])

        explanation = explain_results(result)

        return jsonify({
            "problem_type": result["problem_type"],
            "best_model": result["best_model"],
            "score": result["score"],
            "top_features": result["top_features"],
            "model_id": model_id,
            "results_table": [
                {
                    "model": r["model"],
                    "score": r["score"],
                    "cv_score": r["cv_score"]
                } for r in result["results"]
            ],
            "explanation": explanation
        })

    except Exception as e:
      
        print(f"Error during training: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        model_id = data.get("model_id")
        input_data = data.get("input")

        model_path = f"saved_models/{model_id}.pkl"

        if not os.path.exists(model_path):
            return jsonify({"error": "Model not found"}), 404

        model = joblib.load(model_path)

        # Convert input to DataFrame
        df_input = pd.DataFrame([input_data])

        #  Apply SAME preprocessing
        df_input, _ = preprocess_data(df_input)

        prediction = model.predict(df_input)

        return jsonify({
            "prediction": prediction.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# app server starting
if __name__ =="__main__":
    app.run(debug=True)