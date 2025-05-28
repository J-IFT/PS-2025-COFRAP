🔐 Fonction 2 — generate-2fa

Ce qui est demandé :

Générer un secret 2FA pour un utilisateur, générer un QRCode de ce 2FA, le chiffrer, et le stocker.

Ce que nous avons fait :
✔ Génération d’un code OTP
✔ Insertion dans une table dédiée (twofa_codes)
✔ Fonctionnalité fonctionnelle et testée
✔ Intégrée dans le même environnement que la fonction 1

!!!!!!Ajouter le chiffrement + QR code dans une V2

But :

Génère un code 2FA (One-Time Password à 6 chiffres), l'enregistre dans la base PostgreSQL, et le retourne en réponse.

Entrée :

Aucune donnée n'est requise en entrée (fonction autonome). Elle pourrait être étendue pour inclure un identifiant utilisateur si besoin.

Sortie :

Un JSON contenant :

json

{
  "message": "2FA code generated successfully",
  "code": "824083",
  "id": 1,
  "expires_at": "2025-05-21T13:04:15Z"
}

code : le code OTP (6 chiffres)

id : l'identifiant de l'entrée en base

expires_at : date UTC d’expiration du code (valable 5 minutes)

Traitement effectué :

Génération d’un OTP aléatoire à 6 chiffres.

Enregistrement dans la base PostgreSQL dans la table twofa_codes (créée automatiquement si besoin).

Calcul de la date d’expiration (5 minutes après création).

Retourne le code, son identifiant en base, et sa date d’expiration.

Base de données :

La fonction crée automatiquement la table si elle n’existe pas :

sql

CREATE TABLE IF NOT EXISTS twofa_codes (
  id SERIAL PRIMARY KEY,
  code TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL
);
Variables d’environnement requises :

DATABASE_URL : chaîne de connexion PostgreSQL au format URI

Ex. : postgres://user:password@host:port/dbname

Quand on fait invoke sur http://127.0.0.1:8080/ui/ en cochant text voici le résultat :

{
  "message": "2FA code generated successfully",
  "code": "824083",
  "id": 1,
  "expires_at": "2025-05-21T13:04:15.112095Z"
}