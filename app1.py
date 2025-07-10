import streamlit as st
import re
import time
from utils import load_users, save_user, validate_user, send_verification_code
import random
from app import run_app

st.set_page_config("Diabetic Retinopathy Detection", layout="centered")

# 💅 Styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.name = ""
    st.session_state.just_logged_in = False
if "verification_pending" not in st.session_state:
    st.session_state.verification_pending = False
    st.session_state.verification_code = ""
    st.session_state.temp_user = {}
if "show_login" not in st.session_state:
    st.session_state.show_login = True
if "show_signup" not in st.session_state:
    st.session_state.show_signup = True
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Login"

# 🔐 MFA Email Verification (after login)
if st.session_state.verification_pending:
    st.title("🔐 Email Verification")
    st.info("📧 Check your email (and spam folder) for the 4-digit verification code.")

    code_input = st.text_input("Enter the code sent to your email:")

    if st.button("Verify"):
        if code_input == st.session_state.verification_code:
            st.session_state.logged_in = True
            st.session_state.name = st.session_state.temp_user["name"]
            st.session_state.just_logged_in = True

            # Clear verification session data
            st.session_state.verification_pending = False
            st.session_state.verification_code = ""
            st.session_state.temp_user = {}
            st.rerun()
        else:
            st.error("❌ Invalid verification code.")

# 🔓 Logged In
elif st.session_state.logged_in:
    if st.session_state.just_logged_in:
        st.success("✅ Login successful! Redirecting...")
        time.sleep(1.5)
        st.session_state.just_logged_in = False
        st.rerun()

    st.success(f"Welcome {st.session_state.name} 👋")
    run_app()

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# 👥 Login / Sign Up if NOT logged in
else:
    tab = st.sidebar.radio("Choose Action", ["Login", "Sign Up"],
                           index=0 if st.session_state.active_tab == "Login" else 1)
    
    def validate_password_strength(password):
        if len(password) < 8:
            return "Password must be at least 8 characters"
        if not re.search(r"[A-Z]", password):
            return "Password must include an uppercase letter"
        if not re.search(r"[a-z]", password):
            return "Password must include a lowercase letter"
        if not re.search(r"\d", password):
            return "Password must include a number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must include a special character"
        return None

    if tab == "Login":
        st.session_state.active_tab = "Login"
        st.title("🔐 Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            name = validate_user(username, password)
            if name:
                users = load_users()
                user_email = users[users["username"] == username]["email"].values[0]

                code = str(random.randint(1000, 9999))
                send_verification_code(user_email, code)

                st.session_state.verification_code = code
                st.session_state.temp_user = {
                    "name": name,
                    "username": username,
                    "email": user_email
                }
                st.session_state.verification_pending = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("❌ Incorrect username or password!")

    elif tab == "Sign Up":
        st.session_state.active_tab = "Sign Up"
        st.title("📝 Create a New Account")
        st.caption("Password must be at least 8 characters, include an uppercase letter, a lowercase letter, a number, and a special character.")
        
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm:
                st.warning("Passwords do not match.")
            elif username.strip() == "" or name.strip() == "" or email.strip() == "":
                st.warning("All fields are required.")
            else:
                strength_error = validate_password_strength(password)
                if strength_error:
                    st.error(f"⚠️ {strength_error}")
                else:
                    users = load_users()
                    if username in users["username"].values:
                        st.error("Username already exists!")
                    else:
                        save_user(name, username, email, password)
                        st.success("✅ Successfully Signed Up! Please log in.")
                        time.sleep(1.5)
                        st.session_state.show_signup = False
                        st.session_state.show_login = True
                        st.session_state.active_tab = "Login"  # Switch to login tab
                        st.rerun()
