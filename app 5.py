
import streamlit as st
import pandas as pd
import altair as alt
import json
import os

st.set_page_config(page_title="R&D Opportunity Explorer", layout="wide")

# File persistence setup
DATA_FILE = "client_data.json"

def load_clients():
    if "clients" not in st.session_state:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                st.session_state.clients = json.load(f)
        else:
            st.session_state.clients = []

def save_clients():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.clients, f)

load_clients()

# Branding
st.markdown("<h1 style='color:#1A4D8F;'>Deloitte | R&D Opportunity Explorer</h1>", unsafe_allow_html=True)

# Sidebar form
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Deloitte.svg/2560px-Deloitte.svg.png", width=150)
st.sidebar.header("Add Client Profile")

with st.sidebar.form("client_form"):
    client_name = st.text_input("Client Name")
    rd_spend = st.number_input("R&D Spend (USD)", min_value=0, step=1000000)
    footprint = st.selectbox("Global Footprint", ["Local", "Regional", "Global"])
    ta_focus = st.selectbox("Therapeutic Area Focus", ["Niche", "Moderate", "Broad"])
    pipeline = st.selectbox("Pipeline Complexity", ["Simple", "Moderate", "Complex"])
    digital_maturity = st.selectbox("Digital Maturity", ["Low", "Medium", "High"])
    tech_maturity = st.selectbox("Clinical Tech Maturity", ["Outdated", "Developing", "Advanced"])
    data_platform = st.selectbox("Data Platform Maturity", ["On-Prem", "Hybrid", "Cloud-Native"])
    data_products = st.selectbox("Data Products Capability", ["Basic", "Intermediate", "Comprehensive"])
    ai_appetite = st.selectbox("GenAI Appetite", ["Low", "Medium", "High"])
    ai_maturity = st.selectbox("GenAI Maturity", ["Low", "Medium", "High"])
    ai_adoption = st.selectbox("GenAI Adoption", ["Low", "Medium", "High"])

    if st.form_submit_button("Add Client"):
        st.session_state.clients.append({
            "Client": client_name,
            "R&D Spend": rd_spend,
            "Footprint": footprint,
            "TA Focus": ta_focus,
            "Pipeline": pipeline,
            "Digital Maturity": digital_maturity,
            "Tech Maturity": tech_maturity,
            "Data Platform": data_platform,
            "Data Products": data_products,
            "AI Appetite": ai_appetite,
            "AI Maturity": ai_maturity,
            "AI Adoption": ai_adoption
        })
        save_clients()
        st.success(f"{client_name} added successfully!")

# Scoring maps
score_map = {"Low": 3, "Medium": 2, "High": 1}
inv_map = {"Outdated": 3, "Developing": 2, "Advanced": 1}
platform_map = {"On-Prem": 3, "Hybrid": 2, "Cloud-Native": 1}
product_map = {"Basic": 3, "Intermediate": 2, "Comprehensive": 1}
size_map = {"Local": 1, "Regional": 2, "Global": 3}
ta_map = {"Niche": 1, "Moderate": 2, "Broad": 3}
pipeline_map = {"Simple": 1, "Moderate": 2, "Complex": 3}

weights = {
    "Tech Strategy": 0.10,
    "Data Platforms": 0.08,
    "Data Products": 0.06,
    "AI Opportunity": 0.10,
    "Client Size": 0.04,
    "TA Breadth": 0.04,
    "Pipeline Complexity": 0.04,
    "Digital Maturity": 0.04,
}

if st.session_state.clients:
    df_input = pd.DataFrame(st.session_state.clients)
    results = []
    maturity = []

    for _, row in df_input.iterrows():
        scores = {
            "Tech Strategy": inv_map[row["Tech Maturity"]],
            "Data Platforms": platform_map[row["Data Platform"]],
            "Data Products": product_map[row["Data Products"]],
            "AI Appetite": score_map[row["AI Appetite"]],
            "AI Maturity": score_map[row["AI Maturity"]],
            "AI Adoption": score_map[row["AI Adoption"]],
            "Client Size": size_map[row["Footprint"]],
            "TA Breadth": ta_map[row["TA Focus"]],
            "Pipeline Complexity": pipeline_map[row["Pipeline"]],
            "Digital Maturity": score_map[row["Digital Maturity"]],
        }

        ai_total = scores["AI Appetite"] + scores["AI Maturity"] + scores["AI Adoption"]
        if ai_total >= 7:
            ai_weight = weights["AI Opportunity"]
            ai_category = "High Opportunity"
            ai_roadmap = "Implement enterprise AI/GenAI platform"
        elif ai_total >= 5:
            ai_weight = weights["AI Opportunity"] * 0.6
            ai_category = "Moderate Opportunity"
            ai_roadmap = "Run AI/GenAI pilot with scalable infra"
        else:
            ai_weight = weights["AI Opportunity"] * 0.3
            ai_category = "Low Opportunity"
            ai_roadmap = "Build awareness and assess AI readiness"

        components = {
            "Tech Strategy": weights["Tech Strategy"] * scores["Tech Strategy"] / 3,
            "Data Platforms": weights["Data Platforms"] * scores["Data Platforms"] / 3,
            "Data Products": weights["Data Products"] * scores["Data Products"] / 3,
            "AI/GenAI": ai_weight,
            "Client Size": weights["Client Size"] * scores["Client Size"] / 3,
            "TA Breadth": weights["TA Breadth"] * scores["TA Breadth"] / 3,
            "Pipeline Complexity": weights["Pipeline Complexity"] * scores["Pipeline Complexity"] / 3,
            "Digital Maturity": weights["Digital Maturity"] * scores["Digital Maturity"] / 3,
        }

        total_score = sum(components.values())
        revenue = round(row["R&D Spend"] * total_score, -3)

        results.append({
            "Client": row["Client"],
            "Estimated Revenue Opportunity": revenue,
            "Priority Tier": "HIGH" if total_score > 0.66 else "MEDIUM" if total_score > 0.4 else "LOW",
            **components
        })

        maturity.append({
            "Client": row["Client"],
            "AI Roadmap": ai_roadmap
        })

    df_results = pd.DataFrame(results)
    df_maturity = pd.DataFrame(maturity)

    st.header("Opportunity Summary")
    st.dataframe(df_results)

    st.subheader("Revenue by Client")
    chart = alt.Chart(df_results).mark_bar(size=30).encode(
        x=alt.X("Client:N", sort="-y"),
        y=alt.Y("Estimated Revenue Opportunity:Q", title="Revenue ($)"),
        color="Priority Tier:N",
        tooltip=["Client", "Estimated Revenue Opportunity", "Priority Tier"]
    ).properties(width=900)
    st.altair_chart(chart)

    st.subheader("AI Roadmap")
    st.dataframe(df_maturity)

    st.subheader("Chat with Data")
    question = st.text_input("Ask a question (e.g., who has high opportunity?)")
    if question:
        if "high" in question.lower():
            st.write(df_results[df_results["Priority Tier"] == "HIGH"])
        elif "low" in question.lower():
            st.write(df_results[df_results["Priority Tier"] == "LOW"])
        elif "medium" in question.lower():
            st.write(df_results[df_results["Priority Tier"] == "MEDIUM"])
        else:
            st.warning("Try asking about high, medium, or low opportunity.")

else:
    st.info("No client data yet. Please add a client.")
