import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==================== GOOGLE SHEETS AUTH ====================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit Secrets (TOML)
creds_dict = json.loads(st.secrets["gspread_creds_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

# Open your Google Sheet by URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HxbsyThNqCB4TcUS27J-LIaqQBTEkuJsFOaPU2KNAm8/edit?gid=0#gid=0"  # Replace with your sheet URL
sheet = gc.open_by_url(SHEET_URL).sheet1

# ==================== STREAMLIT UI ====================
st.title("Job Application Automation Bot")
st.markdown("""
Welcome to the **Job Application Automation Bot**.  

This app automates your daily job applications on LinkedIn and Indeed.  

**Instructions:**
- Enter your LinkedIn and Indeed passwords (securely).
- Click **Start Applying** to begin automation.
- Your application status will be updated in Google Sheets automatically.
""")

# ==================== PASSWORD INPUT ====================
linkedin_password = st.text_input("LinkedIn Password", type="password")
indeed_password = st.text_input("Indeed Password", type="password")

# ==================== START BUTTON ====================
if st.button("Start Applying"):
    if not linkedin_password or not indeed_password:
        st.warning("Please enter both LinkedIn and Indeed passwords!")
    else:
        st.success("Automation started! (placeholder)")

        # ==================== EXAMPLE: READ JOBS FROM SHEET ====================
        try:
            jobs = sheet.get_all_records()
            st.write("Jobs fetched from Google Sheet:")
            st.dataframe(jobs)
        except Exception as e:
            st.error(f"Error fetching jobs from Google Sheet: {e}")

        # ==================== PLACEHOLDER FOR AUTOMATION ====================
        st.info("Automation logic for applying to jobs goes here...")
        # Here you can integrate Selenium/Playwright scripts to apply automatically.
