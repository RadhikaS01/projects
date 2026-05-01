import os
import pandas as pd
import joblib
import gradio as gr


BASE = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE, "resources", "laptop_data.csv")
MODEL_PATH = os.path.join(BASE, "models", "pipeline.joblib")


def load_choices():
    """Read the dataset and build choice lists for dropdowns.

    If the dataset is missing (e.g. in a deployed Space without resources uploaded),
    return safe empty lists so the app still starts. The dropdowns will be empty
    but the pipeline (if present) can still be used for direct predictions.
    """
    if not os.path.exists(DATA_PATH):
        # Dataset missing in deployment; return empty lists and log a message
        print(f"Warning: dataset not found at {DATA_PATH}. Dropdowns will be empty.")
        return {"Company": [], "Cpu": [], "Gpu": [], "OpSys": [], "Storage_Category": []}

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print(f"Warning: failed to read dataset: {e}")
        return {"Company": [], "Cpu": [], "Gpu": [], "OpSys": [], "Storage_Category": []}

    choices = {
        "Company": sorted(df["Company"].dropna().unique().tolist()),
        "Cpu": sorted(df["Cpu"].dropna().unique().tolist()),
        "Gpu": sorted(df["Gpu"].dropna().unique().tolist()),
        "OpSys": sorted(df["OpSys"].dropna().unique().tolist()),
        "Storage_Category": sorted(df["Storage_Category"].dropna().unique().tolist()),
    }
    return choices


def load_pipeline():
    """Load the trained pipeline if present, otherwise return None.

    This allows the app to start even if the model hasn't been trained yet.
    """
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


choices = load_choices()
pipeline = load_pipeline()


def predict_price(Inches, ppi, Ram_GB, Weight_kg, Total_Storage_GB, TouchScreen, Ips, Dedicated_Gpu, Company, Cpu, Gpu, OpSys, Storage_Category):
    """Wrapper that receives UI inputs, prepares a single-row input,
    and returns the predicted price (rounded).

    Returns a helpful message if the pipeline is not yet trained.
    """
    if pipeline is None:
        return "Model not trained. Run `src/train_model.py` first."

    # Build the input dict converting values to the expected types
    input_dict = {
        "Inches": float(Inches),
        "ppi": float(ppi),
        "Ram_GB": int(Ram_GB),
        "Weight_kg": float(Weight_kg),
        "Total_Storage_GB": int(Total_Storage_GB),
        "TouchScreen": int(TouchScreen),
        "Ips": int(Ips),
        "Dedicated_Gpu": int(Dedicated_Gpu),
        "Company": Company,
        "Cpu": Cpu,
        "Gpu": Gpu,
        "OpSys": OpSys,
        "Storage_Category": Storage_Category,
    }

    # Run the pipeline to get a prediction and round for display
    pred = pipeline.predict(pd.DataFrame([input_dict]))
    return round(float(pred[0]), 2)


with gr.Blocks() as demo:
    gr.Markdown("# Laptop Price Predictor")
    with gr.Row():
        with gr.Column():
            inches = gr.Number(value=15.6, label="Inches")
            ppi = gr.Number(value=141.21, label="PPI")
            ram = gr.Number(value=16, label="Ram_GB")
            weight = gr.Number(value=1.7, label="Weight_kg")
            storage = gr.Number(value=1000, label="Total_Storage_GB")
            touchscreen = gr.Radio([0,1], value=0, label="TouchScreen (0/1)")
            ips = gr.Radio([0,1], value=1, label="Ips (0/1)")
            dedicated = gr.Radio([0,1], value=1, label="Dedicated_Gpu (0/1)")
        with gr.Column():
            company = gr.Dropdown(choices.get("Company", []), label="Company")
            cpu = gr.Dropdown(choices.get("Cpu", []), label="Cpu")
            gpu = gr.Dropdown(choices.get("Gpu", []), label="Gpu")
            opsys = gr.Dropdown(choices.get("OpSys", []), label="OpSys")
            storage_cat = gr.Dropdown(choices.get("Storage_Category", []), label="Storage_Category")
    output = gr.Textbox(label="Predicted Price")
    btn = gr.Button("Predict")
    btn.click(predict_price, inputs=[inches, ppi, ram, weight, storage, touchscreen, ips, dedicated, company, cpu, gpu, opsys, storage_cat], outputs=output)


if __name__ == "__main__":
    demo.launch()
