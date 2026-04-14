import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import hashlib
from sklearn.ensemble import RandomForestRegressor
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="FCMat AI SaaS", layout="wide")

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
# AI (DEMO MODE — NO OPENAI)
# =========================
def ai_brain(prompt):
    return f"""
🔬 AI Research Analysis

Idea:
{prompt}

Approach:
- Use experimental mix design
- Apply regression-based ML models
- Optimize cement-water ratio

Materials:
- Cement, water, aggregates
- Additives: fly ash, silica fume

Expected Outcome:
- Better strength prediction
- Improved sustainability

⚠ Demo Mode (No API key required)
"""

# =========================
# PDF
# =========================
def generate_pdf(text, filename="report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    return filename

# =========================
# UI
# =========================
st.title("🏭 FCMat AI — SaaS Platform")

if "user" not in st.session_state:
    st.session_state["user"] = None

menu = st.sidebar.radio("Navigation", ["Login", "Register", "Dashboard", "Analytics"])

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

    idea = st.text_area("Enter Research Idea")

    if st.button("Run AI + Simulation"):

        # AI OUTPUT
        ai_result = ai_brain(idea)
        st.subheader("🧠 AI Result")
        st.write(ai_result)

        # ML SIMULATION
        df = pd.DataFrame({
            "cement": np.random.randint(200, 500, 200),
            "water": np.random.randint(100, 300, 200),
            "age": np.random.randint(7, 90, 200)
        })

        df["strength"] = (150 / ((df["water"]/df["cement"]) * 5)) + 0.3 * df["age"]

        X = df[["cement", "water", "age"]]
        y = df["strength"]

        model = RandomForestRegressor()
        model.fit(X, y)
        pred = model.predict(X)

        error = np.mean(np.abs(y - pred))

        st.metric("Model Error", round(error, 4))

        # SAVE PROJECT
        result = f"{ai_result[:120]} | MAE {error:.4f}"

        c.execute(
            "INSERT INTO projects (username, idea, result) VALUES (?,?,?)",
            (st.session_state["user"], idea, result)
        )
        conn.commit()

        # PDF DOWNLOAD
        pdf = generate_pdf(ai_result)

        with open(pdf, "rb") as f:
            st.download_button("📄 Download Report", f, file_name="report.pdf")

        st.dataframe(df.head())

# =========================
# ANALYTICS
# =========================
if menu == "Analytics":

    if st.session_state["user"] is None:
        st.warning("Login required")
        st.stop()

    st.subheader("📊 Your Research Analytics")

    c.execute("SELECT idea FROM projects WHERE username=?", (st.session_state["user"],))
    data = c.fetchall()

    st.metric("Total Projects", len(data))

    lengths = [len(i[0]) for i in data] if data else [0]

    st.line_chart(lengths)