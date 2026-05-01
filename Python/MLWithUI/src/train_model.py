import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib


def load_data(path):
    """Load dataset from CSV file.

    Args:
        path (str): Path to CSV file.

    Returns:
        pd.DataFrame: Loaded dataframe.
    """
    # Use pandas to read the CSV into a DataFrame
    return pd.read_csv(path)


def build_pipeline(numeric_features, categorical_features):
    """Create preprocessing + model pipeline.

    The pipeline applies numeric imputation and scaling to numeric features,
    one-hot encoding to categorical features (with imputation for missing),
    then trains a RandomForestRegressor.

    Args:
        numeric_features (list[str]): Names of numeric feature columns.
        categorical_features (list[str]): Names of categorical feature columns.

    Returns:
        sklearn.pipeline.Pipeline: A fitted pipeline (preprocessor + regressor).
    """
    # Numeric pipeline: fill missing values with median and scale
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    # Categorical pipeline: fill missing with a token then one-hot encode
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
    ])

    return model


def train_and_save(data_path, out_dir):
    """Train the model pipeline on the dataset and save it.

    Steps:
    - Load CSV into a DataFrame
    - Select features and target, drop rows missing the target
    - Split into train/test, fit the pipeline, evaluate RMSE
    - Save the trained pipeline to `out_dir/pipeline.joblib`

    Args:
        data_path (str): Path to the CSV data file.
        out_dir (str): Directory where the pipeline will be saved.
    """
    # Load the dataset
    df = load_data(data_path)

    target = "Price"

    # Features chosen for the simple example model
    features = [
        "Inches",
        "ppi",
        "Ram_GB",
        "Weight_kg",
        "Total_Storage_GB",
        "TouchScreen",
        "Ips",
        "Dedicated_Gpu",
        "Company",
        "Cpu",
        "Gpu",
        "OpSys",
        "Storage_Category",
    ]

    # Keep only rows that have the target value
    df = df[features + [target]].dropna(subset=[target])

    X = df[features]
    y = df[target]

    # Define which features are numeric vs categorical
    numeric_features = ["Inches", "ppi", "Ram_GB", "Weight_kg", "Total_Storage_GB", "TouchScreen", "Ips", "Dedicated_Gpu"]
    categorical_features = ["Company", "Cpu", "Gpu", "OpSys", "Storage_Category"]

    # Build the full pipeline (preprocessing + estimator)
    model = build_pipeline(numeric_features, categorical_features)

    # Split, train, and evaluate
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    from sklearn.metrics import mean_squared_error
    import numpy as np

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"Test RMSE: {rmse:.2f}")

    # Ensure output directory exists and save the trained pipeline
    os.makedirs(out_dir, exist_ok=True)
    joblib.dump(model, os.path.join(out_dir, "pipeline.joblib"))
    print(f"Saved pipeline to {os.path.join(out_dir, 'pipeline.joblib')}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base, "resources", "laptop_data.csv")
    out_dir = os.path.join(base, "models")
    train_and_save(data_path, out_dir)
