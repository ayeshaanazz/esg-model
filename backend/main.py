from fastapi import FastAPI
import joblib
import pandas as pd
import json

app = FastAPI()

# Load model + columns
model = joblib.load("esg_model.pkl")
columns = json.load(open("columns.json"))

@app.get("/")
def home():
    return {"message": "ESG Model API is running successfully!"}

@app.post("/predict")
def predict(input_data: dict):
    df = pd.DataFrame([input_data])
    
    # Add missing columns
    for col in columns:
        if col not in df.columns:
            df[col] = 0
    
    df = df[columns]
    prediction = model.predict(df)[0]
    
    return {"predicted_grade": int(prediction)}
