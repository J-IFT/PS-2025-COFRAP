# PS-2025-COFRAP

*PS = Projet Scolaire*

## 📚 Projet Scolaire | MSPR 2

Juin 2025

Groupe : Yasmine, Colas, Théo et Juliette

### 📌 Consignes du projet :

à remplir ici


### 🐱 Notre projet :

🔧 Plateforme : Kubernetes avec OpenFaaS

🔧 Backend : Fonctions Python serverless

🔧 Frontend : Simple interface web (HTML/JS ou React minimaliste)

🔧 Base de données : PostgreSQL (recommandé pour sécurité/fiabilité)

🔧 Outils utilisés : Docker (build d'image de chaque fonction), Helm pour déployer OpenFaaS sur le cluster K8s, OpenFaaS CLI (faas-cli) pour push les fonctions



🔹 Fonction 1 : generate_password_qrcode

- Paramètre : username

- Génère :

mot de passe fort (24 caractères avec maj/min/chiffres/spéciaux)

QRCode de ce mot de passe

- Chiffre et stocke en base :

username, password, gendate, expired=0

- Librairies utiles :

secrets ou random, string

pyqrcode, cryptography ou Fernet pour chiffrement

psycopg2 ou SQLAlchemy pour DB



🔹 Fonction 2 : generate_2fa_secret

- Paramètre : username

Génére un secret OTP (TOTP)

Crée un QRCode compatible Google Authenticator

- Chiffre et stocke en base :

MFA, username, gendate

- Librairies utiles :

pyotp, qrcode



🔹 Fonction 3 : authenticate_user

- Paramètres : username, password, code_2FA

- Vérifie :

mot de passe et code TOTP

que les identifiants ne sont pas expirés (>6 mois → expired = 1)

Si expiré → relancer création mot de passe + 2FA

Retourne JSON : succès / erreur / renouvellement nécessaire




### 💻 Applications et langages utilisés :

+ Visual studio code
+ PostgreSQL / Python / Docker Desktop Kubernetes Minikube Helm Openfaas

## 🌸 Merci !
© J-IFT
