import pandas as pd
import numpy as np
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# 1. Create Dataset
# -----------------------------

np.random.seed(42)

n = 2000

age = np.random.randint(18, 81, n)

bmi = np.round(
    np.random.uniform(16, 40, n),
    1
)

blood_pressure = np.random.randint(
    90, 181, n
)

glucose = np.random.randint(
    70, 220, n
)

cholesterol = np.random.randint(
    120, 301, n
)

physical_activity = np.random.randint(
    0, 8, n
)

smoking = np.random.randint(
    0, 2, n
)

family_history = np.random.randint(
    0, 2, n
)


# -----------------------------
# 2. Generate Risk Score
# -----------------------------

risk_score = (
    0.025 * age
    + 0.08 * bmi
    + 0.025 * blood_pressure
    + 0.035 * glucose
    + 0.012 * cholesterol
    - 0.25 * physical_activity
    + 0.8 * smoking
    + 1.0 * family_history
)

threshold = np.median(risk_score)

diabetes_risk = (
    risk_score > threshold
).astype(int)


# -----------------------------
# 3. Create DataFrame
# -----------------------------

df = pd.DataFrame({

    "Age": age,

    "BMI": bmi,

    "BloodPressure": blood_pressure,

    "Glucose": glucose,

    "Cholesterol": cholesterol,

    "PhysicalActivity": physical_activity,

    "Smoking": smoking,

    "FamilyHistory": family_history,

    "DiabetesRisk": diabetes_risk
})


# -----------------------------
# 4. Prepare Data
# -----------------------------

X = df.drop(
    "DiabetesRisk",
    axis=1
)

y = df["DiabetesRisk"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# -----------------------------
# 5. Feature Scaling
# -----------------------------

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)


# -----------------------------
# 6. Train Model
# -----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(
    X_train_scaled,
    y_train
)


# -----------------------------
# 7. Evaluation
# -----------------------------

y_pred = model.predict(
    X_test_scaled
)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(
    f"Model Accuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# -----------------------------
# 8. Save Model
# -----------------------------

os.makedirs(
    "health_model",
    exist_ok=True
)


with open(
    "health_model/model.pkl",
    "wb"
) as f:

    pickle.dump(
        model,
        f
    )


with open(
    "health_model/scaler.pkl",
    "wb"
) as f:

    pickle.dump(
        scaler,
        f
    )


# -----------------------------
# 9. Save Dataset
# -----------------------------

df.to_csv(
    "health_data.csv",
    index=False
)


print("\nModel saved successfully!")

print(
    "Files created:"
)

print(
    "health_model/model.pkl"
)

print(
    "health_model/scaler.pkl"
)

print(
    "health_data.csv"
)