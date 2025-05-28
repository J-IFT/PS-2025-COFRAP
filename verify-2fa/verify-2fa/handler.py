import os
import json
import psycopg2
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import pyotp

def handle(event, context):
    try:
        # Chargement des variables d’environnement
        FERNET_KEY = os.getenv("FERNET_KEY")
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not FERNET_KEY or not DATABASE_URL:
            return {
                "statusCode": 500,
                "body": "Missing environment variables",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        fernet = Fernet(FERNET_KEY.encode())

        # Lecture du corps JSON
        data = json.loads(event.body)
        username = data.get("username")
        password_input = data.get("password")
        otp_input = data.get("otp")

        if not username or not password_input or not otp_input:
            return {
                "statusCode": 400,
                "body": "Missing required fields (username, password, otp)",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        # Connexion base PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Vérification utilisateur
        cur.execute("SELECT password, totp_secret, gendate, expired FROM users WHERE username = %s", (username,))
        row = cur.fetchone()

        if not row:
            return {
                "statusCode": 404,
                "body": "User not found",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        encrypted_password, encrypted_totp_secret, gendate, expired = row

        # Vérifie si le compte est expiré
        now = datetime.utcnow()
        if gendate + timedelta(days=180) < now or expired:
            # Mise à jour en base si non déjà expiré
            if not expired:
                cur.execute("UPDATE users SET expired = true WHERE username = %s", (username,))
                conn.commit()
            cur.close()
            conn.close()
            return {
                "statusCode": 403,
                "body": "Account expired. Please reset password and 2FA.",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        # Déchiffrement
        try:
            decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
            decrypted_totp_secret = fernet.decrypt(encrypted_totp_secret.encode()).decode()
        except Exception as e:
            cur.close()
            conn.close()
            return {
                "statusCode": 500,
                "body": f"Decryption error: {str(e)}",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        # Vérification mot de passe
        if password_input != decrypted_password:
            cur.close()
            conn.close()
            return {
                "statusCode": 401,
                "body": "Invalid password",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        # Vérification TOTP
        totp = pyotp.TOTP(decrypted_totp_secret)
        if not totp.verify(otp_input):
            cur.close()
            conn.close()
            return {
                "statusCode": 401,
                "body": "Invalid OTP",
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            }

        cur.close()
        conn.close()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Authentication successful",
                "username": username
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
            "body": f"Internal server error: {str(e)}",
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
        }
