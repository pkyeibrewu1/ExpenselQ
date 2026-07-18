# ExpenseIQ

ExpenseIQ is a functional Streamlit-based personal finance app built as a practical MVP for managing uploaded bank statements. It focuses on the core user experience of signing up, logging in, uploading files, and organizing statement records in a simple dashboard.

## What the project currently includes
- A landing page and onboarding flow
- User sign-up and login experience
- A local SQLite database for storing users and statement metadata
- A statement upload workflow for PDF files from selected banks
- A statement history view with the ability to delete uploaded records
- Local file storage for uploaded documents in the project data folder

## What it does not yet include
- No AI-powered financial analysis
- No automatic transaction parsing from PDF statements
- No forecasting or scenario-planning features
- No live bank API integration

## Tech stack
- Python
- Streamlit
- SQLite

## How to run
1. Install dependencies:
   pip install -r requirements.txt
2. Start the app:
   streamlit run main.py


