import streamlit as st
import numpy as np
from sklearn.linear_model import LogisticRegression

# Define logistic regression coefficients from final trained models (assumed refit values)
# These are representative values based on previous logistic fits
coef_str = [0.065]  # per unit risk score (stricture)
intercept_str = -4.5

coef_dil = [0.06]  # per unit risk score (stricture + dilation)
intercept_dil = -4.2

coef_rng = [0.05]  # per unit risk score (rings)
intercept_rng = -2.5

# Risk scoring logic (same point system from previous steps)
def calculate_scores(age, disease_duration, eosinophils, fibrosis_score):
    age_scaled = min(age // 10, 8)
    duration_scaled = min(disease_duration, 15)
    eos_scaled = min(eosinophils // 10, 10)
    fib_scaled = min(fibrosis_score // 10, 30)

    score_str = fib_scaled * 4 + eos_scaled * 2 + age_scaled * 3 + duration_scaled * 12
    score_dil = fib_scaled * 3 + eos_scaled * 2 + age_scaled * 3 + duration_scaled * 12
    score_rng = fib_scaled * 2 + eos_scaled * 3 + age_scaled * 2 + duration_scaled * 2

    return score_str, score_dil, score_rng

# Logistic prediction
def predict_probability(score, coef, intercept):
    log_odds = coef[0] * score + intercept
    return 1 / (1 + np.exp(-log_odds))

# Streamlit UI
st.title("EoE Fibrosis Risk Calculator")
st.markdown("Estimate the probability of developing strictures, strictures with dilation, and rings based on clinical and histologic features.")

age = st.slider("Age (years)", 0, 80, 25)
disease_duration = st.slider("Disease duration (years)", 0, 15, 3)
eosinophils = st.slider("Eosinophils (per HPF)", 0, 100, 50)
fibrosis_score = st.slider("AI Fibrosis Score", 0, 300, 80)

if st.button("Calculate"):
    score_str, score_dil, score_rng = calculate_scores(age, disease_duration, eosinophils, fibrosis_score)

    p_str = predict_probability(score_str, coef_str, intercept_str)
    p_dil = predict_probability(score_dil, coef_dil, intercept_dil)
    p_rng = predict_probability(score_rng, coef_rng, intercept_rng)

    st.subheader("Predicted Probabilities")
    st.write(f"**Stricture:** {p_str:.2%} (Score: {score_str})")
    st.write(f"**Stricture + Dilation:** {p_dil:.2%} (Score: {score_dil})")
    st.write(f"**Rings:** {p_rng:.2%} (Score: {score_rng})")
