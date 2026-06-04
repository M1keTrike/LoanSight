from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

NUMERIC_FEATURES: list[str] = [
    "loan_amnt",
    "term_months",
    "annual_inc",
    "dti",
    "emp_length_years",
]
ONEHOT_FEATURES: list[str] = ["purpose"]
ORDINAL_FEATURES: list[str] = []

TARGET_REGRESSION = "int_rate"
TARGET_CLASSIFICATION = "is_default"

GRADE_ORDER = [["A", "B", "C", "D", "E", "F", "G"]]

API_TO_FEATURE = {
    "loan_amnt": "loan_amnt",
    "term": "term_months",
    "annual_inc": "annual_inc",
    "dti": "dti",
    "emp_length": "emp_length_years",
    "purpose": "purpose",
}

MODEL_COLUMNS = NUMERIC_FEATURES + ONEHOT_FEATURES + ORDINAL_FEATURES

def build_preprocessor(
    numeric_features: list[str] | None = None,
    onehot_features: list[str] | None = None,
    ordinal_features: list[str] | None = None,
    ordinal_categories: list[list[str]] | str = "auto",
) -> ColumnTransformer:
    numeric_features = NUMERIC_FEATURES if numeric_features is None else numeric_features
    onehot_features = ONEHOT_FEATURES if onehot_features is None else onehot_features
    ordinal_features = ORDINAL_FEATURES if ordinal_features is None else ordinal_features

    transformers = []

    if numeric_features:
        numeric_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        transformers.append(("num", numeric_pipe, numeric_features))

    if onehot_features:
        onehot_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),

            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        transformers.append(("cat", onehot_pipe, onehot_features))

    if ordinal_features:
        ordinal_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ordinal", OrdinalEncoder(
                categories=ordinal_categories,
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            )),
        ])
        transformers.append(("ord", ordinal_pipe, ordinal_features))

    return ColumnTransformer(
        transformers=transformers,
        remainder="drop",
        verbose_feature_names_out=False,
    )

def build_model_pipeline(estimator, **preprocessor_kwargs) -> Pipeline:
    return Pipeline([
        ("preprocessor", build_preprocessor(**preprocessor_kwargs)),
        ("model", estimator),
    ])
