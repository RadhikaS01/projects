import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import warnings
import os
import openai
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, jsonify, request
warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)

# 1. Load environment variables
load_dotenv()

# Configuration for GPT-4 API
def configure_gpt4():
    """Set up GPT-4 API access"""
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("API key not found in environment variables")
        
        # Test API connection
        openai.Model.list()
        return True
    except Exception as e:
        print(f"GPT-4 configuration failed: {str(e)}")
        print("Please follow these steps to configure:")
        print("1. Get API key from https://platform.openai.com/account/api-keys")
        print("2. Set environment variable: export OPENAI_API_KEY='your-api-key'")
        print("3. Install required package: pip install openai")
        return False

GPT4_ENABLED = configure_gpt4()
def run_anomaly_detection():
    """Run the anomaly detection pipeline and store results"""
    global anomalies_df,historical_data, scaler, model

    # Load historical data
    historical_data = pd.read_csv('historical_balances.csv')
    input_data = pd.read_csv('input_data.csv')

    # Ensure Match Status is calculated consistently
    def calculate_match_status(row):
        return 'Match' if abs(row['Balance Difference']) < 1 else 'Break'

    # Preprocess data
    def preprocess_data(df):
        df['As of Date'] = pd.to_datetime(df['As of Date'], dayfirst=True)
        df['Match Status'] = df.apply(calculate_match_status, axis=1)
        return df

    historical_data = preprocess_data(historical_data)
    input_data = preprocess_data(input_data)

    # Feature engineering
    def create_features(df):
        grouped = df.groupby(['Company', 'Account', 'AU', 'Currency', 'Primary Account', 'Secondary Account'])
        df.fillna(0, inplace=True)
        return df

    historical_data = create_features(historical_data)
    input_data = create_features(input_data)

    # Select features for anomaly detection
    features = ['GL Balance', 'IHub Balance', 'Balance Difference']

    # Train Isolation Forest model
    def train_model(data):
        scaler = StandardScaler()
        X = scaler.fit_transform(data[features])
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X)
        return model, scaler

    model, scaler = train_model(historical_data)

    # Detect anomalies
    def detect_anomalies(data, model, scaler):
        X = scaler.transform(data[features])
        anomalies = model.predict(X)
        data['anomaly'] = anomalies
        data['anomaly'] = data['anomaly'].map({1: 0, -1: 1})  # 1 is anomaly, 0 is normal
        return data

    input_data = detect_anomalies(input_data, model, scaler)

    # Generate AI explanation
    def generate_gpt4_explanation(row, historical_data):
        """Generate human-friendly explanation using GPT-4"""
        if not GPT4_ENABLED:
            return generate_basic_explanation(row, historical_data)
        
        # Prepare historical context
        hist_summary = f"""
        Historical Patterns (Last {len(historical_data)} periods):
        - GL Balance: Avg {historical_data['GL Balance'].mean():.2f} ± {historical_data['GL Balance'].std():.2f}
        - IHub Balance: Avg {historical_data['IHub Balance'].mean():.2f} ± {historical_data['IHub Balance'].std():.2f}
        - Typical Difference: {historical_data['Balance Difference'].mean():.2f}
        Recent Trend:
        {historical_data.tail(3)[['As of Date', 'GL Balance', 'IHub Balance']].to_string(index=False)}
        """
        
        prompt = f"""
        As a financial auditor, explain this anomaly in simple terms:
        
        Current Transaction:
        - Date: {row['As of Date']}
        - Account: {row['Account']} ({row['Primary Account']}/{row['Secondary Account']})
        - GL Balance: {row['GL Balance']:.2f}
        - IHub Balance: {row['IHub Balance']:.2f}
        - Difference: {row['Balance Difference']:.2f}
        
        {hist_summary}
        
        Focus on:
        1. What changed significantly
        2. Most likely cause (data entry, timing, system error)
        3. Recommended verification steps
        
        Response format:
        "We noticed [observation]. This suggests [likely cause]. Please [action]."
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Keep responses factual
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            #print(f"GPT-4 error: {str(e)}")
            return generate_basic_explanation(row, historical_data)

    def generate_basic_explanation(row, hist):
        """Fallback explanation without GPT-4"""
        explanation = []
        try:
                    
            # Check balance differences
            avg_diff = hist['Balance Difference'].mean()
            if abs(row['Balance Difference'] - avg_diff) > 2 * hist['Balance Difference'].std():
                explanation.append(f"Balance difference of {row['Balance Difference']:.2f} deviates from historical avg {avg_diff:.2f}")
            
            # Check GL Balance changes
            last_gl = hist.iloc[0]['GL Balance']
            if abs(row['GL Balance'] - last_gl) > 2 * hist['GL Balance'].std():
                explanation.append(f"GL Balance jumped from {last_gl:.2f} to {row['GL Balance']:.2f}")
            
            # Check IHub Balance changes
            last_ihub = hist.iloc[0]['IHub Balance']
            if abs(row['IHub Balance'] - last_ihub) > 2 * hist['IHub Balance'].std():
                explanation.append(f"IHub Balance changed from {last_ihub:.2f} to {row['IHub Balance']:.2f}")
            
            return " | ".join(explanation) if explanation else "Pattern deviation detected"
        except KeyError:
            return "New account combination not in historical data"

    def generate_explanation(row, historical_group):
        try:
            hist = historical_group.get_group((row['Company'], row['Account'], row['AU'],
                                            row['Currency'], row['Primary Account'], row['Secondary Account']))
            
            # Convert dates if needed
            if not isinstance(row['As of Date'], datetime):
                row['As of Date'] = datetime.strptime(row['As of Date'], '%d-%m-%Y')
            hist['As of Date'] = pd.to_datetime(hist['As of Date'])
            
            return generate_gpt4_explanation(row, hist) if GPT4_ENABLED else generate_basic_explanation(row, hist)
            
        except KeyError:
            return "New account - no historical comparison available"


    # Group historical data for comparison
    historical_grouped = historical_data.groupby(['Company', 'Account', 'AU', 'Currency', 'Primary Account', 'Secondary Account'])

    # Analyze anomalies and generate reports
    anomalies_detected = []
    for idx, row in input_data[input_data['anomaly'] == 1].iterrows():
        explanation = generate_explanation(row, historical_grouped)
        
        anomaly_report = {
            'As of Date': row['As of Date'].strftime('%d-%m-%Y'),
            'Company': row['Company'],
            'Account': row['Account'],
            'AU': row['AU'],
            'Currency': row['Currency'],
            'Primary Account': row['Primary Account'],
            'Secondary Account': row['Secondary Account'],
            'GL Balance': row['GL Balance'],
            'IHub Balance': row['IHub Balance'],
            'Balance Difference': row['Balance Difference'],
            'Match Status': row['Match Status'],
            'Anomaly Explanation': explanation,
            'Confirmed Anomaly': 'Pending Review',  # To be filled by user
            'Corrected GL Balance': None,            # To be filled by user
            'Corrected IHub Balance': None,          # To be filled by user
            'Correction Notes': None                 # To be filled by user
        }
        anomalies_detected.append(anomaly_report)

    # Convert anomalies to DataFrame
    anomalies_df = pd.DataFrame(anomalies_detected)

    # Save full results with all input data and anomaly flags
    full_results = input_data.copy()
    full_results['As of Date'] = full_results['As of Date'].dt.strftime('%d-%m-%Y')
    full_results = full_results[[
        'As of Date', 'Company', 'Account', 'AU', 'Currency', 
        'Primary Account', 'Secondary Account', 'GL Balance', 
        'IHub Balance', 'Balance Difference', 'Match Status', 'anomaly'
    ]]

    # Save files
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Save anomalies report for review
    anomalies_df.to_csv(f'{output_dir}/anomalies_report_for_review.csv', index=False)

    # Save full results
    full_results.to_csv(f'{output_dir}/full_results_with_anomaly_flags.csv', index=False)

    print("Anomaly detection completed. Please review:")
    print(f"1. Full results with anomaly flags: {output_dir}/full_results_with_anomaly_flags.csv")
    print(f"2. Anomalies needing review: {output_dir}/anomalies_report_for_review.csv")

    # Feedback loop implementation
    def process_feedback_and_retrain(historical_data):
        try:
            # Check for reviewed anomalies file
            reviewed_file = f'{output_dir}/reviewed_anomalies.csv'
            if os.path.exists(reviewed_file):
                reviewed = pd.read_csv(reviewed_file)
                
                # Filter confirmed anomalies with corrections
                confirmed = reviewed[reviewed['Confirmed Anomaly'] == 'Yes']
                
                if not confirmed.empty:
                    print(f"\nProcessing {len(confirmed)} confirmed anomalies...")
                    
                    # Create corrected records
                    corrected_records = []
                    for _, row in confirmed.iterrows():
                        if pd.notna(row['Corrected GL Balance']) or pd.notna(row['Corrected IHub Balance']):
                            corrected_record = {
                                'As of Date': row['As of Date'],
                                'Company': row['Company'],
                                'Account': row['Account'],
                                'AU': row['AU'],
                                'Currency': row['Currency'],
                                'Primary Account': row['Primary Account'],
                                'Secondary Account': row['Secondary Account'],
                                'GL Balance': row['Corrected GL Balance'] if pd.notna(row['Corrected GL Balance']) else row['GL Balance'],
                                'IHub Balance': row['Corrected IHub Balance'] if pd.notna(row['Corrected IHub Balance']) else row['IHub Balance'],
                                'Balance Difference': (row['Corrected GL Balance'] if pd.notna(row['Corrected GL Balance']) else row['GL Balance']) - 
                                            (row['Corrected IHub Balance'] if pd.notna(row['Corrected IHub Balance']) else row['IHub Balance']),
                                'Correction Notes': row['Correction Notes']
                            }
                            corrected_records.append(corrected_record)
                    
                    if corrected_records:
                        # Add to historical data
                        corrected_df = pd.DataFrame(corrected_records)
                        corrected_df = preprocess_data(corrected_df)
                        corrected_df = create_features(corrected_df)
                        
                        #global historical_data
                        historical_data = pd.concat([historical_data, corrected_df], ignore_index=True)
                        historical_data.to_csv('historical_balances_updated.csv', index=False)
                        
                        # Retrain model
                        #global model, scaler
                        model, scaler = train_model(historical_data)
                        print(f"Added {len(corrected_records)} corrected records to historical data and retrained model.")
                        
                        # Archive reviewed file
                        os.rename(reviewed_file, f'{output_dir}/reviewed_anomalies_processed_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv')
                    else:
                        print("No corrections provided in the reviewed anomalies.")
                else:
                    print("No confirmed anomalies found in the review file.")
            else:
                print("\nNo reviewed anomalies file found. To retrain model:")
                print("1. Review anomalies in anomalies_report_for_review.csv")
                print("2. Add 'Confirmed Anomaly' (Yes/No) and corrections if needed")
                print("3. Save as reviewed_anomalies.csv in the output folder")
                print("4. Run this script again")   
        except Exception as e:
            print(f"Error processing feedback: {str(e)}")

    # Run feedback processing
    process_feedback_and_retrain(historical_data)

# API Endpoints
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """Return all anomalies in JSON format"""
    if anomalies_df is None:
        return jsonify({"error": "No anomaly data available. Please run detection first."}), 404
    
    # Convert DataFrame to dictionary
    anomalies_data = anomalies_df.to_dict(orient='records')
    return jsonify(anomalies_data)

if __name__ == '__main__':
    # Run the anomaly detection when starting the server
    run_anomaly_detection()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)