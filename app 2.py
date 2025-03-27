
import streamlit as st
import pandas as pd

st.title("R&D Opportunity Explorer (Enhanced)")

# --- Input Section ---
st.header("Client Profile")
client_name = st.text_input("Client Name")
rd_spend = st.number_input("R&D Spend (in USD)", min_value=0, step=1000000)

st.header("Client Characteristics")
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

# --- Scoring Maps ---
level_scores = {"Low": 3, "Medium": 2, "High": 1}
inverse_scores = {"Outdated": 3, "Developing": 2, "Advanced": 1}
platform_scores = {"On-Prem": 3, "Hybrid": 2, "Cloud-Native": 1}
product_scores = {"Basic": 3, "Intermediate": 2, "Comprehensive": 1}
size_scores = {"Local": 1, "Regional": 2, "Global": 3}
ta_scores = {"Niche": 1, "Moderate": 2, "Broad": 3}
pipeline_scores = {"Simple": 1, "Moderate": 2, "Complex": 3}

# --- Weights per category (customizable later) ---
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

# --- Scoring Logic ---
scores = {
    "Tech Strategy": inverse_scores[tech_maturity],
    "Data Platforms": platform_scores[data_platform],
    "Data Products": product_scores[data_products],
    "AI Appetite": level_scores[ai_appetite],
    "AI Maturity": level_scores[ai_maturity],
    "AI Adoption": level_scores[ai_adoption],
    "Client Size": size_scores[footprint],
    "TA Breadth": ta_scores[ta_focus],
    "Pipeline Complexity": pipeline_scores[pipeline],
    "Digital Maturity": level_scores[digital_maturity],
}

# Composite AI score and mapped category
ai_total = scores["AI Appetite"] + scores["AI Maturity"] + scores["AI Adoption"]
if ai_total >= 7:
    ai_category = "High Opportunity"
    ai_weight = weights["AI Opportunity"]
elif ai_total >= 5:
    ai_category = "Moderate Opportunity"
    ai_weight = weights["AI Opportunity"] * 0.6
else:
    ai_category = "Low Opportunity"
    ai_weight = weights["AI Opportunity"] * 0.3

# --- Revenue Opportunity Calculation ---
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

total_opportunity_pct = sum(components.values())
total_revenue = round(rd_spend * total_opportunity_pct, -3)

# --- Display ---
if st.button("Calculate Opportunity"):
    st.subheader(f"Opportunity Summary for {client_name}")
    st.write(f"Estimated Revenue Opportunity: **${total_revenue:,.0f}**")
    st.write(f"AI/GenAI Category: **{ai_category}**")

    # Show breakdown
    df = pd.DataFrame.from_dict(components, orient='index', columns=['Weight'])
    df['Revenue Contribution'] = df['Weight'] * rd_spend
    st.write("### Breakdown by Area")
    st.dataframe(df.style.format({"Weight": "{:.2%}", "Revenue Contribution": "${:,.0f}"}))

    if total_opportunity_pct > 0.66:
        st.success("Priority Tier: HIGH")
    elif total_opportunity_pct > 0.4:
        st.warning("Priority Tier: MEDIUM")
    else:
        st.info("Priority Tier: LOW")
