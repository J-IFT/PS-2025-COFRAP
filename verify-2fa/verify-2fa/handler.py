import os
import json
import psycopg2
import urllib.parse
from datetime import datetime

def handle(event, context):
    # 1. Extraire DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "DATABASE_URL not set"})
        }

    # 2. Extraire le code de la requête JSON
    try:
        body = json.loads(event.body)
        code = body.get("code")
        if not code:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'code' in request body"})
            }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid JSON: {str(e)}"})
        }

    # 3. Parse de l'URL pour psycopg2
    try:
        result = urllib.parse.urlparse(database_url)
        dbname = result.path[1:]
        conn = psycopg2.connect(
            dbname=dbname,
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"DB connection error: {str(e)}"})
        }

    # 4. Vérification du code
    try:
        now = datetime.utcnow()
        cursor.execute("""
            SELECT id FROM twofa_codes
            WHERE code = %s AND expires_at > %s
        """, (code, now))
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "valid": False,
                    "message": "Code is invalid or expired"
                })
            }

        # 5. Rendre le code inutilisable (anti-rejeu)
        cursor.execute("""
            UPDATE twofa_codes
            SET expires_at = %s
            WHERE id = %s
        """, (now, row[0]))
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "valid": True,
                "message": "Code is valid and has been marked as used"
            })
        }

    except Exception as e:
        cursor.close()
        conn.close()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"DB error: {str(e)}"})
        }
