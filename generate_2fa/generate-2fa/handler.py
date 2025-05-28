import os
import json
import base64
import io
import psycopg2
import urllib.parse
import qrcode
import pyotp
from datetime import datetime
from cryptography.fernet import Fernet

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
                "body": json.dumps({"error": "Missing environment variables"}),
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        fernet = Fernet(FERNET_KEY.encode())

        data = json.loads(event.body)
        username = data.get("username")

        if not username:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'username' in request body"}),
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        # Générer une clé TOTP encodée en base32
        totp_secret = pyotp.random_base32()

        # Format otpauth://
        otp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=username, issuer_name="SecureApp")

        # QR Code au format base64
        qrcode_b64 = generate_qrcode(otp_uri)

        # Chiffrer la clé TOTP
        encrypted_secret = fernet.encrypt(totp_secret.encode()).decode()

        # Connexion à la base PostgreSQL
        result = urllib.parse.urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()

        # S'assurer que la table existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                totp_secret TEXT,
                gendate TIMESTAMP NOT NULL,
                expired BOOLEAN DEFAULT FALSE
            );
        """)

        # Mettre à jour le champ totp_secret
        now = datetime.utcnow()
        cursor.execute("""
            UPDATE users
            SET totp_secret = %s
            WHERE username = %s
        """, (encrypted_secret, username))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "TOTP secret generated and stored",
                "qrcode": qrcode_b64
            }),
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
        }
