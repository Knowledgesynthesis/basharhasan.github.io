import streamlit as st
import pandas as pd

# Probability data for risk scores
data = {
    'Risk Score': list(range(-20, 49)),
    'Predicted Probability of Recmet (%)': [
        14.7486258, 16.09498237, 17.53895821, 19.08301786, 20.7288399,
        22.47717703, 24.32772007, 26.27897222, 28.32814063, 30.47105259,
        32.70210384, 35.01424563, 37.39901584, 39.846618, 42.34604897,
        44.88527378, 47.45144292, 50.03114428, 52.61067983, 55.17635509,
        57.71476835, 60.21308686, 62.65929819, 65.04242641, 67.35270594,
        69.58170804, 71.72241859, 73.76926821, 75.71811824, 77.56620818,
        79.31207124, 80.95542541, 82.49704735, 83.93863624, 85.28267387,
        86.53228617, 87.69111062, 88.76317258, 89.75277281, 90.66438746,
        91.50258111, 92.27193268, 92.97697389, 93.62213925, 94.21172666,
        94.74986736, 95.24050421, 95.68737688, 96.09401308, 96.46372463,
        96.79960751, 97.10454513, 97.38121393, 97.63209091, 97.85946242,
        98.06543386, 98.25193991, 98.42075499, 98.57350383, 98.71167178,
        98.83661497, 98.94957, 99.05166326, 99.14391974, 99.2272713,
        99.30256449, 99.3705678, 99.43197838, 99.48742835
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
def get_risk_probability(score, prob_data):
    if score in prob_data['Risk Score'].values:
        return prob_data[prob_data['Risk Score'] == score]['Predicted Probability of Recmet (%)'].values[0]
    else:
        return "Score out of range."

# Streamlit app
st.title("5-Year HCC Recurrence/Metastasis Risk Prediction")

st.header("Input Parameters")
who_grade = st.selectbox("WHO Grade", [1, 2, 3])
t_stage = st.selectbox("T Stage", [1, 2, 3, 4])
hepar = st.selectbox("Hepar", ['high', 'low'])
gpc = st.selectbox("GPC", ['+', '-'])
nuclear_area = st.slider("Nuclear Area %", 0.0, 100.0, 0.0, 1.0)
r_rpa = st.slider("r-RPA %", 0.0, 100.0, 0.0, 1.0)

# Calculate the risk score
risk_score = calculate_risk_score(who_grade, t_stage, hepar, gpc, nuclear_area, r_rpa)

# Get the associated risk probability
risk_probability = get_risk_probability(risk_score, prob_data)

st.header("Calculated Risk Score and Probability")
st.write(f"Calculated Risk Score: {risk_score}")
st.write(f"Associated Risk Probability: {risk_probability}")
