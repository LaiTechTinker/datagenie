import pandas as pd
from pathlib import Path
from Data_insights import generate_insights
from profiling import profile_data,profile_to_text
from visagent import generate_chart_spec
from VisualCreator import apply_aggregation, generate_chart
from Data_cleaning import generate_cleaning_report
from Cleaningsum import explain_cleaning

def run_profiling_pipeline(file_path: str):
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