import streamlit as st
import pandas as pd
import pickle
import sqlite3
from datetime import datetime

st.set_page_config(
    page_title="AI Health Risk",
    page_icon="🩺",
    layout="wide"
)

DB_FILE = "patient_history.db"


# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            age REAL,
            gender TEXT,
            bmi REAL,
            blood_pressure REAL,
            glucose REAL,
            cholesterol REAL,
            physical_activity REAL,
            smoking TEXT,
            family_history TEXT,
            risk_probability REAL,
            risk_category TEXT,
            assessment_date TEXT
        )
    """)

    cur.execute("PRAGMA table_info(patients)")
    columns = {row[1] for row in cur.fetchall()}

    if "phone" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN phone TEXT")

    if "email" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN email TEXT")

    if "created_at" not in columns:
        cur.execute("ALTER TABLE patients ADD COLUMN created_at TEXT")

    conn.commit()
    conn.close()


init_db()


# ================= LOAD MODEL =================

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    MODEL_OK = True
    MODEL_ERROR = ""

except Exception as e:
    MODEL_OK = False
    MODEL_ERROR = str(e)


# ================= PATIENT ID =================

def generate_patient_id():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT patient_id
        FROM patients
        ORDER BY rowid DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    if row is None:
        return "PAT-0001"

    try:
        number = int(row[0].replace("PAT-", ""))
        return f"PAT-{number + 1:04d}"
    except Exception:
        return "PAT-0001"


def find_existing_patient(phone, name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    patient = None

    if phone and phone.strip():
        cur.execute("""
            SELECT patient_id, patient_name, phone, email
            FROM patients
            WHERE phone = ?
            LIMIT 1
        """, (phone.strip(),))

        patient = cur.fetchone()

    if patient is None and name and name.strip():
        cur.execute("""
            SELECT patient_id, patient_name, phone, email
            FROM patients
            WHERE LOWER(patient_name) = LOWER(?)
            LIMIT 1
        """, (name.strip(),))

        patient = cur.fetchone()

    conn.close()

    return patient


def save_patient(patient_id, name, phone, email):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO patients
        (patient_id, patient_name, phone, email, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        name.strip(),
        phone.strip(),
        email.strip(),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def update_patient(patient_id, name, phone, email):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        UPDATE patients
        SET patient_name = ?, phone = ?, email = ?
        WHERE patient_id = ?
    """, (
        name.strip(),
        phone.strip(),
        email.strip(),
        patient_id
    ))

    conn.commit()
    conn.close()


# ================= ASSESSMENT =================

def save_assessment(
    patient_id,
    age,
    gender,
    bmi,
    bp,
    glucose,
    cholesterol,
    activity,
    smoking,
    family_history,
    risk,
    category
):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assessments (
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
            risk_probability,
            risk_category,
            assessment_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        age,
        gender,
        bmi,
        bp,
        glucose,
        cholesterol,
        activity,
        smoking,
        family_history,
        risk,
        category,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_patients(search=""):
    conn = sqlite3.connect(DB_FILE)

    if search.strip():
        value = f"%{search.strip()}%"

        df = pd.read_sql_query("""
            SELECT patient_id, patient_name, phone, email, created_at
            FROM patients
            WHERE patient_id LIKE ?
               OR patient_name LIKE ?
               OR phone LIKE ?
            ORDER BY created_at DESC
        """, conn, params=(value, value, value))

    else:
        df = pd.read_sql_query("""
            SELECT patient_id, patient_name, phone, email, created_at
            FROM patients
            ORDER BY created_at DESC
        """, conn)

    conn.close()

    return df


def get_history(patient_id):
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
        SELECT
            id,
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
            risk_probability,
            risk_category
        FROM assessments
        WHERE patient_id = ?
        ORDER BY assessment_date ASC
    """, conn, params=(patient_id,))

    conn.close()

    return df


# ================= CSS =================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: #f4f9fc !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}


/* HERO */

.hero {
    background: linear-gradient(135deg, #e3f6ff, #ffffff);
    border: 1px solid #c8e6f2;
    border-radius: 28px;
    padding: 42px;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(30,90,120,.08);
}

.hero-label {
    color: #087da8 !important;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-title {
    color: #123b55 !important;
    font-size: 42px;
    line-height: 1.15;
    font-weight: 900;
    margin: 8px 0 12px 0;
}

.hero-subtitle {
    color: #4e6e7f !important;
    font-size: 17px;
    line-height: 1.6;
}


/* SECTION */

.section-title {
    color: #087da8 !important;
    font-size: 25px;
    font-weight: 850;
    margin: 25px 0 15px 0;
}


/* CARDS */

.feature-card {
    background: #ffffff !important;
    border: 1px solid #d5e7ef;
    border-radius: 20px;
    padding: 24px;
    min-height: 150px;
    box-shadow: 0 7px 20px rgba(30,80,100,.07);
}

.feature-card h3 {
    color: #123b55 !important;
    font-size: 19px;
    font-weight: 850;
    margin: 0 0 12px 0;
}

.feature-card p {
    color: #587180 !important;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
}


/* PATIENT ID */

.id-card {
    background: #e7f7ff !important;
    border: 1px solid #bfe3f1;
    border-radius: 16px;
    padding: 16px;
    text-align: center;
}

.id-card .small {
    color: #52717f !important;
    font-size: 12px;
    font-weight: 800;
}

.id-card .id-text {
    color: #087da8 !important;
    font-size: 21px;
    font-weight: 900;
    margin-top: 5px;
}


/* RESULT */

.result-card {
    background: #ffffff !important;
    border: 1px solid #d5e7ef;
    border-radius: 24px;
    padding: 30px;
    text-align: center;
    margin-top: 25px;
    box-shadow: 0 10px 28px rgba(20,70,90,.08);
}

.result-label {
    color: #607986 !important;
    font-size: 14px;
    font-weight: 750;
}

.risk-number {
    color: #123b55 !important;
    font-size: 52px;
    font-weight: 900;
    margin: 5px 0;
}

.patient-id-text {
    color: #087da8 !important;
    font-size: 28px;
    font-weight: 900;
}


/* LABELS */

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] div {
    color: #24495d !important;
    font-weight: 650 !important;
}


/* INPUT */

[data-testid="stTextInput"] input {
    color: #ffffff !important;
    background-color: #292b34 !important;
    border-radius: 10px !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #d5d8dd !important;
}

[data-testid="stNumberInput"] input {
    color: #ffffff !important;
    background-color: #292b34 !important;
    border-radius: 10px !important;
}


/* SELECT */

[data-baseweb="select"] {
    background-color: #292b34 !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] * {
    color: #ffffff !important;
}


/* INFO */

[data-testid="stAlert"] * {
    color: #176b94 !important;
}


/* BUTTON */

.stButton > button {
    background: #087da8 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 750 !important;
    min-height: 48px;
}

.stButton > button:hover {
    background: #066b90 !important;
    color: #ffffff !important;
}


/* METRICS */

[data-testid="stMetricLabel"] {
    color: #52717f !important;
}

[data-testid="stMetricValue"] {
    color: #123b55 !important;
}


/* FOOTER */

.footer {
    color: #71848f !important;
    text-align: center;
    font-size: 12px;
    line-height: 1.7;
    margin-top: 35px;
}


/* NAVIGATION */

div[role="radiogroup"] {
    display: flex !important;
    justify-content: center !important;
    gap: 12px !important;
    margin: 8px 0 25px 0 !important;
}

div[role="radiogroup"] label {
    background: #ffffff !important;
    border: 1px solid #d5e7ef !important;
    border-radius: 12px !important;
    padding: 9px 20px !important;
    cursor: pointer !important;
}

div[role="radiogroup"] label p {
    color: #123b55 !important;
    font-weight: 750 !important;
}

div[role="radiogroup"] label:hover {
    background: #e8f7ff !important;
    border-color: #087da8 !important;
}

div[role="radiogroup"] label[data-checked="true"] {
    background: #087da8 !important;
    border-color: #087da8 !important;
}

div[role="radiogroup"] label[data-checked="true"] p {
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)


# ================= NAVIGATION =================

page = st.radio(
    "Navigation",
    [
        "🏠 Home",
        "📋 Patient History"
    ],
    horizontal=True,
    label_visibility="collapsed"
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.html("""
    <div class="hero">

        <div class="hero-label">
            🫀 AI HEALTH RISK
        </div>

        <div class="hero-title">
            YOUR HEALTH, OUR PRIORITY
        </div>

        <div class="hero-subtitle">
            AI-Based Health Risk Prediction System
        </div>

        <div class="hero-subtitle">
            Machine Learning Based Health Risk
            Assessment & Awareness Platform
        </div>

    </div>
    """)


    # FEATURES

    c1, c2, c3 = st.columns(3)

    with c1:
        st.html("""
        <div class="feature-card">
            <h3>🔍 Early Risk Detection</h3>
            <p>
                Identify potential health risks using
                health and lifestyle information.
            </p>
        </div>
        """)

    with c2:
        st.html("""
        <div class="feature-card">
            <h3>📊 Data Driven Insights</h3>
            <p>
                Machine learning based analysis of
                important health indicators.
            </p>
        </div>
        """)

    with c3:
        st.html("""
        <div class="feature-card">
            <h3>🌱 A Healthier Tomorrow</h3>
            <p>
                Understand your risk level and become
                more aware of your health.
            </p>
        </div>
        """)


    # PATIENT INFORMATION

    st.markdown(
        '<div class="section-title">👤 Patient Information</div>',
        unsafe_allow_html=True
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        st.html("""
        <div class="id-card">
            <div class="small">PATIENT ID</div>
            <div class="id-text">AUTO GENERATED</div>
        </div>
        """)

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
        st.info(
            "Patient ID will be shown automatically after prediction."
        )


    # HEALTH INFORMATION

    st.markdown(
        '<div class="section-title">🩺 Health Information</div>',
        unsafe_allow_html=True
    )

    h1, h2, h3, h4 = st.columns(4)

    with h1:
        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=25
        )

    with h2:
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )

    with h3:
        bmi = st.number_input(
            "BMI",
            min_value=5.0,
            max_value=80.0,
            value=22.0,
            step=0.1
        )

    with h4:
        blood_pressure = st.number_input(
            "Systolic Blood Pressure",
            min_value=60,
            max_value=250,
            value=120
        )

    h5, h6, h7, h8 = st.columns(4)

    with h5:
        glucose = st.number_input(
            "Glucose",
            min_value=40,
            max_value=500,
            value=100
        )

    with h6:
        cholesterol = st.number_input(
            "Cholesterol",
            min_value=50,
            max_value=500,
            value=180
        )

    with h7:
        physical_activity = st.number_input(
            "Physical Activity (hours/week)",
            min_value=0.0,
            max_value=50.0,
            value=3.0,
            step=0.5
        )

    with h8:
        smoking = st.selectbox(
            "Smoking",
            ["No", "Yes"]
        )

    l1, l2 = st.columns(2)

    with l1:
        family_history = st.selectbox(
            "Family History of Disease",
            ["No", "Yes"]
        )

    with l2:
        st.write("")


    # PREDICT

    predict_button = st.button(
        "🔮 Predict Health Risk",
        use_container_width=True,
        type="primary"
    )


    if predict_button:

        if not patient_name.strip():

            st.error(
                "Please enter the Patient Name."
            )

            st.stop()


        if not MODEL_OK:

            st.error(
                "Model files could not be loaded."
            )

            st.code(MODEL_ERROR)

            st.stop()


        # FIND EXISTING PATIENT

        existing = find_existing_patient(
            phone,
            patient_name
        )


        if existing:

            patient_id = existing[0]

            update_patient(
                patient_id,
                patient_name,
                phone,
                email
            )

        else:

            patient_id = generate_patient_id()

            save_patient(
                patient_id,
                patient_name,
                phone,
                email
            )


        # MODEL INPUT

        smoking_value = (
            1 if smoking == "Yes"
            else 0
        )

        family_history_value = (
            1 if family_history == "Yes"
            else 0
        )


        input_data = pd.DataFrame([
            {
                "Age": age,
                "BMI": bmi,
                "BloodPressure": blood_pressure,
                "Glucose": glucose,
                "Cholesterol": cholesterol,
                "PhysicalActivity": physical_activity,
                "Smoking": smoking_value,
                "FamilyHistory": family_history_value
            }
        ])


        try:

            input_scaled = scaler.transform(
                input_data
            )

            prediction = model.predict(
                input_scaled
            )[0]


            if hasattr(model, "predict_proba"):

                probability = model.predict_proba(
                    input_scaled
                )[0][1]

            else:

                probability = float(
                    prediction
                )


            percentage = probability * 100


            # RISK CATEGORY

            if percentage < 10:

                category = "LOW RISK"
                emoji = "🟢"

            elif percentage < 20:

                category = "MEDIUM RISK"
                emoji = "🟡"

            else:

                category = "HIGH RISK"
                emoji = "🔴"


            # SAVE

            save_assessment(
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
                category
            )


            # RESULT

            st.html(f"""
            <div class="result-card">

                <div class="result-label">
                    YOUR PATIENT ID
                </div>

                <div class="patient-id-text">
                    {patient_id}
                </div>

                <br>

                <div class="result-label">
                    HEALTH RISK SCORE
                </div>

                <div class="risk-number">
                    {percentage:.1f}%
                </div>

                <h2>
                    {emoji} {category}
                </h2>

                <div class="result-label">
                    Patient: {patient_name}
                </div>

            </div>
            """)


            # INSIGHTS

            st.markdown(
                '<div class="section-title">💡 Health Insights</div>',
                unsafe_allow_html=True
            )


            i1, i2, i3 = st.columns(3)


            if bmi < 18.5:

                bmi_message = (
                    "BMI is below the commonly "
                    "used healthy range."
                )

            elif bmi < 25:

                bmi_message = (
                    "BMI is within the commonly "
                    "used healthy range."
                )

            elif bmi < 30:

                bmi_message = (
                    "BMI is above the commonly "
                    "used healthy range."
                )

            else:

                bmi_message = (
                    "BMI is in the obesity range."
                )


            if blood_pressure < 120:

                bp_message = (
                    "Systolic BP is below "
                    "120 mmHg."
                )

            elif blood_pressure < 130:

                bp_message = (
                    "Systolic BP is elevated."
                )

            else:

                bp_message = (
                    "Systolic BP is high and "
                    "deserves attention."
                )


            if physical_activity >= 3:

                activity_message = (
                    "Good level of physical activity."
                )

            else:

                activity_message = (
                    "Consider increasing regular "
                    "physical activity."
                )


            with i1:

                st.info(
                    "**BMI Insight**\n\n"
                    + bmi_message
                )


            with i2:

                st.info(
                    "**Blood Pressure**\n\n"
                    + bp_message
                )


            with i3:

                st.info(
                    "**Lifestyle**\n\n"
                    + activity_message
                )


            st.success(
                f"Assessment saved successfully. "
                f"Patient ID: {patient_id}"
            )


            st.warning(
                "⚠️ This result is for educational and "
                "health-awareness purposes only. It is not "
                "a medical diagnosis and should not replace "
                "advice from a qualified healthcare professional."
            )


        except Exception as e:

            st.error(
                "Prediction could not be completed."
            )

            st.code(str(e))


# =========================================================
# PATIENT HISTORY
# =========================================================

else:

    st.html("""
    <div class="hero">

        <div class="hero-label">
            📋 PATIENT HISTORY
        </div>

        <div class="hero-title">
            PATIENT HEALTH RECORDS
        </div>

        <div class="hero-subtitle">
            Search Patient ID, name or phone number
            to view previous assessments.
        </div>

    </div>
    """)


    search = st.text_input(
        "🔎 Search Patient",
        placeholder="Example: PAT-0001 or patient name"
    )


    patients_df = get_patients(search)


    if patients_df.empty:

        st.info(
            "No patient records found."
        )


    else:

        selected_patient = st.selectbox(
            "Select Patient",
            patients_df["patient_id"].tolist()
        )


        selected_row = patients_df[
            patients_df["patient_id"]
            == selected_patient
        ].iloc[0]


        st.markdown(
            '<div class="section-title">'
            '👤 Patient Details'
            '</div>',
            unsafe_allow_html=True
        )


        d1, d2, d3, d4 = st.columns(4)


        with d1:

            st.metric(
                "Patient ID",
                selected_row["patient_id"]
            )


        with d2:

            st.metric(
                "Patient Name",
                selected_row["patient_name"]
            )


        with d3:

            st.metric(
                "Phone",
                selected_row["phone"]
                if selected_row["phone"]
                else "Not provided"
            )


        with d4:

            st.metric(
                "Email",
                selected_row["email"]
                if selected_row["email"]
                else "Not provided"
            )


        history_df = get_history(
            selected_patient
        )


        if history_df.empty:

            st.info(
                "No assessments found for this patient."
            )


        else:

            # RISK HISTORY

            st.markdown(
                '<div class="section-title">'
                '📈 Risk History'
                '</div>',
                unsafe_allow_html=True
            )


            chart_df = history_df[
                [
                    "assessment_date",
                    "risk_probability"
                ]
            ].copy()


            chart_df["assessment_date"] = (
                pd.to_datetime(
                    chart_df["assessment_date"]
                )
            )


            chart_df = chart_df.set_index(
                "assessment_date"
            )


            st.line_chart(
                chart_df["risk_probability"],
                use_container_width=True
            )


            st.caption(
                "Risk probability (%) across "
                "previous assessments."
            )


            # TABLE

            st.markdown(
                '<div class="section-title">'
                '📊 Previous Assessments'
                '</div>',
                unsafe_allow_html=True
            )


            display_df = history_df.copy()


            display_df[
                "risk_probability"
            ] = display_df[
                "risk_probability"
            ].round(1)


            display_df = display_df.rename(
                columns={
                    "assessment_date":
                        "Date",

                    "bmi":
                        "BMI",

                    "blood_pressure":
                        "Blood Pressure",

                    "glucose":
                        "Glucose",

                    "cholesterol":
                        "Cholesterol",

                    "physical_activity":
                        "Activity Hours",

                    "risk_probability":
                        "Risk %",

                    "risk_category":
                        "Risk Category"
                }
            )


            st.dataframe(
                display_df[
                    [
                        "Date",
                        "BMI",
                        "Blood Pressure",
                        "Glucose",
                        "Cholesterol",
                        "Activity Hours",
                        "Risk %",
                        "Risk Category"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


            # DETAILS

            st.markdown(
                '<div class="section-title">'
                '🔍 Assessment Details'
                '</div>',
                unsafe_allow_html=True
            )


            numbers = list(
                range(
                    1,
                    len(history_df) + 1
                )
            )


            selected_number = st.selectbox(
                "Select Assessment",
                numbers,
                index=len(numbers) - 1
            )


            assessment = history_df.iloc[
                selected_number - 1
            ]


            a1, a2, a3, a4 = st.columns(4)


            with a1:

                st.metric(
                    "Risk",
                    f"{assessment['risk_probability']:.1f}%"
                )


            with a2:

                st.metric(
                    "Category",
                    assessment["risk_category"]
                )


            with a3:

                st.metric(
                    "BMI",
                    f"{assessment['bmi']:.1f}"
                )


            with a4:

                st.metric(
                    "Glucose",
                    f"{assessment['glucose']:.0f}"
                )


            detail_df = pd.DataFrame({

                "Parameter": [

                    "Age",
                    "Gender",
                    "BMI",
                    "Blood Pressure",
                    "Glucose",
                    "Cholesterol",
                    "Physical Activity",
                    "Smoking",
                    "Family History",
                    "Assessment Date"

                ],

                "Value": [

                    assessment["age"],
                    assessment["gender"],
                    assessment["bmi"],
                    assessment["blood_pressure"],
                    assessment["glucose"],
                    assessment["cholesterol"],
                    assessment["physical_activity"],
                    assessment["smoking"],
                    assessment["family_history"],
                    assessment["assessment_date"]

                ]

            })


            st.dataframe(
                detail_df,
                use_container_width=True,
                hide_index=True
            )


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">

    AI Health Risk Prediction System
    • Machine Learning Based Health Awareness Platform

    <br>

    ⚠️ For educational and awareness purposes only.
    Not a substitute for professional medical advice.

</div>
""")
