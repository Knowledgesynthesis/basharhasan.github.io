import streamlit as st
import pandas as pd

# Define a function to calculate the risk score
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

    # Hepar/GPC
    if hepar == 'low' or gpc == 'positive':
        score += 4
    elif hepar == 'low' and gpc == 'positive':
        score += 10

    # Nuclear Area Percentage
    if nuclear_area < 5:
        score += 0
    elif 5 <= nuclear_area < 15:
        score += 3
    elif 15 <= nuclear_area < 25:
        score += 6
    elif nuclear_area >= 25:
        score += 9

    # r-RPA
    score += -2 * (r_rpa / 10)  # Subtract 2 points for each 10% increase

    return score

# Create Streamlit app
st.title('5 Year Rec-Met Risk Prediction Calculator')

# Input fields
who_grade = st.selectbox('WHO Grade', [1, 2, 3])
t_stage = st.selectbox('T Stage', [1, 2, 3, 4])
hepar = st.selectbox('Hepar', ['low', 'high'])
gpc = st.selectbox('GPC', ['positive', 'negative'])
nuclear_area = st.slider('Nuclear Area (%)', 0, 100)
r_rpa = st.slider('r-RPA (%)', 0, 100)

# Calculate risk score
if st.button('Calculate'):
    score = calculate_risk_score(who_grade, t_stage, hepar, gpc, nuclear_area, r_rpa)
    st.write(f'Calculated Risk Score: {score}')

    # Load your probability data
    prob_data = pd.read_csv('full_range_probabilities.csv')
    risk_probability = prob_data[prob_data['risk_score'] == score]['Predicted'].values[0]
    st.write(f'Predicted Probability of Recurrence/Metastasis: {risk_probability:.2f}%')
