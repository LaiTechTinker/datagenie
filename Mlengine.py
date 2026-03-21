import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression


def preprocess_data(df: pd.DataFrame):
    df = df.copy()

    encoders = {}

    for col in df.columns:
        if df[col].dtype == "object":
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    return df, encoders


def detect_problem_type(df: pd.DataFrame, target: str):
    if df[target].dtype == "object" or df[target].nunique() < 20:
        return "classification"
    return "regression"


def train_models(X_train, X_test, y_train, y_test, problem_type):
    results = []

    if problem_type == "regression":
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor()
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = r2_score(y_test, preds)

            results.append({
                "model": name,
                "score": score,
                "model_obj": model
            })

    else:
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Random Forest": RandomForestClassifier()
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = accuracy_score(y_test, preds)

            results.append({
                "model": name,
                "score": score,
                "model_obj": model
            })

    return results


def get_top_features(model, feature_names):
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        return sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )[:5]

    return []


def run_automl(df: pd.DataFrame, target: str):
    # Step 1: preprocess
    df_processed, _ = preprocess_data(df)

    # Step 2: split
    X = df_processed.drop(columns=[target])
    y = df_processed[target]

    problem_type = detect_problem_type(df, target)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Step 3: train models
    results = train_models(X_train, X_test, y_train, y_test, problem_type)

    # Step 4: pick best
    best = max(results, key=lambda x: x["score"])

    # Step 5: feature importance
    top_features = get_top_features(best["model_obj"], X.columns)

    return {
        "problem_type": problem_type,
        "best_model": best["model"],
        "score": round(best["score"] * 100, 2),
        "top_features": top_features
    }