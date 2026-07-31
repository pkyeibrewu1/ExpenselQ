import streamlit as st
import sqlite3
import os
import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ExpenseIQ",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Folders Setup
UPLOAD_BASE_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)
DB_PATH = os.path.join("data", "expenseiq.db")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
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

init_db()

# --- DATABASE HELPER FUNCTIONS ---
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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("💸 ExpenseIQ")
    if st.session_state.user_id:
        st.success(f"👤 Logged in as **{st.session_state.user_name}**")
        st.divider()
        if st.button("📊 Dashboard & Uploads", use_container_width=True):
            navigate_to("statements")
            st.rerun()
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_name = None
            navigate_to("landing")
            st.toast("Logged out successfully!")
            st.rerun()
    else:
        st.info("Please log in or register to access features.")
        if st.button("🏠 Home", use_container_width=True):
            navigate_to("landing")
            st.rerun()
        if st.button("🔓 Login", use_container_width=True):
            navigate_to("login")
            st.rerun()
        if st.button("✨ Sign Up", use_container_width=True):
            navigate_to("signup")
            st.rerun()

# --- SCREEN CONTROLLER ---

# SCREEN A: Landing Page
if st.session_state.page == "landing":
    st.title("💸 Welcome to ExpenseIQ")
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
        st.container(border=True).markdown("### 📊\n**Automatic Insights**\nSee where your money goes with clear breakdowns.")
    with c2:
        st.container(border=True).markdown("### 🏷️\n**Smart Categories**\nExpenses sort themselves automatically.")
    with c3:
        st.container(border=True).markdown("### 🎯\n**Budget Goals**\nSet targets and avoid overspending.")


# SCREEN B: Sign Up Screen
elif st.session_state.page == "signup":
    st.title("✨ Join the ExpenseIQ Family")
    st.subheader("Create your profile below")
    
    # Form handles text inputs and form submission
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
        with col2:
            last_name = st.text_input("Last Name")
        
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
        
        if submit:
            if not first_name or not last_name or not email or not password:
                st.warning("⚠️ Please fill in all required fields.")
            elif not first_name.isalpha() or not last_name.isalpha():
                st.error("⚠️ Names can only contain letters.")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match.")
            else:
                if add_user(first_name, last_name, email, password):
                    st.session_state.signup_success = True
                    st.session_state.signed_up_user = first_name
                else:
                    st.error("⚠️ An account with this email already exists.")

    # Render post-signup actions OUTSIDE the form block
    if st.session_state.get("signup_success", False):
        st.balloons()
        st.success(f"🎉 Welcome {st.session_state.signed_up_user}! Your account has been created.")
        if st.button("Proceed to Login ➡️", type="primary", use_container_width=True):
            st.session_state.signup_success = False
            navigate_to("login")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Back to Home"):
        navigate_to("landing")
        st.rerun()


# SCREEN C: Login Screen
elif st.session_state.page == "login":
    st.title("🔓 Login to ExpenseIQ")
    
    with st.form("login_form"):
        login_email = st.text_input("Email Address")
        login_password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)
        
        if submit:
            user_found = verify_user(login_email, login_password)
            if user_found:
                st.session_state.user_id = user_found[0]
                st.session_state.user_name = user_found[1]
                st.toast(f"Welcome back, {st.session_state.user_name}!", icon="🔐")
                navigate_to("statements")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")

    st.markdown("---")
    if st.button("⬅️ Back to Home"):
        navigate_to("landing")
        st.rerun()


# SCREEN D: Dashboard & Statements Management
elif st.session_state.page == "statements":
    if not st.session_state.user_id:
        st.warning("Please log in to view your statement dashboard.")
        st.stop()

    st.title(f"📁 Dashboard & Statements — Welcome, {st.session_state.user_name}!")
    
    # Interactive Metrics Overview
    user_records = get_user_statements(st.session_state.user_id)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Uploads", len(user_records))
    unique_banks = len(set(row[1] for row in user_records)) if user_records else 0
    m2.metric("Connected Banks", unique_banks)
    m3.metric("System Status", "Active", delta="Synced")
    
    st.divider()
    
    # Interactive Statement Upload Section
    with st.expander("➕ **Upload New Bank Statement**", expanded=True):
        bank_options = {
            "Bank of America": "bofa",
            "Chase": "chase",
            "Wells Fargo": "wells_fargo",
            "Chime": "chime"
        }
        
        c1, c2 = st.columns([1, 2])
        with c1:
            selected_bank_label = st.selectbox("Select Your Bank", options=list(bank_options.keys()))
            chosen_bank_id = bank_options[selected_bank_label]
            
        with c2:
            uploaded_file = st.file_uploader(f"Upload PDF from {selected_bank_label}", type=["pdf"])
            
        if uploaded_file is not None:
            if st.button(f"💾 Save {selected_bank_label} Statement", type="primary", use_container_width=True):
                bank_folder = os.path.join(UPLOAD_BASE_DIR, chosen_bank_id)
                os.makedirs(bank_folder, exist_ok=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                stored_filename = f"{timestamp}_{uploaded_file.name}"
                full_save_path = os.path.join(bank_folder, stored_filename)
                
                with open(full_save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                save_statement_metadata(
                    user_id=st.session_state.user_id,
                    bank=selected_bank_label,
                    orig_name=uploaded_file.name,
                    stored_name=stored_filename
                )
                st.toast(f"Saved {uploaded_file.name} successfully!", icon="✅")
                st.rerun()

    st.divider()

    # Interactive Statement History & Data Table
    st.markdown("### 📋 Statement History & Analytics")
    
    if not user_records:
        st.info("No statements logged yet. Upload a PDF statement above to get started.")
    else:
        df = pd.DataFrame(user_records, columns=["ID", "Bank", "File Name", "Upload Date", "Status", "Stored File"])
        
        # Search and Filtering Controls
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search File Name", "")
        with col_filter:
            selected_banks = st.multiselect("Filter by Bank", options=df["Bank"].unique(), default=df["Bank"].unique())
        
        filtered_df = df[(df["Bank"].isin(selected_banks)) & (df["File Name"].str.contains(search_query, case=False))]
        
        tab1, tab2 = st.tabs(["📊 Interactive Data Table", "📈 Bank Analytics"])
        
        with tab1:
            st.dataframe(
                filtered_df[["Bank", "File Name", "Upload Date", "Status"]],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("#### File Operations")
            bank_options = {"Bank of America": "bofa", "Chase": "chase", "Wells Fargo": "wells_fargo", "Chime": "chime"}
            for idx, row in filtered_df.iterrows():
                c_info, c_action = st.columns([4, 1])
                c_info.text(f"📄 {row['Bank']} — {row['File Name']} ({row['Upload Date']})")
                
                with c_action:
                    with st.popover("🗑️ Delete"):
                        st.write("Confirm deletion?")
                        if st.button("Yes, delete", key=f"del_{row['ID']}", type="primary"):
                            target_bank_id = bank_options.get(row['Bank'], "unknown")
                            file_disk_path = os.path.join(UPLOAD_BASE_DIR, target_bank_id, row['Stored File'])
                            if os.path.exists(file_disk_path):
                                os.remove(file_disk_path)
                            delete_statement_from_db(row['ID'])
                            st.toast(f"Deleted {row['File Name']}", icon="🗑️")
                            st.rerun()
                            
        with tab2:
            bank_counts = filtered_df["Bank"].value_counts().reset_index()
            bank_counts.columns = ["Bank", "Count"]
            st.bar_chart(bank_counts, x="Bank", y="Count", use_container_width=True)

# Footer
st.divider()
st.caption("© 2026 ExpenseIQ — All Rights Reserved | pamelakyei15@gmail.com")