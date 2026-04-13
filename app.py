# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:55:21 2026

@author: lolip
"""

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from openai import OpenAI

# =========================
# 1. DATABASE (MULTI-USER)
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
# 2. AI BRAIN (REAL)
# =========================
client = OpenAI(api_key="YOUR_API_KEY")

def ai_brain(prompt):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a civil engineering PhD research assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

# =========================
# 3. LOGIN SYSTEM
# =========================
st.set_page_config(page_title="FCMat AI SaaS", layout="wide")

st.title("🏭 FCMat AI — SaaS + PhD Platform")

menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Dashboard"])

# =========================
# REGISTER
# =========================
if menu == "Register":
    st.subheader("Create Account")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        c.execute("INSERT INTO users VALUES (?,?)", (u, p))
        conn.commit()
        st.success("Account created!")

# =========================
# LOGIN
# =========================
if menu == "Login":
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            st.session_state["user"] = username
            st.success("Login successful")
        else:
            st.error("Wrong credentials")

# =========================
# DASHBOARD (MAIN SYSTEM)
# =========================
if menu == "Dashboard":

    if "user" not in st.session_state:
        st.warning("Please login first")
        st.stop()

    st.success(f"Welcome {st.session_state['user']} 🚀")

    idea = st.text_area("Enter Research Idea")

    if st.button("Run Full AI Simulation"):

        # =========================
        # AI BRAIN
        # =========================
        st.subheader("🧠 AI Brain Result")
        ai_result = ai_brain(idea)
        st.write(ai_result)

        # =========================
        # DATASET (SYNTHETIC + ML)
        # =========================
        st.subheader("🧪 ML Simulation")

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

        error = np.mean(abs(y - pred))

        st.write("MAE:", error)

        # =========================
        # SAVE PROJECT
        # =========================
        result_text = f"AI:{ai_result[:100]} | MAE:{error}"

        c.execute(
            "INSERT INTO projects (username, idea, result) VALUES (?,?,?)",
            (st.session_state["user"], idea, result_text)
        )
        conn.commit()

        st.success("Project saved!")

        # =========================
        # OUTPUT
        # =========================
        st.subheader("📊 Dataset Preview")
        st.dataframe(df.head())