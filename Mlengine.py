import pandas as pd
import joblib
import uuid
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np
# this is where feature engineering on the uploaded data will happen
def preprocess_data(df: pd.DataFrame):
    df = df.copy()
    encoders = {}

    # Handle missing values
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    # Date feature extraction
    for col in list(df.columns):
        if any(keyword in col.lower() for keyword in ["date", "time", "created", "timestamp"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_dayofweek"] = df[col].dt.dayofweek
            df[f"{col}_is_weekend"] = (df[col].dt.dayofweek >= 5).astype(int)

            df.drop(columns=[col], inplace=True)

    # Encode ALL non-numeric columns 
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip().str.lower()

            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])

            encoders[col] = le

    return df, encoders
# this code block detects if the problem is a classification or regression problem
def detect_problem_type(df, target, override=None):
   if override:
        return override
   y = df[target]

    # If it's text → classification
   if y.dtype == "object":
        return "classification"

    # If numeric but few unique values → classification
   if y.nunique() < 15 and y.dtype != "float":
        return "classification"

    # If float → regression
   if y.dtype in ["float64", "float32"]:
        return "regression"

   return "regression"


# this code block will run the ML pipeline and return the results
def get_models(problem_type, selected_models=None):
    if problem_type == "regression":
        models = {
            "linear_regression": Pipeline([
                ("scaler", StandardScaler()),
                ("model", LinearRegression())
            ]),
            "random_forest": RandomForestRegressor()
        }
    else:
        models = {
            "logistic_regression": Pipeline([
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000))
            ]),
            "random_forest": RandomForestClassifier()
        }

    if selected_models:
        models = {k: v for k, v in models.items() if k in selected_models}

    return models

# this code block will run the Ml model trainnig an evaluation and return the results
def train_models(X_train, X_test, y_train, y_test, models, problem_type):
    results = []

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)

        if problem_type == "classification":
            metrics = {
                "accuracy": accuracy_score(y_test, preds),
                "precision": precision_score(y_test, preds, average="weighted"),
                "recall": recall_score(y_test, preds, average="weighted"),
                "f1": f1_score(y_test, preds, average="weighted")
            }
            main_score = metrics["accuracy"]

        else:
            metrics = {
                "r2": r2_score(y_test, preds),
                "mae": mean_absolute_error(y_test, preds),
                "rmse": np.sqrt(mean_squared_error(y_test, preds))
            }
            main_score = metrics["r2"]

        results.append({
            "model": name,
            "score": round(main_score * 100, 2),
            "cv_score": round(cv_scores.mean() * 100, 2),
            "metrics": metrics,
            "model_obj": model
        })

    return results
# this code block gets the top features importance for the model and returns them 
def get_top_features(model, feature_names, top_n=5):
    # Handle pipeline
    if hasattr(model, "named_steps"):
        model = model.named_steps.get("model", model)

    # Tree-based models
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_

    # Linear models
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)

    else:
        return []

    return sorted(
        zip(feature_names, importances),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]
# this run the entire ML pipeline and returns the results in a dictionary format that can be easily explained by the Mlexplanation module
def run_automl(df, target, selected_models=None, problem_override=None):
    df_processed, _ = preprocess_data(df)

    X = df_processed.drop(columns=[target])
    y = df_processed[target]

    problem_type = detect_problem_type(df_processed, target, problem_override)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = get_models(problem_type, selected_models)

    if not models:
        raise ValueError("No valid models selected")

    results = train_models(X_train, X_test, y_train, y_test, models, problem_type)

    best = max(results, key=lambda x: x["score"])

    top_features = get_top_features(best["model_obj"], X.columns)

    return {
        "problem_type": problem_type,
        "results": results,
        "best_model_obj": best["model_obj"],
        "best_model": best["model"],
        "score": best["score"],
        "top_features": top_features
    }


def save_model(model):
    os.makedirs("saved_models", exist_ok=True)
    model_id = str(uuid.uuid4())
    path = f"saved_models/{model_id}.pkl"
    joblib.dump(model, path)
    return model_id, path