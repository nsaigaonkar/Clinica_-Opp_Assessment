
import streamlit as st
import pandas as pd
import altair as alt
import openai
import json
import os

st.set_page_config(page_title="R&D Opportunity Explorer", layout="wide")
DATA_FILE = "client_data.json"
st.markdown("<style>body { font-family: 'Segoe UI'; }</style>", unsafe_allow_html=True)

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

st.markdown("<h1 style='color:#1A4D8F;'>Deloitte | R&D Opportunity Explorer</h1>", unsafe_allow_html=True)
st.markdown("**Understand, Analyze, and Act on Clinical Development Opportunities.** Built using human-centered design principles to guide your decisions.")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Deloitte.svg/2560px-Deloitte.svg.png", width=150)
st.sidebar.header("Add Client Profile")

with st.sidebar.form("client_form"):
    st.markdown("**Client Identity**")
    client_name = st.text_input("Client Name")
    rd_spend = st.number_input("R&D Spend (USD)", min_value=0, step=1000000)
    st.markdown("**Organization Profile**")
    footprint = st.selectbox("Global Footprint", ["Local", "Regional", "Global"])
    ta_focus = st.selectbox("Therapeutic Area Focus", ["Niche", "Moderate", "Broad"])
    pipeline = st.selectbox("Pipeline Complexity", ["Simple", "Moderate", "Complex"])
    st.markdown("**Digital & AI Maturity**")
    digital_maturity = st.selectbox("Digital Maturity", ["Low", "Medium", "High"])
    tech_maturity = st.selectbox("Clinical Tech Maturity", ["Outdated", "Developing", "Advanced"])
    data_platform = st.selectbox("Data Platform Maturity", ["On-Prem", "Hybrid", "Cloud-Native"])
    data_products = st.selectbox("Data Products Capability", ["Basic", "Intermediate", "Comprehensive"])
    ai_appetite = st.selectbox("GenAI Appetite", ["Low", "Medium", "High"])
    ai_maturity = st.selectbox("GenAI Maturity", ["Low", "Medium", "High"])
    ai_adoption = st.selectbox("GenAI Adoption", ["Low", "Medium", "High"])

    submitted = st.form_submit_button("Add Client")
    if submitted and client_name:
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

st.sidebar.markdown("---")
if st.sidebar.button("Reset All Client Data"):
    st.session_state.clients = []
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.experimental_rerun()

if st.session_state.clients:
    df = pd.DataFrame(st.session_state.clients)

    st.header("Client Portfolio Overview")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Clients", len(df))
    kpi2.metric("Total R&D Spend", f"${df['R&D Spend'].sum():,.0f}")
    avg_ai = df[["AI Appetite", "AI Maturity", "AI Adoption"]].applymap(lambda x: {"Low": 1, "Medium": 2, "High": 3}[x]).mean().mean()
    kpi3.metric("Avg. AI Maturity Score", f"{avg_ai:.1f} / 3")

    st.subheader("Client Table")
    st.dataframe(df, use_container_width=True)

    st.subheader("Revenue Opportunity Visualization")
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X("Client", sort="-y"),
        y=alt.Y("R&D Spend", title="R&D Spend ($)", scale=alt.Scale(zero=False)),
        tooltip=["Client", "R&D Spend", "AI Appetite", "Digital Maturity"]
    ).properties(height=400)
    st.altair_chart(bar, use_container_width=True)

    st.markdown("### Ask GPT-4 about your clients")
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    query = st.text_area("Ask a question like: 'Who is most ready for GenAI scale-up?'")

    if st.button("Ask GPT-4") and query and api_key:
        try:
            openai.api_key = api_key
            prompt = (
                "Here is a table of clients and their attributes:

"
                f"{df.to_csv(index=False)}

"
                f"Answer this question based on the data: {query}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600
            )
            st.markdown("**GPT-4 Answer:**")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Start by adding a client from the sidebar.")
