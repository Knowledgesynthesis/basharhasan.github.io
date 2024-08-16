import streamlit as st
import pandas as pd
import altair as alt

# Probability data for risk scores (directly added from the CSV)
data = {
    'Risk Score': [-27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
    'Predicted 3-Year Probability of Death (%)': [0.072, 0.085, 0.101, 0.119, 0.141, 0.168, 0.199, 0.235, 0.277, 0.325, 0.379, 0.441, 0.51, 0.588, 0.675, 0.772, 0.879, 0.998, 1.13, 1.276, 1.438, 1.616, 1.812, 2.028, 2.264, 2.523, 2.806, 3.114, 3.45, 3.814, 4.209, 4.637, 5.099, 5.597, 6.134, 6.71, 7.329, 7.992, 8.702, 9.462, 10.273, 11.139, 12.063, 13.046, 14.093, 15.206, 16.388, 17.642, 18.972, 20.38, 21.869, 23.442, 25.101, 26.85, 28.692, 30.628, 32.661, 34.794, 37.03, 39.371, 41.819, 44.376, 47.044, 49.824, 52.719],
    'Predicted 5-Year Probability of Death (%)': [0.717, 0.818, 0.934, 1.065, 1.214, 1.381, 1.567, 1.774, 2.004, 2.257, 2.537, 2.845, 3.183, 3.553, 3.958, 4.4, 4.882, 5.407, 5.977, 6.595, 7.263, 7.984, 8.761, 9.596, 10.492, 11.452, 12.479, 13.575, 14.745, 15.991, 17.316, 18.724, 20.217, 21.799, 23.472, 25.241, 27.107, 29.075, 31.147, 33.327, 35.618, 38.022, 40.544, 43.186, 45.951, 48.843, 51.864, 55.018, 58.309, 61.739, 65.312, 69.033, 72.905, 76.932, 81.118, 85.467, 89.983, 94.67, 99.532, 104.574, 109.799, 115.213, 120.818, 126.619, 132.619]
}

prob_data = pd.DataFrame(data)

# Define the scoring function
def calculate_risk_score(study_grade_who, tstage, cirrhosis, portal_hyp, hepar_gpc_catv2, r_rpa):
    score = 0
    score += {1: 0, 2: 11, 3: 34}.get(study_grade_who, 0)
    score += {1: 0, 2: 0, 3: 9, 4: 16}.get(tstage, 0)
    score += {0: 0, 1: 6}.get(cirrhosis, 0)
    score += {0: 0, 1: 11}.get(portal_hyp, 0)
    score += {1: 0, 2: 1, 3: 10}.get(int(hepar_gpc_catv2), 0)
    score += -3 * round(int(r_rpa) / 10)
    return score

# Define the function to get the associated risk probabilities
def get_risk_probabilities(score, prob_data):
    row = prob_data[prob_data['risk_score'] == score]
    if not row.empty:
        risk_3yr = row['Predicted Probability of 3-Year Death (%)'].values[0]
        risk_5yr = row['Predicted Probability of 5-Year Death (%)'].values[0]
        survival_3yr = 100 - risk_3yr
        survival_5yr = 100 - risk_5yr
        return risk_3yr, risk_5yr, survival_3yr, survival_5yr
    else:
        return "Score out of range.", "Score out of range.", "Score out of range.", "Score out of range."

# Streamlit app
st.title("HCC Overall Survival Probability Calculator")

st.header("Input Parameters")
study_grade_who = st.selectbox("Study Grade WHO", [1, 2, 3])
tstage = st.selectbox("T Stage", [1, 2, 3, 4])
cirrhosis = st.selectbox("Cirrhosis", [0, 1])
portal_hyp = st.selectbox("Portal Hypertension", [0, 1])
hepar_gpc_catv2 = st.selectbox("Hepar/GPC Category", [1, 2, 3])
r_rpa = st.slider("r-RPA (100-reticloss pct)", 0, 100, 0, 1)

# Calculate the risk score
risk_score = calculate_risk_score(study_grade_who, tstage, cirrhosis, portal_hyp, hepar_gpc_catv2, r_rpa)

# Get the associated risk and survival probabilities
risk_3yr, risk_5yr, survival_3yr, survival_5yr = get_risk_probabilities(risk_score, prob_data)

st.header("Calculated Risk Score and Probabilities")
st.write(f"Calculated Risk Score: {risk_score}")
st.write(f"Associated 3-year Death Risk Probability: {risk_3yr}%")
st.write(f"Associated 5-year Death Risk Probability: {risk_5yr}%")
st.write(f"Associated 3-year Overall Survival Probability: {survival_3yr}%")
st.write(f"Associated 5-year Overall Survival Probability: {survival_5yr}%")

# Plotting
st.header("Risk Probability Plot")
prob_data_melted = prob_data.melt('risk_score', var_name='Year', value_name='Probability')

# Plot for Death Risk
base_risk = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Death')]).mark_line().encode(
    x='risk_score',
    y='Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Death Risk Probability'
)

dot_3yr_risk = alt.Chart(pd.DataFrame({
    'risk_score': [risk_score],
    'Probability': [risk_3yr],
    'Year': ['3-Year Death Risk']
})).mark_point(size=100, color='yellow').encode(
    x='risk_score',
    y='Probability',
    tooltip=['risk_score', 'Probability']
)

dot_5yr_risk = alt.Chart(pd.DataFrame({
    'risk_score': [risk_score],
    'Probability': [risk_5yr],
    'Year': ['5-Year Death Risk']
})).mark_point(size=100, color='red').encode(
    x='risk_score',
    y='Probability',
    tooltip=['risk_score', 'Probability']
)

chart_risk = base_risk + dot_3yr_risk + dot_5yr_risk
st.altair_chart(chart_risk, use_container_width=True)

# Plot for Overall Survival
prob_data_melted['Probability'] = 100 - prob_data_melted['Probability']
base_survival = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Death')]).mark_line().encode(
    x='risk_score',
    y='Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Overall Survival Probability'
)

dot_3yr_survival = alt.Chart(pd.DataFrame({
    'risk_score': [risk_score],
    'Probability': [survival_3yr],
    'Year': ['3-Year Survival']
})).mark_point(size=100, color='yellow').encode(
    x='risk_score',
    y='Probability',
    tooltip=['risk_score', 'Probability']
)

dot_5yr_survival = alt.Chart(pd.DataFrame({
    'risk_score': [risk_score],
    'Probability': [survival_5yr],
    'Year': ['5-Year Survival']
})).mark_point(size=100, color='red').encode(
    x='risk_score',
    y='Probability',
    tooltip=['risk_score', 'Probability']
)

chart_survival = base_survival + dot_3yr_survival + dot_5yr_survival
st.altair_chart(chart_survival, use_container_width=True)
