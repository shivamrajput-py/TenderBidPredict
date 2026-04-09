from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "ElectricalWorks.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_OUTPUT_PATH = ARTIFACTS_DIR / "best_bid_estimator.pkl"
REPORT_OUTPUT_PATH = ARTIFACTS_DIR / "training_report.json"

TARGET_COLUMN = "gov_est_price"
DROP_COLUMNS = ["id", "title", "org"]
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_SPLITS = 5
SAFE_N_JOBS = 1


@dataclass
class CandidateResult:
    model_name: str
    cv_r2_mean: float
    cv_r2_std: float
    cv_rmse_mean: float
    test_mae: float
    test_rmse: float
    test_r2: float


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    dataframe = pd.read_csv(dataset_path)
    dataframe = dataframe.dropna(subset=[TARGET_COLUMN]).copy()
    if dataframe.empty:
        raise ValueError("Dataset is empty after removing rows with missing target values.")
    return dataframe


def split_features_and_target(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_frame = dataframe.drop(columns=DROP_COLUMNS + [TARGET_COLUMN])
    target = dataframe[TARGET_COLUMN].astype(float)
    return feature_frame, target


def build_preprocessor(feature_frame: pd.DataFrame) -> ColumnTransformer:
    numeric_features = feature_frame.select_dtypes(include="number").columns.tolist()
    categorical_features = [column for column in feature_frame.columns if column not in numeric_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_candidate_pipelines(preprocessor: ColumnTransformer) -> dict[str, Pipeline]:
    return {
        "elastic_net": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", ElasticNet(alpha=0.01, l1_ratio=0.15, random_state=RANDOM_STATE, max_iter=10000)),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "model",
                    RandomForestRegressor(
                        n_estimators=300,
                        max_depth=12,
                        min_samples_leaf=2,
                        random_state=RANDOM_STATE,
                        n_jobs=SAFE_N_JOBS,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "model",
                    ExtraTreesRegressor(
                        n_estimators=400,
                        max_depth=None,
                        min_samples_leaf=1,
                        random_state=RANDOM_STATE,
                        n_jobs=SAFE_N_JOBS,
                    ),
                ),
            ]
        ),
    }


def evaluate_candidates(
    pipelines: dict[str, Pipeline],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[Pipeline, list[CandidateResult]]:
    cv = KFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    results: list[CandidateResult] = []
    best_name = ""
    best_pipeline: Pipeline | None = None
    best_score = float("-inf")

    for model_name, pipeline in pipelines.items():
        scores = cross_validate(
            pipeline,
            x_train,
            y_train,
            cv=cv,
            scoring={
                "r2": "r2",
                "rmse": "neg_root_mean_squared_error",
            },
            n_jobs=1,
        )

        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)

        candidate_result = CandidateResult(
            model_name=model_name,
            cv_r2_mean=float(scores["test_r2"].mean()),
            cv_r2_std=float(scores["test_r2"].std()),
            cv_rmse_mean=float((-scores["test_rmse"]).mean()),
            test_mae=float(mean_absolute_error(y_test, predictions)),
            test_rmse=float(sqrt(mean_squared_error(y_test, predictions))),
            test_r2=float(r2_score(y_test, predictions)),
        )
        results.append(candidate_result)

        if candidate_result.test_r2 > best_score:
            best_score = candidate_result.test_r2
            best_name = model_name
            best_pipeline = pipeline

    if best_pipeline is None:
        raise RuntimeError("No model candidates were evaluated successfully.")

    print(f"Selected best model: {best_name}")
    return best_pipeline, sorted(results, key=lambda item: item.test_r2, reverse=True)


def build_training_report(
    dataset: pd.DataFrame,
    feature_frame: pd.DataFrame,
    candidate_results: list[CandidateResult],
    best_pipeline: Pipeline,
) -> dict[str, Any]:
    model_step = best_pipeline.named_steps["model"]
    return {
        "dataset_path": str(DATASET_PATH),
        "row_count": int(len(dataset)),
        "feature_columns": feature_frame.columns.tolist(),
        "target_column": TARGET_COLUMN,
        "best_model": model_step.__class__.__name__,
        "candidate_results": [asdict(result) for result in candidate_results],
    }


def save_artifacts(best_pipeline: Pipeline, report: dict[str, Any]) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_OUTPUT_PATH)
    REPORT_OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    dataset = load_dataset(DATASET_PATH)
    features, target = split_features_and_target(dataset)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    preprocessor = build_preprocessor(features)
    candidate_pipelines = build_candidate_pipelines(preprocessor)
    best_pipeline, candidate_results = evaluate_candidates(
        candidate_pipelines,
        x_train,
        y_train,
        x_test,
        y_test,
    )

    report = build_training_report(dataset, features, candidate_results, best_pipeline)
    save_artifacts(best_pipeline, report)

    print(json.dumps(report, indent=2))
    print(f"Saved model artifact to: {MODEL_OUTPUT_PATH}")
    print(f"Saved training report to: {REPORT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
