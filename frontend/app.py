import json
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ----------------- CONFIG -----------------
st.set_page_config(
    page_title="ESG Scoring Dashboard",
    page_icon="📊",
    layout="wide"
)

API_URL = "https://esg-model.onrender.com/predict"  # your deployed FastAPI endpoint

# ----------------- UTILS -----------------
def call_esg_api(payload: dict):
    """Call the FastAPI ESG model API and safely handle errors."""
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, f"API Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return None, f"Request failed: {e}"


def radar_chart(env, soc, gov, label="ESG Components"):
    categories = ["Environment", "Social", "Governance"]
    values = [env, soc, gov]
    values.append(values[0])  # close loop for radar

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=label
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# ----------------- SIDEBAR NAV -----------------
st.sidebar.title("📊 ESG Scoring Dashboard")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Single Prediction", "Batch Prediction", "Visual Analytics", "API Playground", "About Project"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Backend: FastAPI on Render\nFrontend: Streamlit")

# ----------------- PAGES -----------------

# 1) OVERVIEW
if page == "Overview":
    st.title("🌍 ESG Scoring & Analytics Dashboard")
    st.markdown(
        """
        This dashboard provides **ESG (Environmental, Social, Governance) scoring** using a deployed Machine Learning model.
        
        **What you can do here:**
        - Predict ESG score for a single company
        - Upload a CSV and score multiple companies
        - Visualize ESG components and distributions
        - Interact directly with the live FastAPI endpoint
        """
    )

    # Quick info cards
    col1, col2, col3 = st.columns(3)
    col1.metric("🚀 Model Type", "Random Forest", "Classification")
    col2.metric("📡 API Status", "ONLINE", "FastAPI")
    col3.metric("📍 Deployed On", "Render + Streamlit", "Cloud")

    st.markdown("### 🔎 Quick ESG Component Example")
    env = 7
    soc = 6
    gov = 8
    fig = radar_chart(env, soc, gov, "Sample ESG Profile")
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Use the left sidebar to move to **Single Prediction**, **Batch Prediction**, "
        "**Visual Analytics**, or **API Playground**."
    )


# 2) SINGLE PREDICTION
elif page == "Single Prediction":
    st.title("🔮 Single Company ESG Prediction")

    st.markdown("Provide ESG sub-scores and metadata to get a predicted overall ESG grade.")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Input Parameters")

        env = st.slider("Environment Score (1–10)", 1, 10, 7)
        soc = st.slider("Social Score (1–10)", 1, 10, 6)
        gov = st.slider("Governance Score (1–10)", 1, 10, 7)

        industry = st.selectbox(
            "Industry",
            ["OTHER", "Technology", "Finance", "Healthcare", "Energy", "Consumer", "Industrial"]
        )

        currency = st.selectbox(
            "Reporting Currency",
            ["USD", "EUR", "INR", "GBP", "OTHER"]
        )

        if st.button("Predict ESG Grade", type="primary"):
            payload = {
                "environment_grade_num": env,
                "social_grade_num": soc,
                "governance_grade_num": gov,
                # these extra features map to your model's one-hot features;
                # the backend will fill missing columns with 0
                "industry_clean_OTHER": 1 if industry == "OTHER" else 0,
                "currency_clean_USD": 1 if currency == "USD" else 0,
            }

            result, error = call_esg_api(payload)

            if error:
                st.error(error)
            else:
                pred = result.get("predicted_grade", "N/A")
                st.success(f"✅ Predicted ESG Grade: **{pred}**")

                with col_right:
                    st.subheader("ESG Profile")
                    fig = radar_chart(env, soc, gov, "Input ESG Components")
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Raw API Response")
                st.code(json.dumps(result, indent=2), language="json")


# 3) BATCH PREDICTION
elif page == "Batch Prediction":
    st.title("📁 Batch ESG Scoring (CSV Upload)")
    st.markdown(
        """
        Upload a CSV file containing columns like:  
        `environment_grade_num`, `social_grade_num`, `governance_grade_num`  
        
        The app will call the **live API** for each row and return predicted ESG scores.
        """
    )

    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.write("Preview of uploaded data:", df.head())

        required_cols = ["environment_grade_num", "social_grade_num", "governance_grade_num"]
        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            if st.button("Run Batch Prediction", type="primary"):
                results = []
                with st.spinner("Scoring all rows via API..."):
                    for idx, row in df.iterrows():
                        payload = {
                            "environment_grade_num": float(row["environment_grade_num"]),
                            "social_grade_num": float(row["social_grade_num"]),
                            "governance_grade_num": float(row["governance_grade_num"]),
                        }
                        res, err = call_esg_api(payload)
                        if err:
                            results.append(None)
                        else:
                            results.append(res.get("predicted_grade", None))

                df["predicted_grade"] = results
                st.success("Batch prediction completed!")
                st.dataframe(df)

                # Download results
                csv_out = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Results as CSV",
                    data=csv_out,
                    file_name="esg_scored_output.csv",
                    mime="text/csv",
                )


# 4) VISUAL ANALYTICS
elif page == "Visual Analytics":
    st.title("📊 Visual Analytics")

    st.markdown(
        """
        Use this section to **explore ESG component values** and see how they map to predicted ESG scores.
        """
    )

    st.subheader("Interactive ESG Scatter Plot")

    # simple demo dataset (user could upload real one)
    num_samples = 50
    env_vals = [i % 10 + 1 for i in range(num_samples)]
    soc_vals = [((i * 2) % 10) + 1 for i in range(num_samples)]
    gov_vals = [((i * 3) % 10) + 1 for i in range(num_samples)]

    demo_df = pd.DataFrame({
        "Environment": env_vals,
        "Social": soc_vals,
        "Governance": gov_vals
    })
    demo_df["ESG_Avg"] = demo_df[["Environment", "Social", "Governance"]].mean(axis=1)

    fig_scatter = px.scatter_3d(
        demo_df,
        x="Environment",
        y="Social",
        z="Governance",
        color="ESG_Avg",
        title="ESG Components 3D Scatter (Sample Data)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.info(
        "You can extend this section by feeding your real dataset and visualizing actual ESG scores and predictions."
    )


# 5) API PLAYGROUND
elif page == "API Playground":
    st.title("🧪 API Playground (Advanced Users)")

    st.markdown(
        """
        Here you can **manually send JSON** to the live FastAPI endpoint for full control.
        """
    )

    default_payload = {
        "environment_grade_num": 7,
        "social_grade_num": 6,
        "governance_grade_num": 5,
        "industry_clean_OTHER": 1,
        "currency_clean_USD": 1
    }

    json_input = st.text_area(
        "Request JSON",
        value=json.dumps(default_payload, indent=2),
        height=220
    )

    if st.button("Send Request to API", type="primary"):
        try:
            payload = json.loads(json_input)
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
            st.stop()

        with st.spinner("Sending request..."):
            res, err = call_esg_api(payload)

        if err:
            st.error(err)
        else:
            st.success("✅ API call successful")
            st.markdown("**Response:**")
            st.code(json.dumps(res, indent=2), language="json")

    st.markdown("---")
    st.caption(f"Current API URL: `{API_URL = "https://esg-model.onrender.com/predict"}`")


# 6) ABOUT PROJECT
elif page == "About Project":
    st.title("ℹ️ About This ESG ML Project")

    st.markdown(
        """
        ### 📌 Project Overview
        This project builds an **ESG (Environmental, Social, Governance) Scoring Model** using Machine Learning,  
        and deploys it as a **FastAPI backend** with a **Streamlit dashboard frontend**.

        ### 🔧 Tech Stack
        - **Modeling**: Scikit-learn (Random Forest)
        - **Backend**: FastAPI (deployed on Render)
        - **Frontend**: Streamlit (this dashboard)
        - **Communication**: REST API via HTTP POST (JSON)
        
        ### 🔁 End-to-End Flow
        1. User provides ESG-related inputs (Environment, Social, Governance scores, etc.)
        2. Frontend sends JSON payload to FastAPI endpoint: `/predict`
        3. Backend loads the trained model (`esg_model.pkl`), processes input, and returns prediction
        4. Frontend displays the predicted ESG grade + visualizations

        ### ✅ Features in this Dashboard
        - Single-company ESG prediction
        - Batch prediction using CSV upload
        - Basic visual analytics (3D scatter, radar chart)
        - API playground for manual testing
        - Deployed backend and frontend – simulating a real-world ML product

        ---
        You can extend this further by:
        - adding authentication (login system),
        - connecting to a database to log predictions,
        - or integrating live financial/ESG datasets.
        """
    )

