import streamlit as st
import pandas as pd
import altair as alt

# Probability data for risk scores
data = {
    'Risk Score': list(range(-20, 49)),
    'Predicted 3-Year Probability of Recmet (%)': [
        6.9, 7.6, 8.4, 9.4, 10.4, 11.4, 12.6, 13.9, 15.3, 16.9, 18.5, 20.3, 22.1, 24.1, 26.3,
        28.5, 30.9, 33.3, 35.9, 38.5, 41.2, 44, 46.7, 49.6, 52.4, 55.2, 57.9, 60.7, 63.3, 65.9,
        68.4, 70.8, 73, 75.2, 77.2, 79.2, 81, 82.6, 84.2, 85.6, 87, 88.2, 89.3, 90.3, 91.3,
        92.1, 92.9, 93.6, 94.3, 94.8, 95.4, 95.8, 96.3, 96.7, 97, 97.3, 97.6, 97.8, 98.1, 98.3,
        98.5, 98.6, 98.8, 98.9, 99, 99.1, 99.2, 99.3, 99.4
    ],
    'Predicted 5-Year Probability of Recmet (%)': [
        14.7, 16.1, 17.5, 19.1, 20.7, 22.5, 24.3, 26.3, 28.3, 30.5, 32.7, 35, 37.4, 39.8, 42.3,
        44.9, 47.5, 50, 52.6, 55.2, 57.7, 60.2, 62.7, 65, 67.4, 69.6, 71.7, 73.8, 75.7, 77.6,
        79.3, 81, 82.5, 83.9, 85.3, 86.5, 87.7, 88.8, 89.8, 90.7, 91.5, 92.3, 93, 93.6, 94.2,
        94.7, 95.2, 95.7, 96.1, 96.5, 96.8, 97.1, 97.4, 97.6, 97.9, 98.1, 98.3, 98.4, 98.6,
        98.7, 98.8, 98.9, 99.1, 99.1, 99.2, 99.3, 99.4, 99.4, 99.5
    ]
}
prob_data = pd.DataFrame(data)

# Define the scoring function
def calculate_risk_score(who_grade, t_stage, hepar, gpc, nuclear_area, r_rpa):
    score = 0
    # WHO Grade
    if who_grade == 2:
        score += 6
    elif who_grade == 3:
        score += 26
    
    # T Stage
    if t_stage == 2:
        score += 4
    elif t_stage in [3, 4]:
        score += 12
    
    # Hepar and GPC
    if hepar == 'low' or gpc == '+':
        score += 1
    
    # Nuclear Area Percentage
    if nuclear_area < 15:
        score += 0
    elif 15 <= nuclear_area < 20:
        score += 3
    elif 20 <= nuclear_area < 25:
        score += 6
    elif nuclear_area >= 25:
        score += 9
    
    # r-RPA
    score += round(-2 * (r_rpa / 10))  # Subtract 2 points for each 10% increase

    return score

# Define the function to get the associated risk
def get_risk_probability(score, prob_data, year):
    column_name = f'Predicted {year}-Year Probability of Recmet (%)'
    if score in prob_data['Risk Score'].values:
        return prob_data[prob_data['Risk Score'] == score][column_name].values[0]
    else:
        return "Score out of range."

# Streamlit app
st.title("HCC Recurrence/Metastasis Risk Prediction")

st.header("Input Parameters")
who_grade = st.selectbox("WHO Grade", [1, 2, 3])
t_stage = st.selectbox("T Stage", [1, 2, 3, 4])
hepar = st.selectbox("Hepar", ['high', 'low'])
gpc = st.selectbox("GPC", ['+', '-'])
nuclear_area = st.slider("Nuclear Area %", 0.0, 100.0, 0.0, 1.0)
r_rpa = st.slider("r-RPA %", 0.0, 100.0, 0.0, 1.0)

# Calculate the risk score
risk_score = calculate_risk_score(who_grade, t_stage, hepar, gpc, nuclear_area, r_rpa)

# Get the associated risk probabilities
risk_probability_3yr = get_risk_probability(risk_score, prob_data, 3)
risk_probability_5yr = get_risk_probability(risk_score, prob_data, 5)

st.header("Calculated Risk Score and Probability")
st.write(f"Calculated Risk Score: {risk_score}")
st.write(f"Associated 3-year rec-met Risk Probability: {risk_probability_3yr}%")
st.write(f"Associated 5-year rec-met Risk Probability: {risk_probability_5yr}%")

# Plotting
st.header("Risk Probability Plot")
prob_data_melted = prob_data.melt('Risk Score', var_name='Year', value_name='Probability')

base = alt.Chart(prob_data_melted).mark_line().encode(
    x='Risk Score',
    y='Probability',
    color='Year'
).properties(
    title='3-Year and 5-Year Recurrence/Metastasis Risk Probability'
)

dot_3yr = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_probability_3yr],
    'Year': ['3-Year']
})).mark_point(size=100, color='blue').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

dot_5yr = alt.Chart(pd.DataFrame({
    'Risk Score': [risk_score],
    'Probability': [risk_probability_5yr],
    'Year': ['5-Year']
})).mark_point(size=100, color='red').encode(
    x='Risk Score',
    y='Probability',
    tooltip=['Risk Score', 'Probability']
)

chart = base + dot_3yr + dot_5yr

st.altair_chart(chart, use_container_width=True)
