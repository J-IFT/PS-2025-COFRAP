⬜ Fonction 3 – verify-2fa

Ce qui est demandé :

Vérifier que le login, mot de passe, et code 2FA sont valides et que les identifiants datent de moins de 6 mois. Sinon, marquer le compte comme expiré.

Ce qu'on a fait :

Récupérer les données chiffrées de l’utilisateur (depuis la table users)

Déchiffrer le mot de passe avec la clé Fernet

Comparer au mot de passe fourni

Vérifier la date de génération (gendate) < 6 mois

Vérifier que le code 2FA correspond à celui généré (dans twofa_codes, ou ajouter totp_secret dans users)

Si échec → marquer expired = true et retourner une réponse adaptée

////

🎯 Objectif :

Authentifier un utilisateur en vérifiant :

- Son login

- Son mot de passe

- Son code TOTP généré par l’app 2FA

- Que les identifiants datent de moins de 6 mois


🧠 Fonctionnement :

- Récupère les infos de l’utilisateur depuis la base PostgreSQL.

- Déchiffre le mot de passe stocké et le compare à celui envoyé.

- Déchiffre le totp_secret, et génère un code TOTP valide pour l’instant T.

- Compare ce code au code fourni.

- Vérifie que le champ gendate est récent (< 6 mois).

- Si tout est OK → authentification validée.

- Sinon → retourne une erreur, et marque le compte comme expired = true en base.