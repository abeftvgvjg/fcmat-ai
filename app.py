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
# AI DEMO
# =========================
def ai_brain(prompt):
    return f"""
AI Research Analysis:

{prompt}

- Optimize concrete mix design
- Use ML regression modeling
- Improve sustainability
- Structural engineering application

(Demo Mode)
"""

# =========================
# HEADER
# =========================
st.title("🏭 FCMat AI — Advanced Concrete Intelligence System")

menu = st.sidebar.radio("Menu", ["Login", "Register", "Dashboard", "Analytics", "Optimizer"])

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

    cement = st.slider("Cement", 200, 500, 350)
    water = st.slider("Water", 100, 300, 180)
    age = st.slider("Age", 7, 90, 28)
    fly_ash = st.slider("Fly Ash", 0, 100, 30)
    silica_fume = st.slider("Silica Fume", 0, 30, 10)

    idea = st.text_area("Research Idea")

    if st.button("Run AI + ML"):

        # AI
        st.subheader("🧠 AI Output")
        st.write(ai_brain(idea))

        # DATASET
        df = pd.DataFrame({
            "cement": np.random.uniform(200, 500, 400),
            "water": np.random.uniform(120, 280, 400),
            "age": np.random.choice([7, 14, 28, 56, 90], 400),
            "fly_ash": np.random.uniform(0, 100, 400),
            "silica_fume": np.random.uniform(0, 30, 400)
        })

        df["strength"] = (
            (0.55 * df["cement"]) / (df["water"] + 1)
            + 0.25 * df["age"]
            + 0.3 * df["fly_ash"]
            + 0.9 * df["silica_fume"]
        )

        X = df.drop("strength", axis=1)
        y = df["strength"]

        model = RandomForestRegressor(n_estimators=300, max_depth=12)
        model.fit(X, y)

        # prediction
        inp = np.array([[cement, water, age, fly_ash, silica_fume]])
        pred = model.predict(inp)[0]

        st.subheader("📊 Prediction")
        st.success(f"Strength = {pred:.2f}")

        # insight
        if pred > 40:
            st.info("High strength concrete (high-rise structures)")
        elif pred > 25:
            st.warning("Medium strength concrete")
        else:
            st.error("Low strength — optimize mix")

        # SAVE
        c.execute("INSERT INTO projects VALUES (NULL,?,?,?)",
                  (st.session_state["user"], idea, str(pred)))
        conn.commit()

        # GRAPH
        st.subheader("📊 Feature Impact")
        fig, ax = plt.subplots()
        ax.bar(X.columns, model.feature_importances_)
        st.pyplot(fig)

        st.dataframe(df.head())

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

# =========================
# OPTIMIZER (NEW FEATURE)
# =========================
if menu == "Optimizer":

    st.subheader("🔥 Auto Concrete Optimizer")

    st.write("Finding best mix automatically...")

    best_strength = 0
    best_mix = None

    for i in range(200):

        cement = np.random.uniform(300, 500)
        water = np.random.uniform(120, 250)
        age = np.random.choice([28, 56, 90])
        fly_ash = np.random.uniform(20, 100)
        silica_fume = np.random.uniform(5, 30)

        strength = (
            (0.55 * cement) / (water + 1)
            + 0.25 * age
            + 0.3 * fly_ash
            + 0.9 * silica_fume
        )

        if strength > best_strength:
            best_strength = strength
            best_mix = (cement, water, age, fly_ash, silica_fume)

    st.success(f"Best Strength Found: {best_strength:.2f}")

    st.write("Best Mix:")
    st.write({
        "cement": best_mix[0],
        "water": best_mix[1],
        "age": best_mix[2],
        "fly_ash": best_mix[3],
        "silica_fume": best_mix[4],
    })