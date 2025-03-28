
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="R&D Opportunity Explorer", layout="wide")

# Deloitte Branding
st.markdown(
    "<h1 style='color:#1A4D8F;'>Deloitte | R&D Opportunity Explorer</h1>",
    unsafe_allow_html=True
)
st.markdown("Use this tool to assess and compare revenue opportunities across multiple clients based on clinical tech maturity, data capabilities, and AI/GenAI readiness.")

# --- Input Section ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Deloitte.svg/2560px-Deloitte.svg.png", width=150)
st.sidebar.header("Add Client Profiles")

with st.sidebar.form(key="client_form"):
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

    submitted = st.form_submit_button("Add Client")
    if submitted and client_name:
        st.session_state.setdefault("clients", []).append({
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
        st.success(f"{client_name} added successfully!")

# Scoring maps
level_scores = {"Low": 3, "Medium": 2, "High": 1}
inverse_scores = {"Outdated": 3, "Developing": 2, "Advanced": 1}
platform_scores = {"On-Prem": 3, "Hybrid": 2, "Cloud-Native": 1}
product_scores = {"Basic": 3, "Intermediate": 2, "Comprehensive": 1}
size_scores = {"Local": 1, "Regional": 2, "Global": 3}
ta_scores = {"Niche": 1, "Moderate": 2, "Broad": 3}
pipeline_scores = {"Simple": 1, "Moderate": 2, "Complex": 3}

# Weights
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

if "clients" in st.session_state and st.session_state["clients"]:
    df_input = pd.DataFrame(st.session_state["clients"])
    results = []
    maturity_data = []

    for _, row in df_input.iterrows():
        scores = {
            "Tech Strategy": inverse_scores[row["Tech Maturity"]],
            "Data Platforms": platform_scores[row["Data Platform"]],
            "Data Products": product_scores[row["Data Products"]],
            "AI Appetite": level_scores[row["AI Appetite"]],
            "AI Maturity": level_scores[row["AI Maturity"]],
            "AI Adoption": level_scores[row["AI Adoption"]],
            "Client Size": size_scores[row["Footprint"]],
            "TA Breadth": ta_scores[row["TA Focus"]],
            "Pipeline Complexity": pipeline_scores[row["Pipeline"]],
            "Digital Maturity": level_scores[row["Digital Maturity"]],
        }

        ai_total = scores["AI Appetite"] + scores["AI Maturity"] + scores["AI Adoption"]
        if ai_total >= 7:
            ai_weight = weights["AI Opportunity"]
            ai_category = "High Opportunity"
            ai_roadmap = "Ready for scaled AI/GenAI deployment"
            action_step = "Implement enterprise AI/GenAI platform with use-case integration"
        elif ai_total >= 5:
            ai_weight = weights["AI Opportunity"] * 0.6
            ai_category = "Moderate Opportunity"
            ai_roadmap = "Begin pilots, strengthen AI/GenAI infrastructure"
            action_step = "Conduct AI pilot for clinical or regulatory use case"
        else:
            ai_weight = weights["AI Opportunity"] * 0.3
            ai_category = "Low Opportunity"
            ai_roadmap = "Focus on AI/GenAI awareness and data readiness"
            action_step = "Educate stakeholders and assess data architecture for AI readiness"

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
            "R&D Spend": row["R&D Spend"],
            "AI/GenAI Category": ai_category,
            "Estimated Revenue Opportunity": revenue,
            "Priority Tier": "HIGH" if total_score > 0.66 else "MEDIUM" if total_score > 0.4 else "LOW",
            **components
        })

        maturity_data.append({
            "Client": row["Client"],
            "Digital Maturity": row["Digital Maturity"],
            "Tech Maturity": row["Tech Maturity"],
            "Data Platform": row["Data Platform"],
            "Data Products": row["Data Products"],
            "AI Readiness": ai_category,
            "AI Roadmap": ai_roadmap,
            "Recommended Action": action_step
        })

    df_results = pd.DataFrame(results)
    df_maturity = pd.DataFrame(maturity_data)

    st.header("Client Opportunity Summary")
    st.dataframe(df_results.style.format({"Estimated Revenue Opportunity": "${:,.0f}"}))

    st.header("Visual Dashboard")
    st.subheader("Revenue Opportunity by Client")
    chart = alt.Chart(df_results).mark_bar().encode(
        x=alt.X("Client", sort="-y"),
        y="Estimated Revenue Opportunity",
        color="Priority Tier",
        tooltip=["Client", "Estimated Revenue Opportunity", "Priority Tier"]
    ).properties(width=800, height=400)
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Component Weight Breakdown")
    df_melted = df_results.melt(id_vars=["Client"], value_vars=[
        "Tech Strategy", "Data Platforms", "Data Products", "AI/GenAI",
        "Client Size", "TA Breadth", "Pipeline Complexity", "Digital Maturity"
    ], var_name="Component", value_name="Weight")
    stacked = alt.Chart(df_melted).mark_bar().encode(
        x="Client",
        y="Weight",
        color="Component",
        tooltip=["Client", "Component", "Weight"]
    ).properties(width=800, height=400)
    st.altair_chart(stacked, use_container_width=True)

    st.header("Maturity Heatmap and Roadmap Tracker")
    st.dataframe(df_maturity)

else:
    st.info("Add at least one client from the sidebar to begin.")
