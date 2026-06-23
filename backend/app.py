from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import datetime
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

model = joblib.load("saved_model/model.pkl")

logs = []

@app.route('/')
def home():
    return "CyberShield AI Backend Running 🚀"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['features']

        input_data = np.array(data).reshape(1, -1)

        # UNIFIED TRAFFIC SCORE, THREAT LEVEL, & ATTACK TYPE LOGIC
        traffic_score = sum(data)

        if traffic_score > 500:
            result = 1
            threat_level = "CRITICAL"
            attack_type = "DDoS Attack"
        elif traffic_score > 350:
            result = 1
            threat_level = "HIGH"
            attack_type = "Port Scan"
        elif traffic_score > 250:
            result = 1
            threat_level = "MEDIUM"
            attack_type = "Brute Force"
        else:
            result = 0
            threat_level = "LOW"
            attack_type = "Normal Traffic"

        # Extract classification probability metrics for logging/analytics
        confidence = 0
        if hasattr(model, "predict_proba"):
            confidence = float(max(model.predict_proba(input_data)[0]))

        time_now = datetime.datetime.now().strftime("%H:%M:%S")

        logs.append({
            "input": data,
            "result": result,
            "confidence": round(confidence * 100, 2),
            "threat_level": threat_level,
            "attack_type": attack_type,
            "time": time_now
        })

        return jsonify({
            "result": result,
            "confidence": round(confidence * 100, 2),
            "threat_level": threat_level,
            "attack_type": attack_type,
            "time": time_now
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/logs')
def get_logs():
    return jsonify(logs)

@app.route('/stats')
def stats():
    total = len(logs)
    normal = len([x for x in logs if x['result'] == 0])
    attack = len([x for x in logs if x['result'] == 1])

    return jsonify({
        "total": total,
        "normal": normal,
        "attack": attack
    })

# FEATURE 6: UPGRADED SERVER-SIDE EXPORT UTILITY
@app.route('/export_report')
def export_report():
    try:
        if not logs:
            # Fallback placeholder to maintain functionality if logs are empty
            dummy_df = pd.DataFrame(columns=["Time", "Attack Type", "Threat Level", "Confidence", "Status"])
            filename = "security_report.csv"
            dummy_df.to_csv(filename, index=False)
            return send_file(filename, as_attachment=True)
            
        df = pd.DataFrame(logs)
        filename = "security_report.csv"
        df.to_csv(filename, index=False)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global logs
    logs = []
    return jsonify({"message": "Logs cleared"})

if __name__ == '__main__':
    app.run(debug=True)