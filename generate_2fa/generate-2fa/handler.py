import os
import psycopg2
import urllib.parse
import json
import random
import datetime

def generate_otp():
    """Génère un OTP numérique à 6 chiffres."""
    return f"{random.randint(0, 999999):06d}"

def handle(event, context):
    # Récupération de DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "DATABASE_URL not set"})
        }

    # Parse DATABASE_URL
    try:
        result = urllib.parse.urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Invalid DATABASE_URL: {str(e)}"})
        }

    # Connexion à la base PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        cursor = conn.cursor()
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"DB connection error: {str(e)}"})
        }

    # Générer un code 2FA (OTP)
    otp_code = generate_otp()
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(minutes=5)  # Code valable 5 minutes

    try:
        # Création automatique de la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS twofa_codes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(6) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL
            );
        """)

        # Insertion du code
        cursor.execute("""
            INSERT INTO twofa_codes (code, created_at, expires_at)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (otp_code, now, expires_at))

        inserted_id = cursor.fetchone()[0]
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"DB insert error: {str(e)}"})
        }

    cursor.close()
    conn.close()

    # Réponse JSON avec le code 2FA
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "2FA code generated successfully",
            "code": otp_code,
            "id": inserted_id,
            "expires_at": expires_at.isoformat() + "Z"
        })
    }
