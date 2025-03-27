
import streamlit as st

st.title("R&D Opportunity Explorer")

# --- Input Section ---
st.header("Client Details")
client_name = st.text_input("Client Name")
rd_spend = st.number_input("R&D Spend (in USD)", min_value=0, step=1000000)

st.header("Client Characteristics")
footprint = st.selectbox("Global Footprint", ["Local", "Regional", "Global"])
ta_focus = st.selectbox("Therapeutic Area Focus", ["Niche", "Moderate", "Broad"])
pipeline = st.selectbox("Pipeline Complexity", ["Simple", "Moderate", "Complex"])
digital_maturity = st.selectbox("Digital Maturity", ["Low", "Medium", "High"])
tech_maturity = st.selectbox("Clinical Tech Maturity", ["Outdated", "Developing", "Advanced"])
ai_appetite = st.selectbox("AI/GenAI Appetite", ["Low", "Medium", "High"])
ai_maturity = st.selectbox("AI/GenAI Maturity", ["Low", "Medium", "High"])
ai_adoption = st.selectbox("AI/GenAI Adoption", ["Low", "Medium", "High"])

# --- Scoring Maps ---
scoring_map = {"Low": 3, "Medium": 2, "High": 1}
inverse_score = {"Outdated": 3, "Developing": 2, "Advanced": 1}
size_score = {"Local": 1, "Regional": 2, "Global": 3}
ta_score = {"Niche": 1, "Moderate": 2, "Broad": 3}
pipeline_score = {"Simple": 1, "Moderate": 2, "Complex": 3}

# --- Scoring Logic ---
total_score = (
    size_score[footprint] +
    ta_score[ta_focus] +
    pipeline_score[pipeline] +
    scoring_map[digital_maturity] +
    inverse_score[tech_maturity] +
    scoring_map[ai_appetite] +
    scoring_map[ai_maturity] +
    scoring_map[ai_adoption]
)

# --- Weighting Logic ---
score_percent = total_score / 21  # 21 is max total score
estimated_opportunity = round(rd_spend * score_percent, -3)

# --- Output ---
if st.button("Calculate Opportunity"):
    st.subheader(f"Opportunity for {client_name}")
    st.write(f"Total Score: {total_score} / 21")
    st.write(f"Estimated Revenue Opportunity: **${estimated_opportunity:,.0f}**")

    if score_percent > 0.66:
        st.success("Priority Tier: HIGH")
    elif score_percent > 0.4:
        st.warning("Priority Tier: MEDIUM")
    else:
        st.info("Priority Tier: LOW")
