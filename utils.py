import pandas as pd
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText

USER_FILE = "users.csv"

def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["name", "username", "password"])

def save_user(name, username, email, password):
    users = load_users()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = pd.DataFrame([[name, username, email, hashed]], columns=["name", "username", "email", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_FILE, index=False)

def validate_user(username, password):
    users = load_users()
    user_row = users[users["username"] == username]

    if not user_row.empty:
        stored_hash = user_row.iloc[0]["password"]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return user_row.iloc[0]["name"]  # return name on success
    return None

def send_verification_code(email, code):
    sender_email = "diabeticretinopathy1214@gmail.com"
    sender_password = "zzri gnjd vsdh hbfs"  # Use App Password if using Gmail

    message = MIMEText(f"Your verification code is: {code}")
    message['Subject'] = "Your Verification Code"
    message['From'] = sender_email
    message['To'] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())