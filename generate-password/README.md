🔐 Fonction generate-password – Résumé

🎯 Objectif :

Générer un mot de passe sécurisé pour un utilisateur donné, le chiffrer, l'enregistrer en base de données PostgreSQL, et retourner un QR code représentant ce mot de passe.

⚙️ Étapes réalisées par la fonction :

Lecture des variables d’environnement :

FERNET_KEY pour chiffrer le mot de passe.

DATABASE_URL pour se connecter à PostgreSQL.

Réception des données en entrée :

Attend un JSON avec une clé "username", par exemple :

json

{ "username": "juliette" }

Génération du mot de passe :

24 caractères, avec lettres, chiffres et symboles.

Chiffrement du mot de passe :

Utilisation de Fernet pour chiffrer le mot de passe.

Génération d’un QR code :

Encode le mot de passe en clair dans un QR code.

Le QR est retourné en base64 (image PNG).

Enregistrement ou mise à jour en base :

Si l’utilisateur n’existe pas : il est ajouté avec le mot de passe chiffré.

S’il existe : son mot de passe est remplacé.

Enregistre aussi :

gendate (date de génération)

expired (par défaut à false)

Réponse de la fonction :

Retourne un JSON contenant :

json

{
  "username": "juliette",
  "password_qr": "<QR CODE EN BASE64>"
}

🗃️ Structure de la table users créée si elle n'existe pas :

id	username	password	totp_secret	gendate	expired

PK	unique	chiffré	(null)	UTC	false


🗃️ Fonctionnement avec la base de données PostgreSQL

Connexion à la base :

La fonction utilise la variable d’environnement DATABASE_URL pour se connecter à une base PostgreSQL. Cette URL contient toutes les infos : hôte, port, nom d’utilisateur, mot de passe et base cible.

Exemple :

postgres://postgres:cJNzEtOleI@127.0.0.1:5432/postgres

Création de la table si elle n’existe pas :

Lors de chaque appel, la fonction vérifie si la table users existe. Si elle n’existe pas, elle la crée avec la structure suivante :

sql

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    totp_secret TEXT,
    gendate TIMESTAMP NOT NULL,
    expired BOOLEAN DEFAULT FALSE
);

Insertion ou mise à jour de l’utilisateur :

Si l’utilisateur n’existe pas encore, un nouvel enregistrement est ajouté.

S’il existe déjà (clé unique sur username), son mot de passe est mis à jour avec le nouveau mot de passe généré, la date de génération est mise à jour, et le champ expired est remis à false.

Requête SQL :

sql

INSERT INTO users (username, password, gendate, expired)
VALUES (%s, %s, %s, false)
ON CONFLICT (username) DO UPDATE SET
    password = EXCLUDED.password,
    gendate = EXCLUDED.gendate,
    expired = false;

✅ Résumé en une phrase :

La fonction interagit dynamiquement avec PostgreSQL : elle crée la table users si nécessaire, puis insère ou met à jour les données liées à l’utilisateur en fonction de son existence dans la base.