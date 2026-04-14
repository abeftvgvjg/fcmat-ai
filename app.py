import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
import hashlib
import matplotlib.pyplot as plt
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
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state["user"] = None

# =========================
# AI (DEMO)
# =========================
def ai_brain(prompt):
    return f"""
AI Engineering Analysis:

{prompt}

- Optimize mix design
- Reduce water-cement ratio
- Improve durability
- Apply ML regression

(Demo Mode)
"""

# =========================
# TITLE
# =========================
st.title("🏭 FCMat AI — Full Engineering Platform")

menu = st.sidebar.radio("Menu", ["Login", "Register", "Dashboard", "Optimizer", "Analytics"])

# =========================
# REGISTER
# =========================
if menu == "Register":
    st.subheader("Create Account")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        c.execute("INSERT INTO users VALUES (?,?)", (u, hash_password(p)))
        conn.commit()
        st.success("Account created!")

# =========================
# LOGIN
# =========================
if menu == "Login":
    st.subheader("Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
        if c.fetchone():
            st.session_state["user"] = u
            st.success("Login successful")
        else:
            st.error("Wrong credentials")

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    if not st.session_state["user"]:
        st.warning("Login required")
        st.stop()

    st.success(f"Welcome {st.session_state['user']} 🚀")

    cement = st.slider("Cement", 200, 550, 350)
    water = st.slider("Water", 100, 300, 180)
    age = st.slider("Age", 7, 90, 28)
    fly_ash = st.slider("Fly Ash", 0, 120, 30)
    silica_fume = st.slider("Silica Fume", 0, 40, 10)

    idea = st.text_area("Research Idea")

    if st.button("Run Simulation"):

        # AI OUTPUT
        st.subheader("🧠 AI Output")
        st.write(ai_brain(idea))

        # =========================
        # REALISTIC DATASET
        # =========================
        df = pd.DataFrame({
            "cement": np.random.randint(200, 550, 500),
            "water": np.random.randint(100, 300, 500),
            "age": np.random.choice([7, 14, 28, 56, 90], 500),
            "fly_ash": np.random.randint(0, 120, 500),
            "silica_fume": np.random.randint(0, 40, 500)
        })

        df["strength"] = (
            (0.6 * df["cement"]) / (df["water"] + 1)
            + (0.3 * df["age"])
            + (0.4 * df["fly_ash"])
            + (1.0 * df["silica_fume"])
            + np.random.normal(0, 2, 500)
        )

        X = df.drop("strength", axis=1)
        y = df["strength"]

        model = RandomForestRegressor(
            n_estimators=400,
            max_depth=15,
            random_state=42
        )
        model.fit(X, y)

        # prediction
        inp = np.array([[cement, water, age, fly_ash, silica_fume]])
        pred = model.predict(inp)[0]

        st.subheader("📊 Prediction Result")
        st.success(f"Concrete Strength = {pred:.2f}")

        if pred > 40:
            st.info("High-strength concrete")
        elif pred > 25:
            st.warning("Medium strength concrete")
        else:
            st.error("Low strength — optimize mix")

        # =========================
        # FIXED FEATURE IMPORTANCE GRAPH
        # =========================
        st.subheader("📊 Feature Importance (Corrected)")

        importance = model.feature_importances_
        features = X.columns

        fig, ax = plt.subplots()
        ax.bar(features, importance, color="skyblue")
        ax.set_ylabel("Importance")
        ax.set_title("Feature Impact on Strength")

        st.pyplot(fig)

        # SAVE
        c.execute("INSERT INTO projects VALUES (NULL,?,?,?)",
                  (st.session_state["user"], idea, str(pred)))
        conn.commit()

# =========================
# OPTIMIZER
# =========================
if menu == "Optimizer":

    st.subheader("🔥 Auto Mix Optimizer")

    best = 0
    best_mix = None

    for i in range(400):

        cement = np.random.randint(300, 550)
        water = np.random.randint(100, 250)
        age = np.random.choice([28, 56, 90])
        fly_ash = np.random.randint(20, 120)
        silica_fume = np.random.randint(5, 40)

        strength = (
            (0.6 * cement) / (water + 1)
            + (0.3 * age)
            + (0.4 * fly_ash)
            + (1.0 * silica_fume)
        )

        if strength > best:
            best = strength
            best_mix = (cement, water, age, fly_ash, silica_fume)

    st.success(f"Best Strength: {best:.2f}")

    st.write({
        "cement": best_mix[0],
        "water": best_mix[1],
        "age": best_mix[2],
        "fly_ash": best_mix[3],
        "silica_fume": best_mix[4]
    })

# =========================
# ANALYTICS
# =========================
if menu == "Analytics":

    if not st.session_state["user"]:
        st.warning("Login required")
        st.stop()

    c.execute("SELECT idea FROM projects WHERE username=?", (st.session_state["user"],))
    data = c.fetchall()

    st.metric("Total Projects", len(data))

    lengths = [len(i[0]) for i in data] if data else [0]
    st.line_chart(lengths)