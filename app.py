import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import hashlib
from sklearn.ensemble import RandomForestRegressor

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="FCMat AI", layout="wide")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("fcmat.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    idea TEXT,
    result TEXT
)
""")
conn.commit()

# =========================
# SECURITY
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# LOGIN STATE
# =========================
if "user" not in st.session_state:
    st.session_state["user"] = None

# =========================
# AI TEXT ENGINE (DEMO)
# =========================
def ai_brain(prompt):
    return f"""
AI Research Analysis:

{prompt}

Suggested Approach:
- Optimize concrete mix design
- Use machine learning regression
- Improve sustainability
- Study water-cement ratio effects

(Demo Mode)
"""

# =========================
# UI HEADER
# =========================
st.title("🏭 FCMat AI — Smart Concrete & Materials Platform")
st.write("AI + ML-based Civil Engineering Research System")

menu = st.sidebar.radio("Menu", ["Login", "Register", "Dashboard", "Analytics"])

# =========================
# REGISTER
# =========================
if menu == "Register":
    st.subheader("Create Account")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if u and p:
            c.execute("INSERT INTO users VALUES (?,?)", (u, hash_password(p)))
            conn.commit()
            st.success("Account created!")
        else:
            st.warning("Fill all fields")

# =========================
# LOGIN
# =========================
if menu == "Login":
    st.subheader("Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
        user = c.fetchone()

        if user:
            st.session_state["user"] = u
            st.success("Login successful")
        else:
            st.error("Wrong credentials")

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    if st.session_state["user"] is None:
        st.warning("Please login first")
        st.stop()

    st.success(f"Welcome {st.session_state['user']} 🚀")

    st.subheader("🧪 Concrete Mix Input")

    cement = st.slider("Cement (kg/m³)", 200, 500, 350)
    water = st.slider("Water (kg/m³)", 100, 280, 180)
    age = st.slider("Curing Age (days)", 7, 90, 28)
    fly_ash = st.slider("Fly Ash", 0, 100, 30)
    silica_fume = st.slider("Silica Fume", 0, 30, 10)

    idea = st.text_area("Research Idea")

    if st.button("Run AI + ML Simulation"):

        # =========================
        # AI OUTPUT
        # =========================
        ai_result = ai_brain(idea)

        st.subheader("🧠 AI Research Output")
        st.write(ai_result)

        # =========================
        # REALISTIC DATASET
        # =========================
        df = pd.DataFrame({
            "cement": np.random.uniform(200, 500, 300),
            "water": np.random.uniform(120, 280, 300),
            "age": np.random.choice([7, 14, 28, 56, 90], 300),
            "fly_ash": np.random.uniform(0, 100, 300),
            "silica_fume": np.random.uniform(0, 30, 300)
        })

        # engineering-inspired strength formula
        df["strength"] = (
            (0.5 * df["cement"]) / (df["water"] + 1)
            + 0.2 * df["age"]
            + 0.3 * df["fly_ash"]
            + 0.8 * df["silica_fume"]
        )

        # =========================
        # ML MODEL
        # =========================
        X = df[["cement", "water", "age", "fly_ash", "silica_fume"]]
        y = df["strength"]

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            random_state=42
        )

        model.fit(X, y)

        # prediction
        input_data = np.array([[cement, water, age, fly_ash, silica_fume]])
        pred = model.predict(input_data)[0]

        st.subheader("📊 Prediction Result")
        st.success(f"Predicted Concrete Strength: {pred:.2f}")

        # =========================
        # RESEARCH INSIGHT
        # =========================
        st.subheader("📌 Research Insight")

        if pred > 40:
            st.info("High-strength concrete suitable for high-rise structures 🏢")
        elif pred > 25:
            st.warning("Medium strength — suitable for general construction")
        else:
            st.error("Low strength — adjust mix design")

        # =========================
        # ERROR METRIC
        # =========================
        pred_train = model.predict(X)
        error = np.mean(np.abs(y - pred_train))

        st.metric("Model Error (MAE)", round(error, 4))

        # =========================
        # SAVE PROJECT
        # =========================
        result = f"Pred:{pred:.2f} | MAE:{error:.2f}"

        c.execute(
            "INSERT INTO projects (username, idea, result) VALUES (?,?,?)",
            (st.session_state["user"], idea, result)
        )
        conn.commit()

        st.success("Project saved successfully!")

        # =========================
        # DATA PREVIEW
        # =========================
        st.subheader("📊 Dataset Preview")
        st.dataframe(df.head())

# =========================
# ANALYTICS
# =========================
if menu == "Analytics":

    if st.session_state["user"] is None:
        st.warning("Login required")
        st.stop()

    st.subheader("📊 User Analytics")

    c.execute("SELECT idea FROM projects WHERE username=?", (st.session_state["user"],))
    data = c.fetchall()

    st.metric("Total Projects", len(data))

    lengths = [len(i[0]) for i in data] if data else [0]

    st.line_chart(lengths)