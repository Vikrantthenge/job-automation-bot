# Job Application Bot (LinkedIn + Indeed)

This repository contains a Streamlit app that automates applications to LinkedIn and Indeed jobs listed in a Google Sheet.

## Files
- `streamlit_app.py` - Main Streamlit application that reads jobs from Google Sheets and runs Selenium automation.
- `requirements.txt` - Python dependencies.
- `.gitignore` - Ignores sensitive files and cache.
- `sample_jobs.csv` - Example CSV format for the Google Sheet (you can import this to create the Sheet).

## Setup (Local)
1. Clone or download this repo.
2. Create a Google service account and download `gspread-creds.json`. Place it in the repo folder (DO NOT commit it to GitHub).
3. Share your Google Sheet with the service account's `client_email` and ensure the sheet header is exactly:
   `Platform | Job URL | Status | Applied Date | Notes`
4. Update `SHEET_URL` inside `streamlit_app.py` with your sheet URL (already set if you gave it).
5. Install dependencies:
```bash
pip install -r requirements.txt
```
6. Run the app:
```bash
streamlit run streamlit_app.py
```
7. Provide your LinkedIn and Indeed passwords in the UI and click **Start Applying**. The browser will open visibly so you can watch the bot.

## Security
- **Do not** push `gspread-creds.json` to GitHub. Add it to `.gitignore`.
- For Streamlit Cloud / deployment, use Streamlit secrets instead of committing credentials.

## Notes
- The bot attempts easy-apply flows and will mark rows as `Applied` or `Manual/Failed` in the sheet.
- Sites may show CAPTCHAs or require manual steps; the app will pause if needed.
