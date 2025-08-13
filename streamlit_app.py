import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = json.loads(st.secrets["gspread_creds_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Authorize gspread client
gc = gspread.authorize(creds)

# Open your Google Sheet by URL
sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1HxbsyThNqCB4TcUS27J-LIaqQBTEkuJsFOaPU2KNAm8/edit?gid=0#gid=0").sheet1
