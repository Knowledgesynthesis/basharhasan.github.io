import streamlit as st
import pandas as pd
import altair as alt

# Probability data for risk scores (directly added from the CSV)
data = {
    'Risk Score': [-9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
    'Predicted 3-Year Probability of Any Event (%)': [9.65, 11.2, 12.97, 14.97, 17.22, 19.72, 22.49, 25.53, 28.82, 32.36, 36.11, 40.03, 44.09, 48.23, 52.39, 56.52, 60.56, 64.46, 68.18, 71.68, 74.94, 77.93, 80.66, 83.13, 85.34, 87.3, 89.04, 90.56, 91.89, 93.05, 94.05, 94.92, 95.67, 96.31, 96.86, 97.32, 97.73, 98.07, 98.36, 98.61, 98.82, 99, 99.15, 99.28],
    'Predicted 5-Year Probability of Any Event (%)': [18.19, 20.78, 23.62, 26.73, 30.08, 33.66, 37.44, 41.38, 45.43, 49.54, 53.66, 57.73, 61.7, 65.51, 69.14, 72.55, 75.71, 78.61, 81.26, 83.64, 85.77, 87.67, 89.35, 90.82, 92.11, 93.22, 94.2, 95.03, 95.76, 96.38, 96.91, 97.37, 97.76, 98.1, 98.38, 98.62, 98.83, 99.01, 99.16, 99.28, 99.39, 99.48, 99.56, 99.63]
}

prob_data = pd.DataFrame(data)

# Define the scoring function with the updated user-friendly interface
def calculate_risk_score(who_grade, tstage, multifocality, nuclear_area, r_rpa, hepar, gpc):
    score = 0
    # WHO Grade
    score += {1: 0, 2: 4, 3: 24}.get(who_grade, 0)
    # T Stage
    score += {1: 0, 2: 2, 3: 9, 4: 10}.get(tstage, 0)
    # Multifocality
    score += {False: 0, True: 1}.get(multifocality, 0)
    # Mean Nuclear Area Percentage
    if nuclear_area < 15:
        score += 0
    elif 15 <= nuclear_area < 20:
        score += 3
    elif 20 <= nuclear_area < 25:
        score += 6
    else:  # above 25
        score += 9
    # R-RPA adjusted to the nearest integer
    score += -2 * round(int(r_rpa) / 10)
    # Hepar/GPC calculation
    if hepar == "high" and gpc == "negative":
        score += 0
    elif (hepar == "high" and gpc == "positive") or (hepar == "low" and gpc == "negative"):
        score += 1
    elif hepar == "low" and gpc == "positive":
        score += 1
    
    return score

# Define the function to get the associated risk probabilities
def get_risk_probabilities(score, prob_data):
    if score in prob_data['Risk Score'].values:
        risk_3yr = prob_data[prob_data['Risk Score'] == score]['Predicted 3-Year Probability of Any Event (%)'].values[0]
        risk_5yr = prob_data[prob_data['Risk Score'] == score]['Predicted 5-Year Probability of Any Event (%)'].values[0]
        dfs_3yr = 100 - risk_3yr
        dfs_5yr = 100 - risk_5yr
        return risk_3yr, risk_5yr, dfs_3yr, dfs_5yr
    else:
        return "Score out of range.", "Score out of range.", "Score out of range.", "Score out of range."

# Streamlit app
st.title("HCC Any Event Probability Calculator")

st.header("Input Parameters")

# Updated user-friendly inputs
who_grade = st.selectbox("WHO Grade", [1, 2, 3])
tstage = st.selectbox("T Stage", [1, 2, 3, 4])
multifocality = st.selectbox("Multifocality", ["No", "Yes"]) == "Yes"
nuclear_area = st.slider("Mean Nuclear Area %", 0.0, 100.0, 0.0, 1.0)
r_rpa = st.slider("r-RPA %", 0, 100, 0, 1)
hepar = st.selectbox("Hepar", ["high", "low"])
gpc = st.selectbox("GPC", ["negative", "positive"])

# Calculate the risk score
risk_score = calculate_risk_score(who_grade, tstage, multifocality, nuclear_area, r_rpa, hepar, gpc)

# Get the associated risk and survival probabilities
risk_3yr, risk_5yr, dfs_3yr, dfs_5yr = get_risk_probabilities(risk_score, prob_data)

st.header("Calculated Risk Score and Probabilities")
st.write(f"Calculated Risk Score: {risk_score}")
st.write(f"Associated 3-year Any Event Risk Probability: {risk_3yr}%")
st.write(f"Associated 5-year Any Event Risk Probability: {risk_5yr}%")
st.write(f"Associated 3-year Disease-Free Survival Probability: {dfs_3yr}%")
st.write(f"Associated 5-year Disease-Free Survival Probability: {dfs_5yr}%")

# Plotting
st.header("Risk Probability Plot")
prob_data_melted = prob_data.melt('Risk Score', var_name='Year', value_name='Probability')

# Plot for Any Event Risk
base_risk = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Any Event')]).mark_line().encode(
    x='Risk Score',
    y='Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Any Event Risk Probability'
)

dot_3yr_risk = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_3yr],
    'Year': ['3-Year Any Event Risk']
})).mark_point(size=100, color='yellow').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

dot_5yr_risk = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_5yr],
    'Year': ['5-Year Any Event Risk']
})).mark_point(size=100, color='red').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

chart_risk = base_risk + dot_3yr_risk + dot_5yr_risk
st.altair_chart(chart_risk, use_container_width=True)

# Create a new column for DFS probabilities
prob_data_melted['DFS Probability'] = 100 - prob_data_melted['Probability']

# Plot for Disease-Free Survival (DFS)
base_dfs = alt.Chart(prob_data_melted[prob_data_melted['Year'].str.contains('Any Event')]).mark_line().encode(
    x='Risk Score',
    y='DFS Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Disease-Free Survival Probability'
)

dot_3yr_dfs = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'DFS Probability': [dfs_3yr],
    'Year': ['3-Year DFS']
})).mark_point(size=100, color='yellow').encode(
    x='Risk Score',
    y='DFS Probability',
tooltip=['Risk Score', 'DFS Probability']
)

dot_5yr_dfs = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'DFS Probability': [dfs_5yr],
    'Year': ['5-Year DFS']
})).mark_point(size=100, color='red').encode(
    x='Risk Score',
    y='DFS Probability',
    tooltip=['Risk Score', 'DFS Probability']
)

chart_dfs = base_dfs + dot_3yr_dfs + dot_5yr_dfs
st.altair_chart(chart_dfs, use_container_width=True)
