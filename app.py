import streamlit as st
import pandas as pd
import pickle
import sqlite3
import textwrap
from datetime import datetime


# ============================================================
# LOAD MODEL
# ============================================================

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


DB_FILE = "patient_history.db"


# ============================================================
# DATABASE
# ============================================================

def init_db():

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            email TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            assessment_date TEXT,
            age INTEGER,
            gender TEXT,
            bmi REAL,
            blood_pressure INTEGER,
            glucose INTEGER,
            cholesterol INTEGER,
            physical_activity INTEGER,
            smoking TEXT,
            family_history TEXT,
            risk_percentage REAL,
            risk_category TEXT,
            model_prediction TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_patient(
    patient_id,
    name,
    age,
    gender,
    phone,
    email
):

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO patients
        (
            patient_id,
            name,
            age,
            gender,
            phone,
            email,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        name,
        age,
        gender,
        phone,
        email,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


def save_assessment(
    patient_id,
    age,
    gender,
    bmi,
    blood_pressure,
    glucose,
    cholesterol,
    physical_activity,
    smoking,
    family_history,
    percentage,
    category,
    prediction
):

    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assessments
        (
            patient_id,
            assessment_date,
            age,
            gender,
            bmi,
            blood_pressure,
            glucose,
            cholesterol,
            physical_activity,
            smoking,
            family_history,
            risk_percentage,
            risk_category,
            model_prediction
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        age,
        gender,
        bmi,
        blood_pressure,
        glucose,
        cholesterol,
        physical_activity,
        smoking,
        family_history,
        percentage,
        category,
        prediction
    ))

    conn.commit()
    conn.close()


def get_patients(search=""):

    conn = sqlite3.connect(DB_FILE)

    if search:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM patients
            WHERE patient_id LIKE ?
            OR name LIKE ?
            ORDER BY name
            """,
            conn,
            params=(
                f"%{search}%",
                f"%{search}%"
            )
        )

    else:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM patients
            ORDER BY name
            """,
            conn
        )

    conn.close()

    return df


def get_patient(patient_id):

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM patients
        WHERE patient_id = ?
        """,
        conn,
        params=(patient_id,)
    )

    conn.close()

    return df


def get_history(patient_id):

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query(
        """
        SELECT
            assessment_date AS Date,
            risk_percentage AS Risk,
            risk_category AS Category,
            model_prediction AS Prediction,
            bmi AS BMI,
            blood_pressure AS BloodPressure,
            glucose AS Glucose,
            cholesterol AS Cholesterol,
            physical_activity AS Activity,
            smoking AS Smoking,
            family_history AS FamilyHistory
        FROM assessments
        WHERE patient_id = ?
        ORDER BY assessment_date DESC
        """,
        conn,
        params=(patient_id,)
    )

    conn.close()

    return df


init_db()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Health Risk",
    page_icon="🩺",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>

    /* =========================
       MAIN PAGE
       ========================= */

    .stApp {
        background-color: #f5f9ff !important;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }


    /* =========================
       GENERAL TEXT
       ========================= */

    .stApp p {
        color: #344563;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #102e68 !important;
    }


    /* =========================
       NAVBAR
       ========================= */

    .navbar {
        background: #ffffff;
        padding: 15px 22px;
        border-radius: 18px;
        margin-bottom: 22px;

        box-shadow:
            0 5px 20px rgba(30, 70, 120, 0.08);
    }

    .brand {
        color: #12356f !important;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #667085 !important;
        font-size: 12px;
        margin-top: 4px;
    }


    /* =========================
       HERO
       ========================= */

    .hero {
        background:
            linear-gradient(
                135deg,
                #dff1ff 0%,
                #c9e7ff 50%,
                #eef8ff 100%
            );

        border-radius: 24px;
        padding: 42px;
        margin-bottom: 25px;

        border: 1px solid #d3eaff;

        box-shadow:
            0 6px 25px rgba(30, 90, 150, 0.08);
    }

    .hero-label {
        color: #1267a8 !important;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .hero-title {
        color: #102e68 !important;
        font-size: 43px;
        font-weight: 800;
        line-height: 1.12;
        margin: 0;
    }

    .hero-text {
        color: #375477 !important;
        font-size: 18px;
        margin-top: 15px;
        line-height: 1.5;
    }

    .hero-features {
        display: flex;
        gap: 35px;
        margin-top: 28px;
    }

    .hero-feature {
        color: #183f75 !important;
        font-size: 14px;
        font-weight: 600;
    }


    /* =========================
       CARD
       ========================= */

    .main-card {
        background: #ffffff;

        padding: 26px;

        border-radius: 20px;

        box-shadow:
            0 5px 20px rgba(30, 70, 120, 0.08);

        border: 1px solid #edf2f7;

        margin-bottom: 22px;
    }


    /* =========================
       SECTION TITLE
       ========================= */

    .section-title {
        color: #102e68 !important;
        font-size: 27px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .section-subtitle {
        color: #64748b !important;
        font-size: 14px;
        margin-bottom: 20px;
    }


    /* =========================
       INPUT LABELS
       ========================= */

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stSlider label {
        color: #263b5a !important;
        font-weight: 650 !important;
    }


    /* =========================
       INPUT BOXES
       ========================= */

    .stTextInput input,
    .stNumberInput input {

        background-color: #ffffff !important;

        color: #172b4d !important;

        border: 1px solid #d8e1ec !important;

        border-radius: 10px !important;
    }


    .stTextInput input::placeholder {
        color: #8a98aa !important;
    }


    /* =========================
       SELECTBOX
       ========================= */

    div[data-baseweb="select"] > div {

        background-color: #ffffff !important;

        border: 1px solid #d8e1ec !important;

        border-radius: 10px !important;

        color: #172b4d !important;
    }

    div[data-baseweb="select"] span {

        color: #172b4d !important;
    }


    /* =========================
       RADIO NAVIGATION
       ========================= */

    div[role="radiogroup"] label {

        color: #17345f !important;

        font-weight: 650 !important;
    }


    /* =========================
       SLIDER
       ========================= */

    .stSlider label {
        color: #263b5a !important;
    }


    /* =========================
       BUTTON
       ========================= */

    .stButton > button {

        background:
            linear-gradient(
                135deg,
                #087ce8,
                #1565e8
            ) !important;

        color: #ffffff !important;

        border: none !important;

        border-radius: 13px !important;

        height: 55px;

        font-size: 17px;

        font-weight: 750;

        box-shadow:
            0 7px 18px rgba(18, 110, 230, 0.25);
    }

    .stButton > button:hover {

        background:
            linear-gradient(
                135deg,
                #076dce,
                #1258d5
            ) !important;

        color: #ffffff !important;
    }


    /* =========================
       METRICS
       ========================= */

    [data-testid="stMetricLabel"] {

        color: #526581 !important;

        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {

        color: #102e68 !important;

        font-weight: 800 !important;
    }


    /* =========================
       HISTORY CARD
       ========================= */

    .history-card {

        background: #ffffff;

        padding: 25px;

        border-radius: 18px;

        border: 1px solid #e5edf6;

        box-shadow:
            0 5px 20px rgba(30,70,120,.08);
    }


    /* =========================
       DISCLAIMER
       ========================= */

    .disclaimer {

        background: #e4f2ff;

        padding: 17px 22px;

        border-radius: 14px;

        text-align: center;

        color: #45627e !important;

        font-size: 12px;

        border: 1px solid #d0e8fb;
    }


    /* =========================
       MOBILE
       ========================= */

    @media (max-width: 768px) {

        .hero {
            padding: 28px;
        }

        .hero-title {
            font-size: 32px;
        }

        .hero-features {
            flex-direction: column;
            gap: 12px;
        }

    }

    </style>
    """),
    unsafe_allow_html=True
)


# ============================================================
# NAVBAR
# ============================================================

st.markdown(
    textwrap.dedent("""
    <div class="navbar">

        <div class="brand">
            🫀 AI Health Risk
        </div>

        <div class="brand-subtitle">
            Predict • Prevent • Live Better
        </div>

    </div>
    """),
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Navigation",
    [
        "🏠 Home",
        "📋 Patient History"
    ],
    horizontal=True,
    label_visibility="collapsed"
)


# ============================================================
# HOME PAGE
# ============================================================

if page == "🏠 Home":


    # ========================================================
    # HERO
    # ========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="hero">

            <div class="hero-label">
                YOUR HEALTH OUR PRIORITY
            </div>

            <div class="hero-title">
                AI-Based Health<br>
                Risk Prediction System
            </div>

            <div class="hero-text">
                Machine Learning Based Health Risk Assessment
                & Awareness Platform
            </div>

            <div class="hero-features">

                <div class="hero-feature">
                    🛡️ Early Risk Detection
                </div>

                <div class="hero-feature">
                    📊 Data Driven Insights
                </div>

                <div class="hero-feature">
                    👥 A Healthier Tomorrow
                </div>

            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    st.info(
        "⚠️ This system is developed for academic, "
        "educational and health-awareness purposes only. "
        "It is NOT a medical diagnosis."
    )


    # ========================================================
    # PATIENT INFORMATION
    # ========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="main-card">

            <div class="section-title">
                👤 Patient Information
            </div>

            <div class="section-subtitle">
                Enter patient details to save and track
                health assessments.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    p1, p2, p3 = st.columns(3)


    with p1:

        patient_id = st.text_input(
            "Patient ID",
            placeholder="Example: P001"
        )


    with p2:

        patient_name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name"
        )


    with p3:

        phone = st.text_input(
            "Phone Number",
            placeholder="Optional"
        )


    p4, p5 = st.columns(2)


    with p4:

        email = st.text_input(
            "Email",
            placeholder="Optional"
        )


    with p5:

        st.caption(
            "Patient ID is used to connect "
            "all previous assessments."
        )


    # ========================================================
    # HEALTH INFORMATION
    # ========================================================

    st.markdown(
        textwrap.dedent("""
        <div class="main-card">

            <div class="section-title">
                🩺 Health & Lifestyle Information
            </div>

            <div class="section-subtitle">
                Enter the health parameters used by
                the machine learning model.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(3)


    # ========================================================
    # PERSONAL
    # ========================================================

    with c1:

        st.subheader("👤 Personal")

        age = st.number_input(
            "Age (years)",
            min_value=18,
            max_value=100,
            value=30,
            step=1
        )


        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other"
            ]
        )


        bmi = st.number_input(
            "BMI (kg/m²)",
            min_value=10.0,
            max_value=60.0,
            value=24.0,
            step=0.1,
            format="%.2f"
        )


    # ========================================================
    # HEALTH
    # ========================================================

    with c2:

        st.subheader("❤️ Health Parameters")


        blood_pressure = st.number_input(
            "Systolic Blood Pressure (mmHg)",
            min_value=70,
            max_value=220,
            value=120,
            step=1
        )


        glucose = st.number_input(
            "Glucose Level (mg/dL)",
            min_value=50,
            max_value=300,
            value=100,
            step=1
        )


        cholesterol = st.number_input(
            "Cholesterol Level (mg/dL)",
            min_value=80,
            max_value=400,
            value=180,
            step=1
        )


    # ========================================================
    # LIFESTYLE
    # ========================================================

    with c3:

        st.subheader("🏃 Lifestyle")


        physical_activity = st.slider(
            "Physical Activity (hours/week)",
            min_value=0,
            max_value=20,
            value=3,
            step=1
        )


        smoking = st.selectbox(
            "Smoking Habit",
            [
                "No",
                "Yes"
            ]
        )


        family_history = st.selectbox(
            "Family History of Diabetes",
            [
                "No",
                "Yes"
            ]
        )


    # ========================================================
    # PREDICT BUTTON
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)


    b1, b2, b3 = st.columns(
        [1, 2, 1]
    )


    with b2:

        predict_button = st.button(
            "🫀 Predict Health Risk →",
            use_container_width=True
        )


    # ========================================================
    # PREDICTION
    # ========================================================

    if predict_button:


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not patient_id.strip():

            st.error(
                "Please enter a Patient ID."
            )

            st.stop()


        if not patient_name.strip():

            st.error(
                "Please enter the Patient Name."
            )

            st.stop()


        # ----------------------------------------------------
        # CATEGORICAL VALUES
        # ----------------------------------------------------

        smoking_value = (
            1
            if smoking == "Yes"
            else 0
        )


        family_history_value = (
            1
            if family_history == "Yes"
            else 0
        )


        # ----------------------------------------------------
        # INPUT DATA
        # ----------------------------------------------------

        input_data = pd.DataFrame([{

            "Age": age,

            "BMI": bmi,

            "BloodPressure":
                blood_pressure,

            "Glucose":
                glucose,

            "Cholesterol":
                cholesterol,

            "PhysicalActivity":
                physical_activity,

            "Smoking":
                smoking_value,

            "FamilyHistory":
                family_history_value

        }])


        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        try:

            input_scaled = scaler.transform(
                input_data
            )


            prediction = model.predict(
                input_scaled
            )[0]


            probability = model.predict_proba(
                input_scaled
            )[0][1]


            percentage = (
                probability * 100
            )


        except Exception as e:

            st.error(
                "Prediction error. Please check "
                "model.pkl and scaler.pkl."
            )

            st.exception(e)

            st.stop()


        # ====================================================
        # RISK CATEGORY
        # ====================================================

        if percentage < 10:

            category = "LOW RISK"

            message = (
                "Your estimated risk level "
                "is relatively low."
            )


        elif percentage < 20:

            category = "MEDIUM RISK"

            message = (
                "Your estimated risk level is "
                "moderate. Maintaining a healthy "
                "lifestyle is recommended."
            )


        else:

            category = "HIGH RISK"

            message = (
                "Your estimated risk level is "
                "relatively high. Consider discussing "
                "your health parameters with a "
                "qualified healthcare professional."
            )


        prediction_text = (
            "Higher Risk"
            if prediction == 1
            else "Lower Risk"
        )


        # ====================================================
        # SAVE PATIENT
        # ====================================================

        save_patient(

            patient_id.strip(),

            patient_name.strip(),

            age,

            gender,

            phone,

            email

        )


        # ====================================================
        # SAVE ASSESSMENT
        # ====================================================

        save_assessment(

            patient_id.strip(),

            age,

            gender,

            bmi,

            blood_pressure,

            glucose,

            cholesterol,

            physical_activity,

            smoking,

            family_history,

            percentage,

            category,

            prediction_text

        )


        # ====================================================
        # RESULT
        # ====================================================

        st.divider()

        st.header(
            "📊 Prediction Result"
        )


        r1, r2, r3 = st.columns(3)


        with r1:

            st.metric(
                "Estimated Risk",
                f"{percentage:.2f}%"
            )


        with r2:

            st.metric(
                "Risk Category",
                category
            )


        with r3:

            st.metric(
                "Model Prediction",
                prediction_text
            )


        # ----------------------------------------------------
        # CATEGORY MESSAGE
        # ----------------------------------------------------

        if category == "LOW RISK":

            st.success(
                "🟢 LOW RISK"
            )


        elif category == "MEDIUM RISK":

            st.warning(
                "🟡 MEDIUM RISK"
            )


        else:

            st.error(
                "🔴 HIGH RISK"
            )


        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        st.progress(
            min(
                max(
                    int(percentage),
                    0
                ),
                100
            )
        )


        st.write(
            f"**Risk Percentage:** "
            f"{percentage:.2f}%"
        )


        st.write(
            f"**Assessment:** {message}"
        )


        st.success(
            f"✅ Assessment saved successfully "
            f"for Patient ID: {patient_id}"
        )


        # ====================================================
        # HEALTH INSIGHTS
        # ====================================================

        st.divider()

        st.header(
            "💡 Health Insights"
        )


        i1, i2, i3 = st.columns(3)


        # ----------------------------------------------------
        # BMI
        # ----------------------------------------------------

        with i1:

            st.subheader(
                "⚖️ BMI"
            )


            if bmi < 18.5:

                st.info(
                    "BMI is below the commonly "
                    "used healthy range."
                )


            elif bmi < 25:

                st.success(
                    "BMI is within the commonly "
                    "used healthy range."
                )


            elif bmi < 30:

                st.warning(
                    "BMI is in the overweight range."
                )


            else:

                st.error(
                    "BMI is in the obesity range."
                )


        # ----------------------------------------------------
        # BLOOD PRESSURE
        # ----------------------------------------------------

        with i2:

            st.subheader(
                "🩸 Blood Pressure"
            )


            if blood_pressure < 120:

                st.success(
                    "Systolic blood pressure "
                    "is below 120 mmHg."
                )


            elif blood_pressure < 130:

                st.warning(
                    "Systolic blood pressure "
                    "is elevated."
                )


            else:

                st.warning(
                    "Systolic blood pressure is "
                    "elevated and may require "
                    "professional evaluation."
                )


        # ----------------------------------------------------
        # GLUCOSE
        # ----------------------------------------------------

        with i3:

            st.subheader(
                "🍬 Glucose"
            )


            if glucose < 100:

                st.success(
                    "Glucose level is below "
                    "100 mg/dL."
                )


            elif glucose < 126:

                st.warning(
                    "Glucose level is elevated."
                )


            else:

                st.error(
                    "Glucose level is significantly "
                    "elevated."
                )


# ============================================================
# PATIENT HISTORY PAGE
# ============================================================

else:


    st.header(
        "📋 Patient History"
    )


    st.write(
        "Search a Patient ID or patient name "
        "to view previous health assessments."
    )


    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(
        "🔎 Search Patient",
        placeholder="Example: P001 or Rahul"
    )


    patients = get_patients(
        search
    )


    if patients.empty:

        st.info(
            "No patients found. Create a patient "
            "assessment from the Home page first."
        )


    else:


        # ====================================================
        # PATIENT SELECT
        # ====================================================

        patient_options = (
            patients["patient_id"]
            + " — "
            + patients["name"]
        ).tolist()


        selected = st.selectbox(
            "Select Patient",
            patient_options
        )


        selected_id = selected.split(
            " — "
        )[0]


        patient = get_patient(
            selected_id
        )


        history = get_history(
            selected_id
        )


        # ====================================================
        # PATIENT INFORMATION
        # ====================================================

        if not patient.empty:

            person = patient.iloc[0]


            st.markdown(
                textwrap.dedent("""
                <div class="history-card">
                </div>
                """),
                unsafe_allow_html=True
            )


            h1, h2, h3, h4 = st.columns(4)


            with h1:

                st.metric(
                    "Patient ID",
                    person["patient_id"]
                )


            with h2:

                st.metric(
                    "Name",
                    person["name"]
                )


            with h3:

                st.metric(
                    "Age",
                    person["age"]
                )


            with h4:

                st.metric(
                    "Gender",
                    person["gender"]
                )


            if person["phone"]:

                st.write(
                    f"📞 **Phone:** "
                    f"{person['phone']}"
                )


            if person["email"]:

                st.write(
                    f"✉️ **Email:** "
                    f"{person['email']}"
                )


        # ====================================================
        # HISTORY
        # ====================================================

        if not history.empty:


            st.divider()


            # =================================================
            # RISK TREND
            # =================================================

            st.subheader(
                "📈 Risk History"
            )


            chart_data = history.copy()


            chart_data["Date"] = pd.to_datetime(
                chart_data["Date"]
            )


            chart_data = chart_data.sort_values(
                "Date"
            )


            st.line_chart(
                chart_data.set_index(
                    "Date"
                )["Risk"]
            )


            # =================================================
            # TABLE
            # =================================================

            st.subheader(
                "🗂️ Previous Assessments"
            )


            display_history = history[
                [
                    "Date",
                    "Risk",
                    "Category",
                    "Prediction"
                ]
            ].copy()


            display_history["Risk"] = (
                display_history["Risk"]
                .map(
                    lambda x:
                    f"{x:.2f}%"
                )
            )


            st.dataframe(
                display_history,

                use_container_width=True,

                hide_index=True
            )


            # =================================================
            # DETAILS
            # =================================================

            st.subheader(
                "🔍 Assessment Details"
            )


            selected_date = st.selectbox(
                "Select an assessment",
                history["Date"].tolist()
            )


            detail = history[
                history["Date"]
                == selected_date
            ].iloc[0]


            d1, d2, d3 = st.columns(3)


            with d1:

                st.write(
                    f"**BMI:** "
                    f"{detail['BMI']}"
                )


                st.write(
                    f"**Blood Pressure:** "
                    f"{detail['BloodPressure']} mmHg"
                )


                st.write(
                    f"**Glucose:** "
                    f"{detail['Glucose']} mg/dL"
                )


            with d2:

                st.write(
                    f"**Cholesterol:** "
                    f"{detail['Cholesterol']} mg/dL"
                )


                st.write(
                    f"**Physical Activity:** "
                    f"{detail['Activity']} hrs/week"
                )


                st.write(
                    f"**Smoking:** "
                    f"{detail['Smoking']}"
                )


            with d3:

                st.write(
                    f"**Family History:** "
                    f"{detail['FamilyHistory']}"
                )


                st.write(
                    f"**Risk:** "
                    f"{detail['Risk']:.2f}%"
                )


                st.write(
                    f"**Category:** "
                    f"{detail['Category']}"
                )


        else:

            st.info(
                "No assessment history available."
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()


st.markdown(
    textwrap.dedent("""
    <div class="disclaimer">

        ℹ️ <b>Disclaimer:</b>

        This tool provides an AI-based health risk
        assessment for educational and awareness
        purposes only.

        <br><br>

        It is not a substitute for professional
        medical advice, diagnosis, or treatment.

    </div>
    """),
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    textwrap.dedent("""
    <div style="
        text-align:center;
        padding:25px;
        color:#64748b;
        font-size:13px;
    ">

        🩺 <b>AI-Based Health Risk Prediction System</b>

        <br><br>

        Developed as an Academic Machine Learning Project

        <br>

        © 2026 | Educational & Awareness Purpose Only

    </div>
    """),
    unsafe_allow_html=True
)
