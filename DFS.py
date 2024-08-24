import streamlit as st
import pandas as pd
import altair as alt

# Probability data for risk scores
data = {
    'Risk Score': [-20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45],
    'Predicted 3-Year Probability of Any Event (%)': [1.68, 1.979, 2.329, 2.74, 3.22, 3.782, 4.437, 5.2, 6.085, 7.11, 8.292, 9.65, 11.203, 12.971, 14.97, 17.216, 19.722, 22.493, 25.529, 28.823, 32.357, 36.105, 40.03, 44.088, 48.225, 52.388, 56.517, 60.558, 64.46, 68.178, 71.678, 74.935, 77.933, 80.664, 83.131, 85.34, 87.304, 89.039, 90.562, 91.893, 93.051, 94.054, 94.92, 95.666, 96.306, 96.855, 97.325, 97.726, 98.068, 98.36, 98.608, 98.819, 98.999, 99.151, 99.28, 99.39, 99.483, 99.562, 99.629, 99.686, 99.734, 99.775, 99.809, 99.838, 99.863, 99.884],
    'Predicted 5-Year Probability of Any Event (%)': [3.494, 4.095, 4.795, 5.607, 6.547, 7.632, 8.879, 10.308, 11.937, 13.783, 15.863, 18.192, 20.777, 23.624, 26.729, 30.082, 33.662, 37.44, 41.378, 45.429, 49.541, 53.66, 57.729, 61.696, 65.513, 69.14, 72.546, 75.707, 78.612, 81.256, 83.64, 85.775, 87.672, 89.347, 90.819, 92.105, 93.225, 94.196, 95.035, 95.758, 96.38, 96.914, 97.371, 97.762, 98.096, 98.381, 98.624, 98.831, 99.007, 99.156, 99.284, 99.392, 99.484, 99.562, 99.629, 99.685, 99.733, 99.773, 99.808, 99.837, 99.862, 99.883, 99.901, 99.916, 99.928, 99.939]
}

prob_data = pd.DataFrame(data)

# Define the scoring function
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
