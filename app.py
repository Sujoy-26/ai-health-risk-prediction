import streamlit as st
import pandas as pd
import pickle

# ==============================
# LOAD MODEL
# ==============================

with open("health_model/model.pkl", "rb") as f:
    model = pickle.load(f)

with open("health_model/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


# ==============================
# PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="AI Health Risk Prediction",
    page_icon="🩺",
    layout="wide"
)


# ==============================
# CUSTOM CSS
# ==============================

st.markdown("""
<style>

.main {
    background-color: #f5f9ff;
}

.title-box {
    background: linear-gradient(135deg, #0072ff, #00c6ff);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
}

.title-box h1 {
    font-size: 42px;
    margin-bottom: 10px;
}

.title-box p {
    font-size: 18px;
}

.info-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.result-card {
    background: linear-gradient(135deg, #e8f5e9, #ffffff);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.10);
}

.metric-card {
    background: white;
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.08);
}

.footer {
    text-align: center;
    padding: 20px;
    color: #666;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# HEADER
# ==============================

st.markdown("""
<div class="title-box">

<h1>🩺 AI-Based Health Risk Prediction System</h1>

<p>
Machine Learning Based Health Risk Assessment & Awareness Platform
</p>

</div>
""", unsafe_allow_html=True)


# ==============================
# INTRODUCTION
# ==============================

st.markdown("""
<div class="info-card">

### 🔬 About the System

This AI-based system uses Machine Learning to estimate
a person's potential health risk using selected health
and lifestyle parameters.

The system analyzes factors such as age, BMI, blood pressure,
glucose, cholesterol, physical activity, smoking habits and
family history.

</div>
""", unsafe_allow_html=True)


st.info(
    "⚠️ This system is developed for academic, educational "
    "and health-awareness purposes only. It is NOT a medical "
    "diagnosis and should not replace a qualified healthcare professional."
)


st.divider()


# ==============================
# INPUT SECTION
# ==============================

st.header("👤 Personal & Health Information")

col1, col2, col3 = st.columns(3)


with col1:

    st.subheader("👤 Personal")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=30
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    bmi = st.number_input(
        "BMI",
        min_value=10.0,
        max_value=60.0,
        value=24.0,
        step=0.1
    )


with col2:

    st.subheader("❤️ Health Parameters")

    blood_pressure = st.number_input(
        "Systolic Blood Pressure",
        min_value=70,
        max_value=220,
        value=120
    )

    glucose = st.number_input(
        "Glucose Level",
        min_value=50,
        max_value=300,
        value=100
    )

    cholesterol = st.number_input(
        "Cholesterol Level",
        min_value=80,
        max_value=400,
        value=180
    )


with col3:

    st.subheader("🏃 Lifestyle")

    physical_activity = st.slider(
        "Physical Activity (hours/week)",
        min_value=0,
        max_value=20,
        value=3
    )

    smoking = st.selectbox(
        "Smoking Habit",
        ["No", "Yes"]
    )

    family_history = st.selectbox(
        "Family History of Diabetes",
        ["No", "Yes"]
    )


# Convert categorical values

smoking_value = 1 if smoking == "Yes" else 0

family_history_value = (
    1 if family_history == "Yes" else 0
)


st.divider()


# ==============================
# PREDICTION BUTTON
# ==============================

predict_button = st.button(
    "🔍 PREDICT HEALTH RISK",
    use_container_width=True
)


if predict_button:

    # ------------------------------
    # Prepare input
    # ------------------------------

    input_data = pd.DataFrame([{

        "Age": age,

        "BMI": bmi,

        "BloodPressure": blood_pressure,

        "Glucose": glucose,

        "Cholesterol": cholesterol,

        "PhysicalActivity": physical_activity,

        "Smoking": smoking_value,

        "FamilyHistory": family_history_value

    }])


    # ------------------------------
    # Scaling
    # ------------------------------

    input_scaled = scaler.transform(
        input_data
    )


    # ------------------------------
    # Prediction
    # ------------------------------

    prediction = model.predict(
        input_scaled
    )[0]


    probability = model.predict_proba(
        input_scaled
    )[0][1]


    percentage = probability * 100


    # ------------------------------
    # Risk Category
    # ------------------------------

    if percentage < 35:

        category = "LOW RISK"

        message = (
            "Your estimated risk level is relatively low."
        )

    elif percentage < 65:

        category = "MEDIUM RISK"

        message = (
            "Your estimated risk level is moderate. "
            "Maintaining a healthy lifestyle is recommended."
        )

    else:

        category = "HIGH RISK"

        message = (
            "Your estimated risk level is relatively high. "
            "Consider discussing your health parameters with "
            "a qualified healthcare professional."
        )


    # ==============================
    # RESULT
    # ==============================

    st.divider()

    st.header("📊 Prediction Result")


    result_col1, result_col2, result_col3 = st.columns(3)


    with result_col1:

        st.markdown(
            '<div class="metric-card">',
            unsafe_allow_html=True
        )

        st.metric(
            "Estimated Risk",
            f"{percentage:.2f}%"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    with result_col2:

        st.markdown(
            '<div class="metric-card">',
            unsafe_allow_html=True
        )

        st.metric(
            "Model Prediction",
            "Higher Risk" if prediction == 1
            else "Lower Risk"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    with result_col3:

        st.markdown(
            '<div class="metric-card">',
            unsafe_allow_html=True
        )

        st.metric(
            "Activity",
            f"{physical_activity} hrs/week"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # ==============================
    # RISK DISPLAY
    # ==============================

    if category == "LOW RISK":

        st.success(
            f"🟢 {category}"
        )

    elif category == "MEDIUM RISK":

        st.warning(
            f"🟡 {category}"
        )

    else:

        st.error(
            f"🔴 {category}"
        )


    st.progress(
        min(int(percentage), 100)
    )


    st.write(
        f"**Assessment:** {message}"
    )


    # ==============================
    # HEALTH INSIGHTS
    # ==============================

    st.divider()

    st.header("💡 Health Insights")


    insight1, insight2 = st.columns(2)


    with insight1:

        st.subheader("⚖️ BMI")

        if bmi < 18.5:

            st.write(
                "BMI is below the commonly used healthy range."
            )

        elif bmi < 25:

            st.write(
                "BMI is within the commonly used healthy range."
            )

        elif bmi < 30:

            st.write(
                "BMI is in the overweight range."
            )

        else:

            st.write(
                "BMI is in the obesity range."
            )


        st.subheader("🩸 Blood Pressure")

        if blood_pressure < 120:

            st.write(
                "Systolic blood pressure is below 120 mmHg."
            )

        elif blood_pressure < 130:

            st.write(
                "Systolic blood pressure is elevated."
            )

        else:

            st.write(
                "Systolic blood pressure is elevated and "
                "may require professional evaluation."
            )


    with insight2:

        st.subheader("🍬 Glucose")

        if glucose < 100:

            st.write(
                "Glucose level is below 100 mg/dL."
            )

        elif glucose < 126:

            st.write(
                "Glucose level is elevated."
            )

        else:

            st.write(
                "Glucose level is significantly elevated."
            )


        st.subheader("🏃 Physical Activity")

        if physical_activity >= 5:

            st.write(
                "Good level of reported physical activity."
            )

        else:

            st.write(
                "Increasing regular physical activity may "
                "support overall health."
            )


    # ==============================
    # RECOMMENDATIONS
    # ==============================

    st.divider()

    st.header("🌱 General Health Recommendations")

    rec1, rec2, rec3 = st.columns(3)


    with rec1:

        st.markdown("""
        ### 🥗 Healthy Diet

        Maintain a balanced diet with vegetables,
        fruits, whole grains and appropriate portions.
        """)


    with rec2:

        st.markdown("""
        ### 🏃 Physical Activity

        Maintain regular physical activity
        according to your individual abilities.
        """)


    with rec3:

        st.markdown("""
        ### 😴 Healthy Lifestyle

        Maintain adequate sleep and avoid
        smoking and other harmful habits.
        """)


    st.warning(
        "Medical Note: The values and recommendations "
        "shown here are general educational information. "
        "For personal medical advice, consult a qualified "
        "healthcare professional."
    )


# ==============================
# FOOTER
# ==============================

st.divider()

st.markdown("""
<div class="footer">

🩺 <b>AI-Based Health Risk Prediction System</b>

<br><br>

Developed as an Academic Machine Learning Project

<br>

© 2026 | Educational & Awareness Purpose Only

</div>
""", unsafe_allow_html=True)