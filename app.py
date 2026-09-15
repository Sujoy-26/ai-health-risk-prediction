import streamlit as st
import pandas as pd
import pickle
import uuid
import html
from supabase import create_client


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Health Risk",
    page_icon="🩺",
    layout="wide"
)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

try:

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

except Exception as e:

    st.error("Supabase connection failed.")
    st.exception(e)
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


# ============================================================
# RESTORE SUPABASE SESSION
# ============================================================

if (
    st.session_state.access_token
    and st.session_state.refresh_token
):

    try:

        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

    except Exception:

        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None


# ============================================================
# LOAD ML MODEL
# ============================================================

try:

    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

except Exception as e:

    st.error(
        "model.pkl or scaler.pkl could not be loaded."
    )

    st.exception(e)
    st.stop()


# ============================================================
# AUTH FUNCTIONS
# ============================================================

def register_user(
    name,
    email,
    phone,
    password
):

    try:

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": name,
                        "phone": phone
                    }
                }
            }
        )

        if response.user is not None:

            if response.session is None:

                st.success(
                    "Account created successfully!"
                )

                st.info(
                    "Please check your email and verify "
                    "your account before logging in."
                )

            else:

                st.success(
                    "Account created successfully!"
                )

                st.session_state.user = response.user

                st.session_state.access_token = (
                    response.session.access_token
                )

                st.session_state.refresh_token = (
                    response.session.refresh_token
                )

            return True

        return False

    except Exception as e:

        st.error(
            f"Registration failed: {e}"
        )

        return False


def login_user(
    email,
    password
):

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        if response.user is not None:

            st.session_state.user = response.user

            if response.session is not None:

                st.session_state.access_token = (
                    response.session.access_token
                )

                st.session_state.refresh_token = (
                    response.session.refresh_token
                )

                # Immediately apply authenticated session
                supabase.auth.set_session(
                    response.session.access_token,
                    response.session.refresh_token
                )

            return True

        return False

    except Exception as e:

        st.error(
            f"Login failed: {e}"
        )

        return False


def logout_user():

    try:

        supabase.auth.sign_out()

    except Exception:

        pass

    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None

    st.rerun()


# ============================================================
# AUTH PAGE
# ============================================================

def show_auth_page():

    st.html("""
    <style>

    .auth-box {
        max-width: 650px;
        margin: 40px auto 35px auto;
        background: white;
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 8px 35px rgba(30,70,120,.12);
        text-align: center;
    }

    .auth-title {
        color: #12356f;
        font-size: 40px;
        font-weight: 800;
    }

    .auth-subtitle {
        color: #68778d;
        font-size: 17px;
        margin-top: 8px;
    }

    </style>

    <div class="auth-box">

        <div class="auth-title">
            🩺 AI Health Risk
        </div>

        <div class="auth-subtitle">
            Predict • Prevent • Live Better
        </div>

    </div>
    """)


    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )


    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Welcome Back")

        login_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if not login_email.strip():

                st.error(
                    "Please enter your email."
                )

            elif not login_password:

                st.error(
                    "Please enter your password."
                )

            else:

                if login_user(
                    login_email.strip(),
                    login_password
                ):

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()


    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.subheader(
            "Create Your Account"
        )

        register_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="register_name"
        )

        register_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="register_email"
        )

        register_phone = st.text_input(
            "Phone Number",
            placeholder="Enter phone number",
            key="register_phone"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            placeholder="Minimum 6 characters",
            key="register_password"
        )

        register_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter password",
            key="register_confirm"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True
        ):

            if not register_name.strip():

                st.error(
                    "Please enter your name."
                )

            elif not register_email.strip():

                st.error(
                    "Please enter your email."
                )

            elif not register_phone.strip():

                st.error(
                    "Please enter your phone number."
                )

            elif len(register_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            elif register_password != register_confirm:

                st.error(
                    "Passwords do not match."
                )

            else:

                register_user(
                    register_name.strip(),
                    register_email.strip(),
                    register_phone.strip(),
                    register_password
                )

    st.divider()

    st.caption(
        "🔒 Authentication is securely handled by Supabase."
    )


# ============================================================
# SHOW LOGIN IF NOT LOGGED IN
# ============================================================

if st.session_state.user is None:

    show_auth_page()

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

current_user = st.session_state.user

USER_ID = current_user.id

USER_EMAIL = current_user.email or ""


# ============================================================
# GLOBAL CSS
# ============================================================

st.html("""
<style>

/* ----------------------------------------------------------
   APP
---------------------------------------------------------- */

.stApp {
    background: #f5f9ff;
}

.block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}


/* ----------------------------------------------------------
   FIX STREAMLIT LABEL COLORS
---------------------------------------------------------- */

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stSlider label {
    color: #12356f !important;
    font-weight: 600 !important;
}
/* FORCE TEXT TO DARK COLOR */

.stRadio label,
.stRadio p,
.stRadio div[role="radiogroup"] label {
    color: #12356f !important;
    font-weight: 600 !important;
}

.stRadio div[role="radiogroup"] label span {
    color: #12356f !important;
}

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #12356f !important;
}

.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4,
.stMarkdown h5,
.stMarkdown h6 {
    color: #12356f !important;
}

.stMarkdown p,
.stMarkdown li,
.stMarkdown span {
    color: #45627e !important;
}

.stSelectbox,
.stTextInput,
.stNumberInput,
.stSlider {
    color: #12356f !important;
}

div[data-testid="stRadio"] label {
    color: #12356f !important;
}

.stCaption,
div[data-testid="stCaptionContainer"] {
    color: #45627e !important;
}

.stTextInput p,
.stNumberInput p,
.stSelectbox p,
.stSlider p {
    color: #45627e !important;
}

.stCaption {
    color: #45627e !important;
}


/* ----------------------------------------------------------
   NAVBAR
---------------------------------------------------------- */

.navbar {
    background: white;
    padding: 20px 25px;
    border-radius: 18px;
    margin-bottom: 18px;
    box-shadow: 0 4px 18px rgba(30,70,120,.08);
}

.brand {
    color: #12356f;
    font-size: 28px;
    font-weight: 800;
}

.nav-subtitle {
    color: #68778d;
    font-size: 13px;
    margin-top: 3px;
}


/* ----------------------------------------------------------
   USER BOX
---------------------------------------------------------- */

.user-box {
    background: white;
    padding: 13px 18px;
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(30,70,120,.08);
    color: #12356f;
}


/* ----------------------------------------------------------
   HERO
---------------------------------------------------------- */

.hero {
    background: linear-gradient(
        135deg,
        #dff1ff,
        #c9e7ff,
        #eef8ff
    );

    border-radius: 24px;
    padding: 45px;
    margin: 25px 0;

    box-shadow: 0 8px 30px rgba(30,70,120,.08);
}

.hero-label {
    color: #1267a8;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero-title {
    color: #102e68;
    font-size: 43px;
    font-weight: 800;
    line-height: 1.12;
}

.hero-text {
    color: #375477;
    font-size: 18px;
    margin-top: 15px;
}


/* ----------------------------------------------------------
   FEATURE CARDS
---------------------------------------------------------- */

.feature-card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    min-height: 145px;
    box-shadow: 0 5px 20px rgba(30,70,120,.08);
    margin-bottom: 20px;
}

.feature-card h3 {
    color: #12356f;
    margin-bottom: 10px;
}

.feature-card p {
    color: #68778d;
    line-height: 1.5;
}


/* ----------------------------------------------------------
   SECTION HEADER
---------------------------------------------------------- */

.section-header {
    background: white;
    padding: 20px 25px;
    border-radius: 18px;
    margin-top: 25px;
    margin-bottom: 15px;
    box-shadow: 0 5px 20px rgba(30,70,120,.07);
}

.section-header h2 {
    color: #12356f;
    margin: 0;
    font-size: 27px;
}


/* ----------------------------------------------------------
   DISCLAIMER
---------------------------------------------------------- */

.disclaimer {
    background: #e4f2ff;
    padding: 17px 20px;
    border-radius: 14px;
    color: #45627e;
    text-align: center;
    font-size: 13px;
    margin: 20px 0;
}


/* ----------------------------------------------------------
   HISTORY CARD
---------------------------------------------------------- */

.history-card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 5px 20px rgba(30,70,120,.08);
}


/* ----------------------------------------------------------
   RESULT CARD
---------------------------------------------------------- */

.result-card {
    background: white;
    padding: 28px;
    border-radius: 20px;
    box-shadow: 0 5px 20px rgba(30,70,120,.08);
    margin-top: 20px;
}

.result-title {
    color: #12356f;
    font-size: 28px;
    font-weight: 800;
}

.patient-id {
    color: #45627e;
    font-size: 17px;
    margin-top: 8px;
}


/* ----------------------------------------------------------
   MOBILE
---------------------------------------------------------- */

@media (max-width: 768px) {

    .hero {
        padding: 28px;
    }

    .hero-title {
        font-size: 32px;
    }

}

</style>
""")


# ============================================================
# NAVBAR
# ============================================================

st.html("""
<div class="navbar">

    <div class="brand">
        🩺 AI Health Risk
    </div>

    <div class="nav-subtitle">
        Predict • Prevent • Live Better
    </div>

</div>
""")


# ============================================================
# USER BAR
# ============================================================

user_col, logout_col = st.columns([5, 1])

with user_col:

    safe_email = html.escape(USER_EMAIL)

    st.html(f"""
    <div class="user-box">
        👤 <b>Logged in:</b> {safe_email}
    </div>
    """)

with logout_col:

    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout_user()


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def generate_patient_id():

    return (
        "P-"
        + uuid.uuid4().hex[:8].upper()
    )


def save_patient(
    patient_id,
    patient_name,
    phone,
    email
):

    try:

        data = {

            "patient_id": patient_id,

            "patient_name": patient_name,

            "phone": phone,

            "email": email,

            "user_id": USER_ID

        }

        response = (
            supabase
            .table("patients")
            .insert(data)
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"Patient save error: {e}"
        )

        return False


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

    try:

        data = {

            "patient_id": patient_id,

            "age": age,

            "gender": gender,

            "bmi": bmi,

            "blood_pressure": blood_pressure,

            "glucose": glucose,

            "cholesterol": cholesterol,

            "physical_activity": physical_activity,

            "smoking": smoking,

            "family_history": family_history,

            "risk_probability": risk_probability,

            "risk_category": risk_category,

            "user_id": USER_ID

        }

        response = (
            supabase
            .table("assessments")
            .insert(data)
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"Assessment save error: {e}"
        )

        return False


def get_patients(search=""):

    try:

        query = (
            supabase
            .table("patients")
            .select("*")
            .eq("user_id", USER_ID)
        )

        if search.strip():

            search_value = (
                search.strip()
            )

            query = query.or_(
                f"patient_id.ilike.%{search_value}%,"
                f"patient_name.ilike.%{search_value}%,"
                f"phone.ilike.%{search_value}%"
            )

        response = query.execute()

        data = response.data or []

        return pd.DataFrame(data)

    except Exception as e:

        st.error(
            f"Patient history error: {e}"
        )

        return pd.DataFrame()


def get_patient(patient_id):

    try:

        response = (
            supabase
            .table("patients")
            .select("*")
            .eq("patient_id", patient_id)
            .eq("user_id", USER_ID)
            .execute()
        )

        return response.data or []

    except Exception as e:

        st.error(
            f"Patient details error: {e}"
        )

        return []


def get_history(patient_id):

    try:

        response = (
            supabase
            .table("assessments")
            .select("*")
            .eq("patient_id", patient_id)
            .eq("user_id", USER_ID)
            .order(
                "assessment_date",
                desc=True
            )
            .execute()
        )

        data = response.data or []

        if not data:

            return pd.DataFrame()

        df = pd.DataFrame(data)

        df["Date"] = pd.to_datetime(
            df["assessment_date"]
        )

        return df

    except Exception as e:

        st.error(
            f"Assessment history error: {e}"
        )

        return pd.DataFrame()


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

    st.html("""
    <div class="hero">

        <div class="hero-label">
            YOUR HEALTH, OUR PRIORITY
        </div>

        <div class="hero-title">
            AI-Based Health<br>
            Risk Prediction System
        </div>

        <div class="hero-text">
            Machine Learning Based Health Risk
            Assessment & Awareness Platform
        </div>

    </div>
    """)


    # ========================================================
    # FEATURE CARDS
    # ========================================================

    f1, f2, f3 = st.columns(3)

    with f1:

        st.html("""
        <div class="feature-card">

            <h3>
                🔎 Early Risk Detection
            </h3>

            <p>
                Identify potential health risks
                using machine-learning based
                assessment.
            </p>

        </div>
        """)


    with f2:

        st.html("""
        <div class="feature-card">

            <h3>
                📊 Data Driven Insights
            </h3>

            <p>
                Analyse health and lifestyle
                information to understand
                possible risk levels.
            </p>

        </div>
        """)


    with f3:

        st.html("""
        <div class="feature-card">

            <h3>
                🌱 A Healthier Tomorrow
            </h3>

            <p>
                Use awareness and data-driven
                insights to encourage healthier
                lifestyle choices.
            </p>

        </div>
        """)


    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.html("""
    <div class="disclaimer">

        ⚠️ This system is for academic,
        educational and health-awareness
        purposes only.

        It is not a medical diagnosis.

    </div>
    """)


    # ========================================================
    # PATIENT INFORMATION
    # ========================================================

    st.html("""
    <div class="section-header">

        <h2>
            👤 Patient Information
        </h2>

    </div>
    """)


    col1, col2 = st.columns(2)

    with col1:

        patient_name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name"
        )

    with col2:

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter phone number"
        )


    email = st.text_input(
        "Email",
        value=USER_EMAIL,
        disabled=True
    )


    st.caption(
        "ℹ️ Patient ID will be automatically "
        "generated after prediction."
    )


    # ========================================================
    # HEALTH INFORMATION
    # ========================================================

    st.html("""
    <div class="section-header">

        <h2>
            🩺 Health & Lifestyle Information
        </h2>

    </div>
    """)


    c1, c2, c3 = st.columns(3)


    with c1:

        age = st.number_input(
            "Age (years)",
            min_value=18,
            max_value=100,
            value=30
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


    with c2:

        blood_pressure = st.number_input(
            "Systolic Blood Pressure (mmHg)",
            min_value=70,
            max_value=220,
            value=120
        )


        glucose = st.number_input(
            "Glucose Level (mg/dL)",
            min_value=50,
            max_value=300,
            value=100
        )


        cholesterol = st.number_input(
            "Cholesterol Level (mg/dL)",
            min_value=80,
            max_value=400,
            value=180
        )


    with c3:

        physical_activity = st.slider(
            "Physical Activity (hours/week)",
            min_value=0,
            max_value=20,
            value=3
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

    st.write("")

    _, middle, _ = st.columns(
        [1, 2, 1]
    )


    with middle:

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

        if not patient_name.strip():

            st.error(
                "Please enter the patient name."
            )

            st.stop()


        # ----------------------------------------------------
        # PATIENT ID
        # ----------------------------------------------------

        patient_id = generate_patient_id()


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
        # MODEL INPUT
        # ----------------------------------------------------

        input_data = pd.DataFrame(
            [{
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

            }]
        )


        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        try:

            input_scaled = (
                scaler.transform(
                    input_data
                )
            )


            prediction = (
                model.predict(
                    input_scaled
                )[0]
            )


            if hasattr(
                model,
                "predict_proba"
            ):

                probability = (
                    model
                    .predict_proba(
                        input_scaled
                    )[0][1]
                )

            else:

                probability = float(
                    prediction
                )


            percentage = (
                probability * 100
            )


        except Exception as e:

            st.error(
                "Prediction failed."
            )

            st.exception(e)

            st.stop()


        # ----------------------------------------------------
        # RISK CATEGORY
        # ----------------------------------------------------

        if percentage < 10:

            category = "LOW RISK"

            message = (
                "Your estimated risk level "
                "is relatively low."
            )


        elif percentage < 20:

            category = "MEDIUM RISK"

            message = (
                "Your estimated risk level "
                "is moderate. Maintaining "
                "a healthy lifestyle is recommended."
            )


        else:

            category = "HIGH RISK"

            message = (
                "Your estimated risk level "
                "is relatively high. Consider "
                "discussing your health parameters "
                "with a qualified healthcare professional."
            )


        # ====================================================
        # SAVE PATIENT
        # ====================================================

        patient_saved = save_patient(
            patient_id,
            patient_name.strip(),
            phone.strip(),
            USER_EMAIL
        )


        if not patient_saved:

            st.stop()


        # ====================================================
        # SAVE ASSESSMENT
        # ====================================================

        assessment_saved = save_assessment(
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


        # ====================================================
        # RESULT
        # ====================================================

        st.divider()

        st.html("""
        <div class="section-header">

            <h2>
                📊 Prediction Result
            </h2>

        </div>
        """)


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
                "Patient ID",
                patient_id
            )


        # ----------------------------------------------------
        # RESULT STATUS
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
            f"**Assessment:** {message}"
        )


        # ----------------------------------------------------
        # SAVE STATUS
        # ----------------------------------------------------

        if assessment_saved:

            st.success(
                "✅ Assessment saved successfully!"
            )

            st.info(
                f"Your Patient ID is **{patient_id}**"
            )


        # ====================================================
        # HEALTH INSIGHTS
        # ====================================================

        st.divider()

        st.html("""
        <div class="section-header">

            <h2>
                💡 Health Insights
            </h2>

        </div>
        """)


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
                    "Systolic blood pressure "
                    "is elevated and may require "
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
# PATIENT HISTORY
# ============================================================

else:


    st.html("""
    <div class="section-header">

        <h2>
            📋 Patient History
        </h2>

    </div>
    """)


    st.write(
        "View your previous health risk assessments."
    )


    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(
        "🔎 Search Patient",
        placeholder="Patient ID, name or phone"
    )


    patients = get_patients(
        search
    )


    if patients.empty:

        st.info(
            "No patient records found."
        )


    else:


        # ----------------------------------------------------
        # PATIENT SELECT
        # ----------------------------------------------------

        patient_options = (
            patients["patient_id"]
            .astype(str)

            + " — "

            + patients["patient_name"]
            .astype(str)
        ).tolist()


        selected = st.selectbox(
            "Select Patient",
            patient_options
        )


        selected_id = (
            selected.split(
                " — "
            )[0]
        )


        # ----------------------------------------------------
        # PATIENT DATA
        # ----------------------------------------------------

        patient_data = get_patient(
            selected_id
        )


        history = get_history(
            selected_id
        )


        # ====================================================
        # PATIENT DETAILS
        # ====================================================

        if patient_data:

            person = patient_data[0]


            st.html("""
            <div class="history-card">
            </div>
            """)


            h1, h2, h3 = st.columns(3)


            with h1:

                st.metric(
                    "Patient ID",
                    person.get(
                        "patient_id",
                        "-"
                    )
                )


            with h2:

                st.metric(
                    "Name",
                    person.get(
                        "patient_name",
                        "-"
                    )
                )


            with h3:

                st.metric(
                    "Phone",
                    person.get(
                        "phone",
                        "-"
                    )
                )


        # ====================================================
        # ASSESSMENT HISTORY
        # ====================================================

        if not history.empty:


            st.divider()


            # ------------------------------------------------
            # GRAPH
            # ------------------------------------------------

            st.subheader(
                "📈 Risk History"
            )


            chart_data = history.copy()


            chart_data = (
                chart_data
                .sort_values("Date")
            )


            st.line_chart(
                chart_data.set_index(
                    "Date"
                )[
                    "risk_probability"
                ]
            )


            # ------------------------------------------------
            # TABLE
            # ------------------------------------------------

            st.subheader(
                "🗂️ Previous Assessments"
            )


            display_history = history[
                [
                    "Date",
                    "risk_probability",
                    "risk_category"
                ]
            ].copy()


            display_history["Risk"] = (
                display_history[
                    "risk_probability"
                ].apply(
                    lambda x:
                    f"{float(x):.2f}%"
                )
            )


            display_history = (
                display_history[
                    [
                        "Date",
                        "Risk",
                        "risk_category"
                    ]
                ]
                .rename(
                    columns={
                        "risk_category":
                            "Category"
                    }
                )
            )


            st.dataframe(
                display_history,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # ASSESSMENT DETAILS
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
                    f"{detail['bmi']}"
                )

                st.write(
                    f"**Blood Pressure:** "
                    f"{detail['blood_pressure']} mmHg"
                )

                st.write(
                    f"**Glucose:** "
                    f"{detail['glucose']} mg/dL"
                )


            with d2:

                st.write(
                    f"**Cholesterol:** "
                    f"{detail['cholesterol']} mg/dL"
                )

                st.write(
                    f"**Physical Activity:** "
                    f"{detail['physical_activity']} hrs/week"
                )

                st.write(
                    f"**Smoking:** "
                    f"{detail['smoking']}"
                )


            with d3:

                st.write(
                    f"**Family History:** "
                    f"{detail['family_history']}"
                )

                st.write(
                    f"**Risk:** "
                    f"{float(detail['risk_probability']):.2f}%"
                )

                st.write(
                    f"**Category:** "
                    f"{detail['risk_category']}"
                )


        else:

            st.info(
                "No assessment history available."
            )


# ============================================================
# FINAL DISCLAIMER
# ============================================================

st.divider()

st.html("""
<div class="disclaimer">

    ℹ️ <b>Disclaimer:</b>

    This tool provides an AI-based health risk
    assessment for educational and awareness
    purposes only.

    It is not a substitute for professional
    medical advice, diagnosis, or treatment.

</div>
""")
