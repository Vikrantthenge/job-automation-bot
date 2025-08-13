# streamlit_app.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from datetime import datetime
import time, random, os

# ----------------- CONFIG -----------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HxbsyThNqCB4TcUS27J-LIaqQBTEkuJsFOaPU2KNAm8/edit"
# Set absolute path to resume if you want upload attempt, otherwise leave None
RESUME_PATH = None  # e.g. r"C:\Users\india\Documents\Resume.pdf"

# Hard-coded emails (as requested)
LINKEDIN_EMAIL = "vikrantthenge@outlook.com"
INDEED_EMAIL = "vikrantthenge@outlook.com"

# ----------------- GOOGLE SHEETS AUTH -----------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gspread-creds.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).sheet1  # assumes header: Platform | Job URL | Status | Applied Date | Notes

# ----------------- STREAMLIT UI -----------------
st.set_page_config(page_title="Job Apply Bot", layout="wide")
st.title("💼 Job Application Bot (LinkedIn + Indeed)")

st.markdown('''
**Instructions**
1. Make sure `gspread-creds.json` is in this folder and the service account has Editor access to the Google Sheet.
2. Sheet header must be exactly: `Platform | Job URL | Status | Applied Date | Notes`.
3. Add job links in the sheet (Platform = LinkedIn or Indeed), leave Status blank for pending.
4. Provide your passwords below and click **Start Applying** — browser will open so you can watch.
''')

linkedin_password = st.text_input("LinkedIn password", type="password")
indeed_password = st.text_input("Indeed password (optional)", type="password")
humanize = st.checkbox("Add random human-like delays (recommended)", value=True)
resume_file = st.file_uploader("Optionally upload a resume (PDF) to use during apply", type=["pdf", "doc", "docx"])

if resume_file:
    # save to temp file
    temp_path = os.path.join(os.getcwd(), f"temp_resume_{int(time.time())}_{resume_file.name}")
    with open(temp_path, "wb") as f:
        f.write(resume_file.getbuffer())
    RESUME_PATH = temp_path
    st.success("Resume uploaded and will be used when file inputs are found during apply.")

start = st.button("▶️ Start Applying (opens visible browser)")

# ----------------- HELPERS -----------------
def human_sleep(base=2.0, jitter=2.0):
    if humanize:
        t = base + random.random()*jitter
        time.sleep(t)
    else:
        time.sleep(base)

def safe_click(driver, elm):
    try:
        elm.click()
        return True
    except (ElementClickInterceptedException, Exception):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elm)
            time.sleep(0.5)
            elm.click()
            return True
        except Exception:
            return False

def update_sheet_row(row_idx, status, notes=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet.update_cell(row_idx, 3, status)       # Status col (C)
        sheet.update_cell(row_idx, 4, now)          # Applied Date col (D)
        sheet.update_cell(row_idx, 5, notes)        # Notes col (E)
    except Exception as e:
        st.warning(f"Could not update sheet row {row_idx}: {e}")

# ----------------- SELENIUM / LOGIN -----------------
def init_driver(visible=True):
    options = webdriver.ChromeOptions()
    if not visible:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 900)
    return driver

def login_linkedin(driver, password):
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
        st.info("Logged into LinkedIn")
        human_sleep(1,1)
    except Exception as e:
        st.warning("LinkedIn login might require manual action (MFA). Please complete in the browser if prompted.")
        st.write(str(e))
        input("After completing any manual steps (MFA), press Enter here to continue...")

def login_indeed(driver, password):
    if not password:
        st.info("Skipping Indeed login (no password provided).")
        return
    driver.get("https://secure.indeed.com/account/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-email-input"))).send_keys(INDEED_EMAIL)
        driver.find_element(By.ID, "login-password-input").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        human_sleep(2,1)
        st.info("Logged into Indeed")
    except Exception as e:
        st.warning("Indeed login may need manual interaction. Please complete it in the browser if prompted.")
        st.write(str(e))
        input("After completing any manual steps (MFA), press Enter here to continue...")

# ----------------- APPLY FLOWS -----------------
def linkedin_apply(driver, url, row_idx):
    notes = ""
    try:
        driver.get(url)
        human_sleep(2,2)
        try:
            easy_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'jobs-apply-button') or contains(., 'Easy Apply')]"))
            )
            safe_click(driver, easy_btn)
            human_sleep(1,2)
        except TimeoutException:
            return False, "Easy Apply not found or blocked"

        for step in range(7):
            human_sleep(0.8,1.2)
            try:
                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                if RESUME_PATH:
                    file_input.send_keys(RESUME_PATH)
                    human_sleep(1,1)
                    notes += "Uploaded resume; "
            except NoSuchElementException:
                pass

            try:
                submit_btn = driver.find_element(By.XPATH, "//button[@aria-label='Submit application' or contains(., 'Submit application') or contains(@class,'artdeco-button--primary') and contains(., 'Submit')]")
                if submit_btn.is_enabled():
                    safe_click(driver, submit_btn)
                    human_sleep(1,1)
                    return True, "Applied"
            except NoSuchElementException:
                pass

            next_btn = None
            for xp in ["//button[contains(., 'Next')]", "//button[contains(., 'Review')]", "//button[contains(., 'Continue')]", "//button[contains(., 'Save and Continue')]"]:
                try:
                    cand = driver.find_element(By.XPATH, xp)
                    if cand.is_enabled():
                        next_btn = cand
                        break
                except NoSuchElementException:
                    continue
            if next_btn:
                safe_click(driver, next_btn)
                continue

            break

        return False, "Partial flow - manual required: " + notes
    except Exception as e:
        return False, f"Error: {e}"

def indeed_apply(driver, url, row_idx):
    notes = ""
    try:
        driver.get(url)
        human_sleep(2,2)
        try:
            apply_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Apply Now') or contains(., 'Easily apply') or contains(., 'Apply on company site')]"))
            )
            safe_click(driver, apply_btn)
            human_sleep(1,1)
        except TimeoutException:
            return False, "No easy apply button"

        try:
            file_input = driver.find_element(By.XPATH, "//input[@type='file']")
            if RESUME_PATH:
                file_input.send_keys(RESUME_PATH)
                notes += "Uploaded resume; "
                human_sleep(1,1)
        except NoSuchElementException:
            pass

        try:
            submit = driver.find_element(By.XPATH, "//button[contains(., 'Submit') or contains(., 'Apply') or contains(., 'Finish application')]")
            if submit.is_enabled():
                safe_click(driver, submit)
                human_sleep(1,1)
                return True, "Applied"
        except NoSuchElementException:
            return False, "Partial - manual required: " + notes

        return False, "Unknown Indeed flow"
    except Exception as e:
        return False, f"Error: {e}"

# ----------------- MAIN RUN -----------------
if start:
    try:
        records = sheet.get_all_records()
    except Exception as e:
        st.error(f"Could not read sheet: {e}")
        st.stop()

    pending = [(idx, r) for idx, r in enumerate(records, start=2) if not str(r.get("Status", "")).strip().lower().startswith("applied")]
    if not pending:
        st.info("No pending jobs to apply for. Status looks clear.")
        st.stop()

    st.write(f"Found {len(pending)} pending jobs — starting automation (visible browser).")
    driver = init_driver(visible=True)
    wait = WebDriverWait(driver, 12)

    if linkedin_password:
        login_linkedin(driver, linkedin_password)
    else:
        st.warning("No LinkedIn password supplied — LinkedIn flows may fail.")
    login_indeed(driver, indeed_password)

    successes = 0
    for row_idx, row in pending:
        platform = str(row.get("Platform","")).strip().lower()
        url = str(row.get("Job URL","")).strip()
        st.write(f"Processing row {row_idx} -> {platform}  {url}")
        if not url:
            update_sheet_row(row_idx, "No URL", "Missing Job URL")
            continue

        human_sleep(1,3)

        try:
            if "linkedin" in url or platform == "linkedin":
                ok, note = linkedin_apply(driver, url, row_idx)
            elif "indeed" in url or platform == "indeed":
                ok, note = indeed_apply(driver, url, row_idx)
            else:
                ok, note = False, "Unsupported platform"

            if ok:
                successes += 1
                update_sheet_row(row_idx, "Applied", note)
                st.success(f"Row {row_idx}: Applied")
            else:
                update_sheet_row(row_idx, "Manual/Failed", note)
                st.warning(f"Row {row_idx}: Not applied -> {note}")

        except Exception as e:
            update_sheet_row(row_idx, "Error", str(e))
            st.error(f"Row {row_idx}: Exception -> {e}")

    st.write(f"Done. Applied: {successes} / {len(pending)}")
    driver.quit()
    if resume_file and os.path.exists(RESUME_PATH) and "temp_resume_" in RESUME_PATH:
        try:
            os.remove(RESUME_PATH)
        except:
            pass
