import streamlit as st
import pandas as pd
import pickle
import sqlite3
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Health Risk",
    page_icon="🩺",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

DB_FILE = "patient_history.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
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
            assessment_date TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# LOAD ML MODEL
# =========================================================

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    model_loaded = True

except Exception as e:
    model_loaded = False
    model_error = str(e)


# =========================================================
# PATIENT ID GENERATOR
# =========================================================

def generate_patient_id():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id
        FROM patients
        ORDER BY rowid DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return "PAT-0001"

    last_id = result[0]

    try:
        number = int(last_id.replace("PAT-", ""))
        return f"PAT-{number + 1:04d}"
    except:
        return "PAT-0001"


# =========================================================
# FIND EXISTING PATIENT
# =========================================================

def find_existing_patient(phone, patient_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    patient = None

    if phone.strip():
        cursor.execute("""
            SELECT patient_id, patient_name, phone, email
            FROM patients
            WHERE phone = ?
            LIMIT 1
        """, (phone.strip(),))

        patient = cursor.fetchone()

    if patient is None and patient_name.strip():
        cursor.execute("""
            SELECT patient_id, patient_name, phone, email
            FROM patients
            WHERE LOWER(patient_name) = LOWER(?)
            LIMIT 1
        """, (patient_name.strip(),))

        patient = cursor.fetchone()

    conn.close()

    return patient


# =========================================================
# SAVE PATIENT
# =========================================================

def save_patient(patient_id, patient_name, phone, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO patients
        (patient_id, patient_name, phone, email, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        patient_name,
        phone,
        email,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# =========================================================
# SAVE ASSESSMENT
# =========================================================

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
    risk_probability,
    risk_category
):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
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
        blood_pressure,
        glucose,
        cholesterol,
        physical_activity,
        smoking,
        family_history,
        risk_probability,
        risk_category,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# =========================================================
# GET PATIENTS
# =========================================================

def get_patients(search=""):
    conn = sqlite3.connect(DB_FILE)

    if search.strip():
        query = """
            SELECT patient_id, patient_name, phone, email, created_at
            FROM patients
            WHERE patient_id LIKE ?
               OR patient_name LIKE ?
               OR phone LIKE ?
            ORDER BY created_at DESC
        """

        search_value = f"%{search.strip()}%"

        df = pd.read_sql_query(
            query,
            conn,
            params=(search_value, search_value, search_value)
        )

    else:
        df = pd.read_sql_query("""
            SELECT patient_id, patient_name, phone, email, created_at
            FROM patients
            ORDER BY created_at DESC
        """, conn)

    conn.close()

    return df


# =========================================================
# GET HISTORY
# =========================================================

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


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7fbff;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

.hero {
    padding: 45px 35px;
    border-radius: 25px;
    background: linear-gradient(135deg, #e8f7ff, #f5fbff);
    border: 1px solid #d7edf8;
    margin-bottom: 25px;
}

.hero-label {
    color: #1687b7;
    font-weight: 700;
    letter-spacing: 2px;
    font-size: 14px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #12344d;
    margin-top: 10px;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 18px;
    color: #547080;
}

.section-title {
    color: #12344d;
    font-size: 25px;
    font-weight: 750;
    margin-top: 20px;
}

.info-card {
    padding: 22px;
    border-radius: 18px;
    background: white;
    border: 1px solid #e0edf4;
    box-shadow: 0 4px 15px rgba(20, 70, 90, 0.06);
}

.result-card {
    padding: 30px;
    border-radius: 20px;
    background: #ffffff;
    border: 1px solid #dbeaf1;
    text-align: center;
    margin-top: 25px;
}

.risk-number {
    font-size: 48px;
    font-weight: 800;
    color: #12344d;
}

.patient-id {
    font-size: 28px;
    font-weight: 800;
    color: #1687b7;
}

.footer {
    text-align: center;
    color: #71828c;
    font-size: 13px;
    margin-top: 35px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVIGATION
# =========================================================

page = st.radio(
    "Navigation",
    ["🏠 Home", "📋 Patient History"],
    horizontal=True,
    label_visibility="collapsed"
)


# =========================================================
# HOME PAGE
# =========================================================

if page == "🏠 Home":

    st.html("""
    <div class="hero">
        <div class="hero-label">🫀 AI HEALTH RISK</div>
        <div class="hero-title">YOUR HEALTH, OUR PRIORITY</div>
        <div class="hero-subtitle">
            AI-Based Health Risk Prediction System
        </div>
        <div class="hero-subtitle">
            Machine Learning Based Health Risk Assessment & Awareness Platform
        </div>
    </div>
    """)

    # Feature cards
    c1, c2, c3 = st.columns(3)

    with c1:
        st.html("""
        <div class="info-card">
            <h3>🔍 Early Risk Detection</h3>
            <p>Identify potential health risks using health and lifestyle information.</p>
        </div>
        """)

    with c2:
        st.html("""
        <div class="info-card">
            <h3>📊 Data Driven Insights</h3>
            <p>Machine learning based analysis of important health indicators.</p>
        </div>
        """)

    with c3:
        st.html("""
        <div class="info-card">
            <h3>🌱 A Healthier Tomorrow</h3>
            <p>Understand your risk level and become more aware of your health.</p>
        </div>
        """)

    st.markdown("---")

    st.markdown(
        '<div class="section-title">👤 Patient Information</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # PATIENT INFORMATION
    # =====================================================

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("### 🆔 Patient ID")
        st.info("Generated automatically")

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
        st.info("Patient ID will appear after prediction.")

    # =====================================================
    # HEALTH INFORMATION
    # =====================================================

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
        st.write("")

    st.markdown("")

    # =====================================================
    # PREDICT BUTTON
    # =====================================================

    predict_button = st.button(
        "🔮 Predict Health Risk",
        use_container_width=True,
        type="primary"
    )

    if predict_button:

        if not patient_name.strip():
            st.error("Please enter the Patient Name.")
            st.stop()

        if not model_loaded:
            st.error("Model files could not be loaded.")
            st.code(model_error)
            st.stop()

        # -------------------------------------------------
        # FIND OR CREATE PATIENT
        # -------------------------------------------------

        existing_patient = find_existing_patient(
            phone,
            patient_name
        )

        if existing_patient:

            patient_id = existing_patient[0]

            # Update contact information if supplied
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE patients
                SET patient_name = ?,
                    phone = ?,
                    email = ?
                WHERE patient_id = ?
            """, (
                patient_name,
                phone,
                email,
                patient_id
            ))

            conn.commit()
            conn.close()

        else:

            patient_id = generate_patient_id()

            save_patient(
                patient_id,
                patient_name,
                phone,
                email
            )

        # -------------------------------------------------
        # SHOW PATIENT ID
        # -------------------------------------------------

        st.html(f"""
        <div class="result-card">
            <div>YOUR PATIENT ID</div>
            <div class="patient-id">{patient_id}</div>
            <p>Please save this ID for viewing your future health history.</p>
        </div>
        """)

        # -------------------------------------------------
        # PREPARE MODEL INPUT
        # -------------------------------------------------

        smoking_value = 1 if smoking == "Yes" else 0
        family_history_value = 1 if family_history == "Yes" else 0

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

        try:

            input_scaled = scaler.transform(input_data)

            prediction = model.predict(input_scaled)[0]

            if hasattr(model, "predict_proba"):

                probability = model.predict_proba(input_scaled)[0][1]

            else:

                probability = float(prediction)

            percentage = probability * 100

            # -------------------------------------------------
            # RISK CATEGORY
            # -------------------------------------------------

            if percentage < 10:
                category = "LOW RISK"
                emoji = "🟢"

            elif percentage < 20:
                category = "MEDIUM RISK"
                emoji = "🟡"

            else:
                category = "HIGH RISK"
                emoji = "🔴"

            # -------------------------------------------------
            # SAVE ASSESSMENT
            # -------------------------------------------------

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

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            st.html(f"""
            <div class="result-card">
                <div style="font-size:20px;">Health Risk Assessment</div>
                <div class="risk-number">{percentage:.1f}%</div>
                <h2>{emoji} {category}</h2>
                <p>Patient ID: <b>{patient_id}</b></p>
            </div>
            """)

            # -------------------------------------------------
            # INSIGHTS
            # -------------------------------------------------

            st.markdown(
                '<div class="section-title">💡 Health Insights</div>',
                unsafe_allow_html=True
            )

            insight1, insight2, insight3 = st.columns(3)

            with insight1:

                if bmi < 18.5:
                    bmi_message = "BMI is below the commonly used healthy range."
                elif bmi < 25:
                    bmi_message = "BMI is within the commonly used healthy range."
                elif bmi < 30:
                    bmi_message = "BMI is above the commonly used healthy range."
                else:
                    bmi_message = "BMI is in the obesity range."

                st.info("**BMI Insight**\n\n" + bmi_message)

            with insight2:

                if blood_pressure < 120:
                    bp_message = "Systolic BP is below 120 mmHg."
                elif blood_pressure < 130:
                    bp_message = "Systolic BP is elevated."
                else:
                    bp_message = "Systolic BP is high and deserves attention."

                st.info("**Blood Pressure**\n\n" + bp_message)

            with insight3:

                if physical_activity >= 3:
                    activity_message = "Good level of physical activity."
                else:
                    activity_message = "Consider increasing regular physical activity."

                st.info("**Lifestyle**\n\n" + activity_message)

            st.success(
                f"Assessment saved successfully for Patient ID: {patient_id}"
            )

            st.warning(
                "⚠️ This result is for educational and health-awareness purposes only. "
                "It is not a medical diagnosis and should not replace advice from a qualified healthcare professional."
            )

        except Exception as e:

            st.error("Prediction could not be completed.")

            st.code(str(e))


# =========================================================
# PATIENT HISTORY PAGE
# =========================================================

else:

    st.html("""
    <div class="hero">
        <div class="hero-label">📋 PATIENT HISTORY</div>
        <div class="hero-title">PATIENT HEALTH RECORDS</div>
        <div class="hero-subtitle">
            Search Patient ID or Name to view previous assessments.
        </div>
    </div>
    """)

    search = st.text_input(
        "🔎 Search Patient",
        placeholder="Enter Patient ID, patient name or phone number"
    )

    patients_df = get_patients(search)

    if patients_df.empty:

        st.info("No patient records found.")

    else:

        st.markdown("### 👥 Patients")

        patient_options = patients_df["patient_id"].tolist()

        selected_patient = st.selectbox(
            "Select Patient",
            patient_options
        )

        selected_row = patients_df[
            patients_df["patient_id"] == selected_patient
        ].iloc[0]

        # -------------------------------------------------
        # PATIENT DETAILS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        history_df = get_history(selected_patient)

        if history_df.empty:

            st.info("No assessments found for this patient.")

        else:

            st.markdown("### 📈 Risk History")

            chart_df = history_df[
                ["assessment_date", "risk_probability"]
            ].copy()

            chart_df["assessment_date"] = pd.to_datetime(
                chart_df["assessment_date"]
            )

            chart_df = chart_df.set_index("assessment_date")

            st.line_chart(
                chart_df["risk_probability"],
                use_container_width=True
            )

            st.caption(
                "Risk probability (%) across previous assessments."
            )

            # -------------------------------------------------
            # ASSESSMENT TABLE
            # -------------------------------------------------

            st.markdown("### 📊 Previous Assessments")

            display_df = history_df.copy()

            display_df["risk_probability"] = (
                display_df["risk_probability"].round(1)
            )

            display_df = display_df.rename(columns={
                "assessment_date": "Date",
                "bmi": "BMI",
                "blood_pressure": "Blood Pressure",
                "glucose": "Glucose",
                "cholesterol": "Cholesterol",
                "physical_activity": "Activity Hours",
                "risk_probability": "Risk %",
                "risk_category": "Risk Category"
            })

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

            # -------------------------------------------------
            # SELECT ASSESSMENT
            # -------------------------------------------------

            st.markdown("### 🔍 Assessment Details")

            assessment_numbers = list(range(1, len(history_df) + 1))

            selected_number = st.selectbox(
                "Select Assessment",
                assessment_numbers,
                index=len(assessment_numbers) - 1
            )

            assessment = history_df.iloc[selected_number - 1]

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

            st.markdown("#### Health Details")

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
    AI Health Risk Prediction System • Machine Learning Based Health Awareness Platform
    <br><br>
    ⚠️ For educational and awareness purposes only. Not a substitute for professional medical advice.
</div>
""")
