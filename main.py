import streamlit as st
import sqlite3
import os
import datetime

# Page configuration
st.set_page_config(
    page_title="ExpenseIQ",
    page_icon="💸",
    layout="centered"
)

# Core Folders Setup
UPLOAD_BASE_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)
DB_PATH = os.path.join("data", "expenseiq.db")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # 2. Statements Table (Metadata)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bank TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            upload_datetime TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# Start up Database Checks
init_db()

# --- DATABASE LOGIC HELPER FUNCTIONS ---
def add_user(first_name, last_name, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Return both the unique User ID and their Name
    cursor.execute("SELECT id, first_name FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user  

def save_statement_metadata(user_id, bank, orig_name, stored_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO statements (user_id, bank, original_filename, stored_filename, upload_datetime, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, bank, orig_name, stored_name, now_str, "Uploaded"))
    conn.commit()
    conn.close()

def get_user_statements(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT statement_id, bank, original_filename, upload_datetime, status, stored_filename 
        FROM statements WHERE user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_statement_from_db(statement_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statements WHERE statement_id = ?", (statement_id,))
    conn.commit()
    conn.close()


# --- STREAMLIT CONTROL STATES ---
if "page" not in st.session_state:
    st.session_state.page = "landing"  
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def navigate_to(page_name):
    st.session_state.page = page_name

# --- SCREEN CONTROLLER ---

# SCREEN A: Landing Page
if st.session_state.page == "landing":
    st.title("💸 ExpenselQ")
    st.subheader("No dollar left unaccounted.")
    st.write("Your finances, finally made simple. Track where your money goes and get smart suggestions.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🚀 Get Started", on_click=navigate_to, args=("signup",), type="primary", use_container_width=True)
    with col2:
        st.button("🔓 Login", on_click=navigate_to, args=("login",), type="primary", use_container_width=True)
    
    st.divider()
    st.subheader("Why ExpenseIQ?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📊\n**Automatic insights**")
        st.caption("See where your money goes with clear, real-time breakdowns.")
    with c2:
        st.markdown("### 🏷️\n**Smart categories**")
        st.caption("Expenses sort themselves so you spend less time on data entry.")
    with c3:
        st.markdown("### 🎯\n**Budget goals**")
        st.caption("Set targets and get gentle nudges before you overspend.")


# SCREEN B: Sign Up Screen
elif st.session_state.page == "signup":
    st.title("✨ Join the ExpenseIQ Family")
    st.subheader("Create your profile below")
    
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up", type="primary", use_container_width=True):
        if not first_name or not last_name or not email or not password:
            st.warning("⚠️ Please fill in all required fields.")
        elif not first_name.isalpha() or not last_name.isalpha():
            st.error("⚠️ Names can only contain letters.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match.")
        else:
            if add_user(first_name, last_name, email, password):
                st.success(f"🎉 Welcome {first_name}! Proceed to log in.")
                st.button("Proceed to Login", on_click=navigate_to, args=("login",))
            else:
                st.error("⚠️ An account with this email already exists.")
    st.button("⬅️ Back to Home", on_click=navigate_to, args=("landing",))


# SCREEN C: Login Screen
elif st.session_state.page == "login":
    st.title("🔓 Login to ExpenseIQ")
    login_email = st.text_input("Email Address")
    login_password = st.text_input("Password", type="password")
    
    if st.button("Sign In", type="primary", use_container_width=True):
        user_found = verify_user(login_email, login_password)
        if user_found:
            st.session_state.user_id = user_found[0]
            st.session_state.user_name = user_found[1]
            st.success(f"🔐 Welcome back, {st.session_state.user_name}!")
            st.button("Go to Statements Upload", on_click=navigate_to, args=("statements",))
        else:
            st.error("❌ Invalid credentials.")
    st.button("⬅️ Back to Home", on_click=navigate_to, args=("landing",))


# SCREEN D: Real-Time Statements Processing & Metadata Display
elif st.session_state.page == "statements":
    st.title(f"📁 Welcome to ExpenseIQ, {st.session_state.user_name}!")
    st.subheader("Let's get started by uploading your financial data.")
    
    st.divider()
    
    # Flow Step 1: Selection Dropdown
    st.markdown("#### 🏦 Step 1: Select Your Bank")
    bank_options = {
        "Bank of America": "bofa",
        "Chase": "chase",
        "Wells Fargo": "wells_fargo",
        "Chime": "chime"
    }
    selected_bank_label = st.selectbox("Which bank issued your statement?", options=list(bank_options.keys()))
    chosen_bank_id = bank_options[selected_bank_label]
    
    # Flow Step 2: PDF Drop-zone
    st.markdown("#### 📂 Step 2: Statement upload feature (Prototype)")
    uploaded_file = st.file_uploader(f"Upload a PDF bank statement from {selected_bank_label}.", type=["pdf"])
    
    # Error checking for file structure
    if uploaded_file is not None:
        if not uploaded_file.name.lower().endswith('.pdf'):
            st.error("❌ File type mismatch! The attached document must be an actual PDF file format.")
        else:
            st.success(f"📄 Validated **{uploaded_file.name}** successfully.")
            
            # Action Execution: Process File & Build entries
            if st.button(f"💾 Save {selected_bank_label} Statement", type="primary", use_container_width=True):
                # Ensure custom folder paths exist: data/uploads/{bank_id}/
                bank_folder = os.path.join(UPLOAD_BASE_DIR, chosen_bank_id)
                os.makedirs(bank_folder, exist_ok=True)
                
                # Make a unique file name using timestamp to prevent name overlaps
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                stored_filename = f"{timestamp}_{uploaded_file.name}"
                full_save_path = os.path.join(bank_folder, stored_filename)
                
                # Save data directly down into local directory storage structures
                with open(full_save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Write matching profile metadata safely to SQLite
                save_statement_metadata(
                    user_id=st.session_state.user_id,
                    bank=selected_bank_label,
                    orig_name=uploaded_file.name,
                    stored_name=stored_filename
                )
                st.success(f"✅ Securely stored and cataloged file entry!")
                st.rerun()

    st.divider()
    
    # Flow Step 4: Display Dynamic List & Action Logs
    st.markdown("### 📋 Uploaded Statements Logs")
    user_records = get_user_statements(st.session_state.user_id)
    
    if not user_records:
        st.info("No statements logged yet. Complete steps 1 & 2 above to view analytics history.")
    else:
        # Create a dynamic interactive table layout using columns loops
        head1, head2, head3, head4, head5 = st.columns([2, 3, 3, 2, 2])
        with head1: st.markdown("**Bank**")
        with head2: st.markdown("**File Name**")
        with head3: st.markdown("**Uploaded Date**")
        with head4: st.markdown("**Status**")
        with head5: st.markdown("**Action**")
        
        st.markdown("---")
        
        for row in user_records:
            stmt_id, bank_name, orig_file, upload_time, status, stored_file = row
            
            c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 2, 2])
            with c1: st.write(bank_name)
            with c2: st.write(orig_file)
            with c3: st.write(upload_time)
            with c4: st.success(status) if status == "Uploaded" else st.write(status)
            with c5:
                # Assign a unique button key to each database row 
                if st.button("🗑️ Delete", key=f"del_{stmt_id}", use_container_width=True):
                    # 1. Purge physical local disk document
                    target_bank_id = bank_options.get(bank_name, "unknown")
                    file_disk_path = os.path.join(UPLOAD_BASE_DIR, target_bank_id, stored_file)
                    if os.path.exists(file_disk_path):
                        os.remove(file_disk_path)
                    
                    # 2. Erase SQLite metadata logs
                    delete_statement_from_db(stmt_id)
                    st.toast(f"Purged {orig_file} safely!")
                    st.rerun()

    st.markdown("###")
    if st.button("🚪 Log Out", type="secondary"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        navigate_to("landing")
    
st.write("##") # Explicit spacing buffer
st.divider()

foot_col1, foot_col2, foot_col3 = st.columns([1, 2, 1])
with foot_col2:
    st.caption("© 2026 ExpenseIQ — All Rights Reserved")
    st.caption("pamelakyei15@gmail.com")