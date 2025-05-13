import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# Final logistic regression coefficients (updated based on new scoring system)
coef_str = [0.044]  # for stricture
intercept_str = -3.9

coef_dil = [0.041]  # for stricture + dilation
intercept_dil = -3.7

coef_rng = [0.034]  # for rings
intercept_rng = -2.1

# Scoring system using 5 predictors and updated multipliers
def calculate_scores(age, disease_duration, eosinophils, fibrosis_score, remodeling_score):
    age_scaled = min(age // 10, 8)
    duration_scaled = min(disease_duration, 15)
    eos_scaled = min(eosinophils // 10, 10)
    fib_scaled = min(fibrosis_score // 10, 30)
    remodeling_scaled = min(remodeling_score // 100, 50)

    score_str = fib_scaled * 2 + eos_scaled * 1 + age_scaled * 2 + duration_scaled * 4 + remodeling_scaled * 1
    score_dil = fib_scaled * 2 + eos_scaled * 1 + age_scaled * 2 + duration_scaled * 4 + remodeling_scaled * 1
    score_rng = fib_scaled * 1 + eos_scaled * 2 + age_scaled * 1 + duration_scaled * 1 + remodeling_scaled * 1

    return score_str, score_dil, score_rng

# Logistic probability prediction
def predict_probability(score, coef, intercept):
    log_odds = coef[0] * score + intercept
    return 1 / (1 + np.exp(-log_odds))

# Streamlit UI
st.title("EoE Fibrosis Risk Calculator (Updated Model)")

age = st.slider("Age (years)", 0, 80, 25)
disease_duration = st.slider("Disease duration (years)", 0, 15, 3)
eosinophils = st.slider("Eosinophils (per HPF)", 0, 100, 50)
fibrosis_score = st.slider("AI Fibrosis Score (0–300)", 0, 300, 80)
remodeling_score = st.slider("Remodeling Score 3 (Fib x Basal %)", 0, 5000, 1200)

# Auto-calculate without a button
score_str, score_dil, score_rng = calculate_scores(age, disease_duration, eosinophils, fibrosis_score, remodeling_score)

p_str = predict_probability(score_str, coef_str, intercept_str)
p_dil = predict_probability(score_dil, coef_dil, intercept_dil)
p_rng = predict_probability(score_rng, coef_rng, intercept_rng)

st.subheader("Predicted Probabilities")
st.write(f"**Stricture:** {p_str:.2%} (Score: {score_str})")
st.write(f"**Stricture + Dilation:** {p_dil:.2%} (Score: {score_dil})")
st.write(f"**Rings:** {p_rng:.2%} (Score: {score_rng})")

# Probability curve
st.header("Risk Probability Plot")
score_range = np.arange(0, 601)
prob_df = pd.DataFrame({
    'Risk Score': score_range,
    'Stricture': predict_probability(score_range, coef_str, intercept_str),
    'Stricture + Dilation': predict_probability(score_range, coef_dil, intercept_dil),
    'Rings': predict_probability(score_range, coef_rng, intercept_rng)
})
melted = prob_df.melt(id_vars='Risk Score', var_name='Outcome', value_name='Probability')

base = alt.Chart(melted).mark_line().encode(
    x='Risk Score',
    y='Probability',
    color='Outcome'
).properties(
    title='Probability of Fibrostenotic Outcomes by Risk Score'
)

dots = alt.Chart(pd.DataFrame({
    'Risk Score': [score_str, score_dil, score_rng],
    'Probability': [p_str, p_dil, p_rng],
    'Outcome': ['Stricture', 'Stricture + Dilation', 'Rings']
})).mark_point(size=100).encode(
    x='Risk Score',
    y='Probability',
    color='Outcome',
    tooltip=['Outcome', 'Risk Score', 'Probability']
)

chart = base + dots
st.altair_chart(chart, use_container_width=True)
