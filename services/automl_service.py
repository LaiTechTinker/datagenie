"""Real AutoML training using scikit-learn, with WebSocket progress streaming."""
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from lazypredict.Supervised import (LazyClassifier,LazyRegressor)
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    mean_squared_error, mean_absolute_error, r2_score, confusion_matrix,
)

from extensions import socketio
from models import dataset as ds_model
from models import job as job_model
from utils.errors import ApiError


from sklearn.linear_model import (
        LinearRegression,LogisticRegression
    )
from sklearn.ensemble import (
        RandomForestRegressor, RandomForestClassifier
    )

from sklearn.neighbors import KNeighborsRegressor,KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
# from sklearn.linear_model import (
#         LogisticRegression, RidgeClassifier, SGDClassifier
#     )
# from sklearn.ensemble import (
#         RandomForestClassifier, ExtraTreesClassifier,
#         GradientBoostingClassifier, HistGradientBoostingClassifier,
#     )

# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from sklearn.neighbors import NearestCentroid
# from sklearn.naive_bayes import BernoulliNB


regressors = [
        LinearRegression,
        RandomForestRegressor,
         KNeighborsRegressor,
    ]
classifiers = [
        LogisticRegression, 
        RandomForestClassifier, 
        DecisionTreeClassifier, KNeighborsClassifier,
       
    ]

NS = "/training"


def _emit(job_id: str, event: str, payload: dict):
    socketio.emit(event, payload, namespace=NS, to=f"job:{job_id}")


def _log(job_id: str, line: str):
    line = f"[{time.strftime('%H:%M:%S')}] {line}"
    job_model.push_log(job_id, line)
    _emit(job_id, "job:update", {"jobId": job_id, "log": line})


def _set_progress(job_id: str, progress: int, status: str | None = None):
    fields = {"progress": progress}
    if status:
        fields["status"] = status
    job_model.update(job_id, **fields)
    _emit(job_id, "job:update", {"jobId": job_id, "progress": progress, "status": status})


def start(user_id: str, dataset_id: str, target: str, problem_type: str,
          test_size: float, random_state: int) -> dict:
    d = ds_model.get(user_id, dataset_id)
    if not d:
        raise ApiError("Dataset not found", 404)
    if target not in [c["name"] for c in d.get("columns", [])]:
        raise ApiError(f"Target column '{target}' not in dataset", 400)
    if problem_type not in ("classification", "regression"):
        raise ApiError("problemType must be classification or regression", 400)

    job = job_model.create(user_id, dataset_id, target, problem_type, test_size, random_state)
    job_id = str(job["_id"])
    socketio.start_background_task(_run_job, job_id, d, target, problem_type, test_size, random_state)
    return job_model.serialize(job)


def _run_job(job_id, dataset, target, problem_type, test_size, random_state):
    try:
        _set_progress(job_id, 5, "running")
        _log(job_id,"="*30)
        _log(job_id, f"Starting {problem_type} training on '{dataset['name']}'")
        _log(job_id, "loading dataset into memory....")
        _set_progress(job_id,10)
        df = pd.DataFrame(dataset["rows"])
        if target not in df.columns:
            raise ValueError(f"Target '{target}' not found")
        y = df[target]
        X = df.drop(columns=[target])
        _log(job_id,"features and target seperation done")
        _set_progress(job_id,15)
       

        # Encode non-numeric features
        _log(job_id, f"Preprocessing {X.shape[1]} features...")
        for col in X.columns:
            if X[col].dtype == object or str(X[col].dtype).startswith("string"):
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
        X = pd.DataFrame(SimpleImputer(strategy="mean").fit_transform(X), columns=X.columns)
        _set_progress(job_id, 25)

        if problem_type == "classification":
            y = LabelEncoder().fit_transform(y.astype(str))
        _log(job_id,f"proceeding to splitting features and target with size {test_size} and random_state{random_state}")
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        _log(job_id, f"Train features: {len(X_tr)} rows • Test: {len(X_te)} rows")
        _log(job_id, f"Train taget: {len(y_tr)} rows • Test: {len(y_te)} rows")
        _set_progress(job_id, 30)

        # if problem_type == "classification":
        #     model = RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1)
        # else:
        #     model = RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1)

        # _log(job_id, "Fitting RandomForest...")
        # model.fit(X_tr, y_tr)
        # _set_progress(job_id, 80)
        if problem_type=="classification":
            _log(job_id,"entering lazy predict runner for classification problem")
            runnner_ouput=_run_classification(job_id=job_id,X_train=X_tr,X_test=X_te,y_train=y_tr,y_test=y_te)
            _set_progress(job_id, 70)
        else:
            _log(job_id,"entering lazy predict runner for regression problem")
            _set_progress(job_id, 80)
            runnner_ouput=_run_regression(job_id=job_id,X_train=X_tr,X_test=X_te,y_train=y_tr,y_test=y_te)
        _log(job_id,"lazy predict runner completed proceeding to building metrics")
        _set_progress(job_id,90)
        # preds = model.predict(X_te)
        # if problem_type == "classification":
        #     metrics = {
        #         "accuracy": float(accuracy_score(y_te, preds)),
        #         "f1": float(f1_score(y_te, preds, average="weighted", zero_division=0)),
        #         "precision": float(precision_score(y_te, preds, average="weighted", zero_division=0)),
        #         "recall": float(recall_score(y_te, preds, average="weighted", zero_division=0)),
        #     }
        #     cm = confusion_matrix(y_te, preds).tolist()
        # else:
        #     metrics = {
        #         "rmse": float(np.sqrt(mean_squared_error(y_te, preds))),
        #         "mae": float(mean_absolute_error(y_te, preds)),
        #         "r2": float(r2_score(y_te, preds)),
        #     }
        #     cm = None

        # importances = sorted(
        #     [{"feature": f, "importance": float(i)}
        #      for f, i in zip(X.columns, model.feature_importances_)],
        #     key=lambda r: r["importance"], reverse=True,
        # )[:20]
        # runner_output is expected to include metrics + (optionally) models.
        metrics = build(runner_output=runnner_ouput) or {}

        # Safe defaults (filled later when we wire classification/regression formatters).
        importances = []
        cm = None


        best_model = metrics.get("best_model")
        results = {
            "metrics": metrics,
            "featureImportance": importances,
            "confusionMatrix": cm,
            "modelSummary": f"The {best_model} is the best model" if best_model else "Best model not available",
        }

        job_model.update(job_id, results=results, status="completed", progress=100)
        _log(job_id, "Training complete")
        _emit(job_id, "job:done", {"jobId": job_id, "results": results})
        _emit(job_id, "job:update", {"jobId": job_id, "status": "completed", "progress": 100})

    except Exception as e:
        job_model.update(job_id, status="failed")
        _log(job_id, f"ERROR: {e}")
        _emit(job_id, "job:update", {"jobId": job_id, "status": "failed"})


def get(job_id: str) -> dict:
    j = job_model.get(job_id)
    if not j:
        raise ApiError("Job not found", 404)
    return job_model.serialize(j)


def list_user(user_id: str) -> list:
    return [job_model.serialize(j) for j in job_model.list_for_user(user_id)]

# running classification and regression with lazy runner

def _format_classification_results(models_df: pd.DataFrame, y_test: np.ndarray) -> dict:
        """Return results in a shape compatible with frontend/src/features/workspace/ResultsTab.tsx.

        LazyClassifier is currently run with predictions=False in this file; so we base
        metrics on the model score columns exposed by LazyPredict. Confusion matrix is
        omitted when raw predictions are not available.
        """
        models_df = models_df.copy()

        # Identify common LazyPredict metric columns.
        # We support both capitalization variants.
        def _pick(col_candidates: list[str]):
            for c in col_candidates:
                if c in models_df.columns:
                    return c
            return None

        # Best model selection
        best_model = None
        if "Model" in models_df.columns:
            # Sometimes LazyPredict uses "Model".
            best_idx = None
            for score_col in ["Accuracy", "F1 Score", "Balanced Accuracy", "ROC AUC"]:
                if score_col in models_df.columns:
                    best_idx = models_df[score_col].idxmax()
                    best_model = models_df.loc[best_idx, "Model"]
                    break
        elif "Accuracy" in models_df.columns and "models" not in models_df.columns:
            # Fallback: rely on idxmax and row index
            try:
                best_idx = models_df["Accuracy"].idxmax()
                best_model = models_df.index.tolist()[0] if len(models_df.index) else None
            except Exception:
                best_model = None

        # Build numeric metrics map for frontend.
        # Prefer these columns if present.
        metrics: dict[str, float] = {}
        for out_key, cols in [
            ("accuracy", ["Accuracy"]),
            ("f1", ["F1 Score", "F1"]),
            ("precision", ["Precision"]),
            ("recall", ["Recall"]),
        ]:
            c = _pick(cols)
            if c is not None and len(models_df) > 0:
                try:
                    # Use best row value if available
                    if best_model is not None and "Model" in models_df.columns:
                        best_row = models_df[models_df["Model"] == best_model]
                        if len(best_row) > 0:
                            metrics[out_key] = float(best_row[c].iloc[0])
                        else:
                            metrics[out_key] = float(models_df[c].max())
                    else:
                        metrics[out_key] = float(models_df[c].max())
                except Exception:
                    pass

        # Ensure at least one metric exists
        if not metrics and len(models_df.columns) > 0:
            # pick first numeric column
            for c in models_df.columns:
                if c.lower() in ("accuracy", "f1 score", "f1", "precision", "recall"):
                    continue
                try:
                    if pd.api.types.is_numeric_dtype(models_df[c]):
                        metrics["accuracy"] = float(models_df[c].max())
                        break
                except Exception:
                    continue

        # Confusion matrix requires predictions.
        confusionMatrix = None

        # LazyPredict returns predictions when `predictions=True`.
        # `models_df` does not include them; LazyPredict attaches them to the fit output.
        # In this simplified implementation we only compute confusion matrix if
        # predictions are present in the fitted results dataframe.
        # (Fallback remains None.)
        if "Predictions" in models_df.columns:
            try:
                preds = models_df["Predictions"].to_numpy()
                confusionMatrix = confusion_matrix(y_test, preds).tolist()
            except Exception:
                confusionMatrix = None


        # Feature importance unavailable with LazyPredict here.
        featureImportance: list[dict] = []

        return {
            "metrics": metrics,
            "featureImportance": featureImportance,
            "confusionMatrix": confusionMatrix,
            "modelSummary": f"Best model: {best_model}" if best_model else "Best model not available",
            "best_model": best_model,
        }


def _run_classification(job_id, X_train, X_test, y_train, y_test) -> dict:

       

        _log(job_id,"Initialising LazyClassifier with curated fast models...")
        _log(job_id,f"Training {len(classifiers)} classification models...")

        clf = LazyClassifier(
            verbose=0,
            ignore_warnings=True,
            custom_metric=None,
predictions=True,       # we need predictions for confusion matrix
            classifiers=classifiers,
        )

        models_df, _ = clf.fit(X_train, X_test, y_train, y_test)
        _log(job_id, f"Training complete. {len(models_df)} classifiers evaluated.")

        return _format_classification_results(models_df, y_test=y_test)

def _run_regression(job_id: str, X_train, X_test, y_train, y_test) -> dict:


        

        _log(job_id,"Initialising LazyRegressor...")
        _log(job_id,"Initialising LazyRegressor with curated fast models...")
        _log(job_id, f"Training {len(regressors)} regression models...")
        _log(job_id, "Training all regressors — this may take a few minutes...")

        reg = LazyRegressor(
            verbose=0,
            ignore_warnings=True,
            custom_metric=None,
            regressors=regressors,
        )

        models_df, _ = reg.fit(X_train, X_test, y_train, y_test)
        _log(job_id, f"Training complete. {len(models_df)} regressors evaluated.")

        return _format_regression_results(models_df)
def _format_regression_results(models_df: pd.DataFrame) -> dict:
        """
        Picks best model by R-Squared (higher is better).
        Filters out models with negative R² (worse than a flat mean prediction).
        """

        models_df = models_df.copy()
        models_df = models_df.replace([np.inf, -np.inf], np.nan).dropna(how="all")
        models_df = models_df.round(4)

        # Filter out completely failed models
        if "R-Squared" in models_df.columns:
            usable = models_df[models_df["R-Squared"] > 0]
            best = usable["R-Squared"].idxmax() if len(usable) > 0 else None
        else:
            best = None

        records = models_df.reset_index().rename(
            columns={"index": "model"}
        ).to_dict(orient="records")

        return {
            "problem_type": "regression",
            "best_model": best,
            "models": records,
            "metric_columns": list(models_df.columns),
        }

# this builds the runner output
@staticmethod
def build(runner_output: dict) -> dict:
        """
        Returns the full metrics dict that gets stored under
        experiment.metrics in MongoDB.
        """
        models = runner_output.get("models", [])
        best_model = runner_output.get("best_model")
        problem_type = runner_output.get("problem_type")

        best_model_metrics = None
        if best_model:
            matched = [m for m in models if m.get("model") == best_model]
            if matched:
                best_model_metrics = matched[0]

        return {
            "problem_type": problem_type,
            "best_model": best_model,
            "best_model_metrics": best_model_metrics,
            "total_models_trained": len(models),
            "metric_columns": runner_output.get("metric_columns", []),
            "all_models": models
          
        }