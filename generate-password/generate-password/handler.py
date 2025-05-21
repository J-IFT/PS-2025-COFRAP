import os
import json
import random
import string
import io
import qrcode
import base64
import psycopg2
from datetime import datetime
from cryptography.fernet import Fernet

def generate_password(length=24):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))

def generate_qrcode(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def handle(event, context):
    try:
        FERNET_KEY = os.getenv("FERNET_KEY")
        DATABASE_URL = os.getenv("DATABASE_URL")

        if not FERNET_KEY or not DATABASE_URL:
            return {
                "statusCode": 500,
                "body": "Missing environment variables"
            }

        fernet = Fernet(FERNET_KEY.encode())

        data = json.loads(event.body)
        username = data.get("username")

        if not username:
            return {
                "statusCode": 400,
                "body": "Missing 'username' in request body"
            }

        # Génération du mot de passe et des données associées
        password = generate_password()
        encrypted_pw = fernet.encrypt(password.encode()).decode()
        qrcode_b64 = generate_qrcode(password)
        gendate = datetime.utcnow()

        # Connexion PostgreSQL et création/enregistrement
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                totp_secret TEXT,
                gendate TIMESTAMP NOT NULL,
                expired BOOLEAN DEFAULT FALSE
            );
        """)
        cur.execute("""
            INSERT INTO users (username, password, gendate, expired)
            VALUES (%s, %s, %s, false)
            ON CONFLICT (username) DO UPDATE SET
                password = EXCLUDED.password,
                gendate = EXCLUDED.gendate,
                expired = false;
        """, (username, encrypted_pw, gendate))
        conn.commit()
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "username": username,
                "password_qr": qrcode_b64
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Internal error: {str(e)}"
        }
