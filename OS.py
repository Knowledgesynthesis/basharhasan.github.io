import streamlit as st
import pandas as pd
import altair as alt

# Probability data for risk scores (directly added from the CSV)
data = {
    'Risk Score': [-27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
    'Predicted 3-Year Probability of Death (%)': [0.072, 0.085, 0.101, 0.119, 0.141, 0.166, 0.197, 0.233, 0.275, 0.326, 0.385, 0.455, 0.539, 0.637, 0.752, 0.889, 1.05, 1.24, 1.464, 1.728, 2.039, 2.403, 2.831, 3.333, 3.92, 4.605, 5.404, 6.331, 7.406, 8.646, 10.071, 11.701, 13.555, 15.65, 18.002, 20.622, 23.512, 26.673, 30.09, 33.744, 37.603, 41.627, 45.765, 49.962, 54.16, 58.299, 62.325, 66.187, 69.845, 73.268, 76.433, 79.328, 81.952, 84.309, 86.409, 88.268, 89.901, 91.33, 92.573, 93.651, 94.581, 95.381, 96.069, 96.657, 97.16, 97.59, 97.955],
    'Predicted 5-Year Probability of Death (%)': [0.717, 0.818, 0.934, 1.065, 1.214, 1.384, 1.578, 1.798, 2.048, 2.333, 2.655, 3.021, 3.435, 3.904, 4.435, 5.033, 5.707, 6.466, 7.317, 8.27, 9.336, 10.522, 11.84, 13.299, 14.907, 16.671, 18.599, 20.695, 22.96, 25.393, 27.991, 30.745, 33.644, 36.671, 39.807, 43.029, 46.311, 49.625, 52.943, 56.234, 59.472, 62.63, 65.683, 68.612, 71.4, 74.034, 76.505, 78.809, 80.942, 82.908, 84.709, 86.351, 87.843, 89.192, 90.407, 91.499, 92.477, 93.351, 94.129, 94.822, 95.436, 95.981, 96.464, 96.89, 97.266, 97.598, 97.891]
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
    if score in prob_data['Risk Score'].values:
        risk_3yr = prob_data[prob_data['Risk Score'] == score]['Predicted 3-Year Probability of Death (%)'].values[0]
        risk_5yr = prob_data[prob_data['Risk Score'] == score]['Predicted 5-Year Probability of Death (%)'].values[0]
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
prob_data_melted = prob_data.melt('Risk Score', var_name='Year', value_name='Probability')

# Plot for Death Risk
base_risk = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Death')]).mark_line().encode(
    x='Risk Score',
    y='Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Death Risk Probability'
)

dot_3yr_risk = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_3yr],
    'Year': ['3-Year Death Risk']
})).mark_point(size=100, color='yellow').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

dot_5yr_risk = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_5yr],
    'Year': ['5-Year Death Risk']
})).mark_point(size=100, color='red').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

chart_risk = base_risk + dot_3yr_risk + dot_5yr_risk
st.altair_chart(chart_risk, use_container_width=True)

# Create a new column for survival probabilities
prob_data_melted['Survival Probability'] = 100 - prob_data_melted['Probability']

# Plot for Overall Survival
base_survival = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Death')]).mark_line().encode(
    x='Risk Score',  # Ensure the column name matches your DataFrame
    y='Survival Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Overall Survival Probability'
)

dot_3yr_survival = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Survival Probability': [survival_3yr],
    'Year': ['3-Year Survival']
})).mark_point(size=100, color='yellow').encode(
    x='Risk Score',
    y='Survival Probability',
    tooltip=['Risk Score', 'Survival Probability']
)

dot_5yr_survival = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Survival Probability': [survival_5yr],
    'Year': ['5-Year Survival']
})).mark_point(size=100, color='red').encode(
    x='Risk Score',
    y='Survival Probability',
    tooltip=['Risk Score', 'Survival Probability']
)

chart_survival = base_survival + dot_3yr_survival + dot_5yr_survival
st.altair_chart(chart_survival, use_container_width=True)
