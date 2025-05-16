import json
import secrets
import string
import pyqrcode
import base64
from cryptography.fernet import Fernet
import psycopg2
import time
import os

# 🔐 Clé de chiffrement — à passer plus tard via Kubernetes secret
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# 🌐 Connexion à PostgreSQL (modifie si besoin)
DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
DB_NAME = os.getenv("DB_NAME", "cofrap")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def handle(req):
    try:
        data = json.loads(req)
        username = data.get("username")

        if not username:
            return json.dumps({"error": "Missing username"}), 400

        # 🔑 Génération du mot de passe fort
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(chars) for _ in range(24))

        # 🔐 Chiffrer le mot de passe
        encrypted_password = fernet.encrypt(password.encode()).decode()

        # 📅 Timestamp actuel
        gendate = int(time.time())

        # 🐘 Insertion en base
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                mfa TEXT,
                gendate BIGINT,
                expired BOOLEAN
            )
        """)
        cur.execute("""
            INSERT INTO users (username, password, gendate, expired)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE
            SET password = EXCLUDED.password,
                gendate = EXCLUDED.gendate,
                expired = FALSE
        """, (username, encrypted_password, gendate, False))
        conn.commit()
        cur.close()
        conn.close()

        # 📦 Génération du QR code en base64
        qr = pyqrcode.create(password)
        qr_base64 = qr.png_as_base64_str(scale=5)

        # ✅ Réponse
        return json.dumps({
            "username": username,
            "password_plaintext": password,
            "qrcode_base64": qr_base64
        }), 200

    except Exception as e:
        return json.dumps({"error": str(e)}), 500
