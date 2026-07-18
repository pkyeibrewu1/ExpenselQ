import streamlit as st
import sqlite3
import os

# Page configuration
st.set_page_config(
    page_title="ExpenseIQ",
    page_icon="💸",
    layout="centered"
)

# Ensure the 'data' directory exists
os.makedirs("data", exist_ok=True)
DB_PATH = os.path.join("data", "expenseiq.db")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Run database initialization
init_db()

# --- HELPER DATABASE FUNCTIONS ---
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
        # This triggers if the email already exists in the database
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns the user data (like first name) if found, otherwise None


# --- STREAMLIT SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "landing"  # Pages: "landing", "signup", "login", "statements"
if "user_name" not in st.session_state:
    st.session_state.user_name = None

def navigate_to(page_name):
    st.session_state.page = page_name


# --- SCREEN CONTROLLER ---

# SCREEN A: The Landing Page
if st.session_state.page == "landing":
    st.title("💸 ExpenselQ")
    st.subheader("No dollar left unaccounted.")
    st.write(
        "Your finances, finally made simple. "
        "Track where your money goes and get smart suggestions to help you spend less and save more."
    )
    
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

    st.divider()
    st.subheader("📘 Learn More")
    with st.expander("What does ExpenseIQ do?"):
        st.write("ExpenseIQ turns raw transactions into clear, actionable insight.")

    st.divider()
    st.subheader("🎬 See it in action")
    st.info("📹 Your introductory video will go here.")
    st.divider()
    st.caption("© 2026 ExpenseIQ | pamelakyei15@gmail.com")


# SCREEN B: Registration Page
elif st.session_state.page == "signup":
    st.title("✨ Join the ExpenseIQ Family")
    st.subheader("Create your account to get started")
    st.divider()
    
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    st.markdown("###")
    
    if st.button("Sign Up", type="primary", use_container_width=True):
        if not first_name or not last_name or not email or not password:
            st.warning("⚠️ Please fill in all required fields.")
        elif not first_name.isalpha():
            st.error("⚠️ First name can only contain letters.")
        elif not last_name.isalpha():
            st.error("⚠️ Last name can only contain letters.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match. Please try again.")
        else:
            # Attempt to save user into SQLite
            success = add_user(first_name, last_name, email, password)
            if success:
                st.success(f"🎉 Account created successfully for {first_name}!")
                st.button("Proceed to Login", on_click=navigate_to, args=("login",))
            else:
                st.error("⚠️ An account with this email already exists.")

    st.button("⬅️ Back to Home", on_click=navigate_to, args=("landing",))


# SCREEN C: Login Page
elif st.session_state.page == "login":
    st.title("🔓 Login to ExpenseIQ")
    st.subheader("Welcome back! Enter your details to view your dashboard.")
    st.divider()
    
    login_email = st.text_input("Email Address", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    st.markdown("###")
    
    if st.button("Sign In", type="primary", use_container_width=True):
        if not login_email or not login_password:
            st.warning("⚠️ Please enter both your email and password.")
        else:
            # Check SQLite database
            user_found = verify_user(login_email, login_password)
            if user_found:
                st.session_state.user_name = user_found[0] # Store their first name
                st.success(f"🔐 Access granted. Welcome back, {st.session_state.user_name}!")
                # Jump directly to the Statements Upload page
                st.button("Go to Statements Upload", on_click=navigate_to, args=("statements",))
            else:
                st.error("❌ Invalid email or password. Please try again.")
            
    st.button("⬅️ Back to Home", on_click=navigate_to, args=("landing",))


# SCREEN D: Statements Upload Page (The Post-Login Goal!)
elif st.session_state.page == "statements":
    st.title(f"📁 Welcome to ExpenseIQ, {st.session_state.user_name}!")
    st.subheader("Let's get started by uploading your financial data.")
    st.write("Before we can build your visual analytics dashboard, we need some data to work with.")
    
    st.divider()
    
    # File Uploader implementation
    st.markdown("#### 📂 Upload your bank statement")
    uploaded_file = st.file_uploader(
        "Choose a CSV file exported from your bank app", 
        type=["csv"]
    )
    
    if uploaded_file is not None:
        st.success(f"📈 successfully loaded **{uploaded_file.name}**! Ready to build insights.")
        # Future step: process this file using Pandas
        
    st.markdown("###")
    
    # Log out button to return home safely
    if st.button("🚪 Log Out", type="secondary"):
        st.session_state.user_name = None
        navigate_to("landing")