# ESG Scoring & Analytics Dashboard 🌍📊

This project is an **end-to-end Machine Learning web application** that predicts **ESG (Environmental, Social, Governance) scores** for companies and provides an interactive analytics dashboard.

It includes:

- ✅ **ML model** trained on ESG-related features  
- ✅ **FastAPI backend** deployed on Render (serves predictions as an API)  
- ✅ **Streamlit frontend** deployed on Streamlit Cloud (user-facing dashboard)  

---

## 1. Project Overview

ESG (Environmental, Social, Governance) scores are widely used by investors to evaluate how sustainable and responsible a company is.

This project builds a **classification model** that predicts an overall ESG grade based on:

- Environment score  
- Social score  
- Governance score  
- Plus some basic metadata (industry, currency, etc.)

The model is then deployed as a web API and integrated into an interactive dashboard.

---

## 2. Architecture

**High-level flow:**

1. User opens the **Streamlit dashboard** (frontend).
2. User enters ESG-related inputs (E, S, G scores, etc.).
3. Streamlit sends a JSON request to the **FastAPI backend** (`/predict` endpoint).
4. FastAPI loads the trained model (`esg_model.pkl`) and returns a predicted ESG grade.
5. The frontend displays the prediction and visualizations.

```text
[User] → [Streamlit UI] → (POST JSON) → [FastAPI API on Render] → [ML Model] → Prediction → [Streamlit UI]
