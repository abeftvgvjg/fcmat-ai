import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import hashlib
from sklearn.ensemble import RandomForestRegressor

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
#