import os
import pandas as pd
import joblib


def load_pipeline():
    """Load the saved pipeline from the models directory.

    Returns:
        sklearn.pipeline.Pipeline: The saved preprocessing+model pipeline.
    """
    base = os.path.dirname(os.path.dirname(__file__))
    model_path = os.path.join(base, "models", "pipeline.joblib")
    # joblib.load will deserialize the pipeline object
    return joblib.load(model_path)


def predict_from_dict(pipeline, input_dict):
    """Predict a single example provided as a dictionary.

    Args:
        pipeline: A fitted sklearn pipeline (preprocessor + estimator).
        input_dict (dict): Mapping of feature names to values for one sample.

    Returns:
        float: Predicted price for the input.
    """
    # Convert the single example into a DataFrame so the pipeline can accept it
    df = pd.DataFrame([input_dict])
    preds = pipeline.predict(df)
    return float(preds[0])


if __name__ == "__main__":
    pipeline = load_pipeline()
    sample = {
        "Inches": 15.6,
        "ppi": 141.21,
        "Ram_GB": 16,
        "Weight_kg": 1.7,
        "Total_Storage_GB": 1000,
        "TouchScreen": 0,
        "Ips": 1,
        "Dedicated_Gpu": 1,
        "Company": "Dell",
        "Cpu": "Intel Core i5-1335U",
        "Gpu": "Intel Iris Xe Graphics G7 (80EU)",
        "OpSys": "Windows",
        "Storage_Category": "Standard (512GB-1TB)",
    }
    print(predict_from_dict(pipeline, sample))
