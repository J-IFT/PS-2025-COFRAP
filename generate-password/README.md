🔐 Fonction generate-password – Résumé

Ce qui est demandé :

Générer un mot de passe complexe (24 caractères), le chiffrer, créer un QR Code à usage unique, et stocker le tout dans la BDD.

Ce que nous avons fait :
✔ Mot de passe généré avec complexité
✔ QR code encodé en base64
✔ Stockage en base PostgreSQL (chiffré avec Fernet)
✔ Données sauvegardées dans la table users
✔ Fonction OpenFaaS fonctionnelle et testée

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

Quand on fait invoke sur http://127.0.0.1:8080/ui/ on coche json puis {"username":"juliette"} on obtient :

{
  "username": "juliette",
  "password_qr": "iVBORw0KGgoAAAANSUhEUgAAAUoAAAFKAQAAAABTUiuoAAACA0lEQVR4nO2awW3jMBBF36wI+EgBKSClSB1sSYstKR2IpaQD8WhAws+BlO1ssIFiQDYPMweLkt/hA8IMZz5lYmekX3tJcNRRRx111NEjUasRsDGbQa6rEuPhAhzdFaFchgkgvyBYghEXgG4BwI4U4OgdaK4pZNZ3ghzQBJhZeIwAR+9ANbGaNIONTxHg6I/QfBKpp+TWMwQ4+t/Y6lwUkMGG+QUjztjwBrez89O1OlrRZGZm/fZ0eA8Aa2kJHyHA0T1RcuuaQkp9B8Sz1Xw7WoCjP5+3xhyAbMaghbJ5wbpNXocLcHRXXHLrbCIK0ggiryZyD3XyOk6Ao/fMW5t58UcqBbBuY9nnrXZQJEkQFzTFpd4OWqg1MUoMkjQ9Xaujl9cjSTNAlCQtSPOnf/1ttYLqbw8lwfQeIPWdvBK2itoI2JhPqs17tmI/kV69y2gHLbWulr6yW0nS3JVnW2H0StgQamYnmdlJxY2317NV+z37+VZr6E1ulSZw7kpvwTB3qv5uI1odvZ4d17bi+hMXbDxcgKO74uvZcV43G3ezMXSkAEfv8TIu21NUtQiTmZH61T34ZtDw74P0ey4fZwjWIJ+3WkbLN0/JbkdkGx8owNHv4pPz1ElTrCuG+TqN+bzVBLq5uiW6uiqGblm5T9gO+uXsuF67m3Nj7wkdddRRRx1tBf0A5TcbtRmFxZYAAAAASUVORK5CYII="
}

Pareil avec la commande echo '{"username":"juliette"}' | faas-cli invoke generate-password --gateway http://127.0.0.1:8080