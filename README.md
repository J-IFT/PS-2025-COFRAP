# PS-2025-COFRAP

*PS = Projet Scolaire*

## 📚 Projet Scolaire | MSPR 2

Juin 2025

Groupe : Yasmine, Colas, Théo et Juliette

### 📌 Consignes du projet :

Fonctions à préparer:

- Une fonction générant un mot de passe pour un compte utilisateur spécifié en paramètres de la
fonction, dont la complexité est fixe (24 caractères, majuscules/minuscules/chiffres/caractères
spéciaux), et générant un qrcode à partir de ce mot de passe, stockant l'identifiant utilisateur et ce mot
de passe (en le chiffrant!) dans votre base de données.

- Une fonction générant un secret 2FA et le qrcode correspondant pour le compte utilisateur demandé
en paramètres de la fonction, et stockant cette information (en la chiffrant!) en base de données.

- Une fonction authentifiant un utilisateur à partir de son login, son mot de passe, et son code 2FA, après
avoir vérifié que ces identifiants ont moins de six mois d'ancienneté, sinon elle doit marqué le compte
comme "expiré" en base de données, et renvoyer une réponse à la frontend relançant le processus de
création de mot de passe et de 2FA.

Enfin, une frontend (simple), doit permettre d'authentifier un utilisateur, ou de le créer s'il n'existe pas (en
suivant le process décrit plus haut), ou de relancer le processus de création de mot de passe et de 2FA si
son login et son mot de passe sont expirés. Une autre équipe est en charge de sécuriser cette solution afin
d'éviter les abus typiques (création de comptes en boucle/spammeurs/etc).

Pour le moment, la COFRAP vous a demandé de réaliser un PoC (Proof of Concept) de cette solution, soit
sur un petit cluster Kubernetes (KinD, K3S ou cloud), soit via minikube ou Docker (minikube préféré si vous
ne pouvez pas, ou n'avez pas le temps, de mettre en place un cluster Kubernetes)

Concernant la base de données, vous pouvez utiliser un Statefulset Kubernetes, une VM dédiée ou un
conteneur docker dédié. La technologie utilisée est à votre discrétion: PostgreSQL, MariaDB, MongoDB,
etc. Votre base de données ne devrait contenir qu'une seule table pour stocker les informations de vos
utilisateurs. La table elle-même devrait être très simple, du type:
ID username
password
MFA
gendate
expired
ID username
password
MFA
gendate
expired

Le langage de programmation a utiliser pour preparer vos fonctions est, la aussi, a votre discretion,
cependant, Python est fortement recommande par la COFRAP, qui l'utilise deja dans la plupart de ses
projets (traduction: vous trouverez toutes les bibliotheques de fonctions necessaires assez facilement avec
Python).


### 🐱 Notre projet :

🔧 Plateforme : Docker Kubernetes avec OpenFaaS

🔧 Langage : Python (OpenFaaS template python3-http)

🔧 Backend serverless : OpenFaaS déployé sur Minikube

🔧 Frontend : Simple interface web HTML/CSS et JavaScript fetch API pour les appels backend

🔧 Base de données : PostgreSQL (chart Helm Bitnami)

🔧 Sécurité : chiffrement Fernet

🔧 QR code : génération au format otpauth://

🔧 Déploiement des fonctions : via DockerHub + faas-cli


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


🔒 Table users (PostgreSQL)

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    totp_secret TEXT,
    gendate TIMESTAMP NOT NULL,
    expired BOOLEAN DEFAULT FALSE
);


🧪 Tests réalisés

✅ Déploiement des 3 fonctions dans OpenFaaS

✅ Tests via faas-cli invoke

✅ Stockage en base PostgreSQL OK

✅ Déchiffrement Fernet OK

✅ Génération et vérification TOTP OK (via authenticator)

✅ Détection d’un compte expiré si > 6 mois OK


📝 Front-end 

Cette page HTML fournit une interface simple pour :

Créer un compte utilisateur avec génération automatique d’un mot de passe QR code et d’un QR code 2FA.

Se connecter avec un nom d’utilisateur, mot de passe et code 2FA.

Elle interagit avec un backend OpenFaaS exposé localement sur http://127.0.0.1:8080.

Structure de la page :

1. Création de compte

Champ texte : Nom d'utilisateur

Bouton : Créer un compte

Processus :

En cliquant sur le bouton, la page envoie deux requêtes successives au backend :

- /function/generate-password : génère un mot de passe unique et fournit un QR code image.

- /function/generate-2fa : génère une clé 2FA et fournit un QR code 2FA.

Les deux QR codes sont affichés sous la section.

2. Connexion

Champs texte :

- Nom d'utilisateur

- Mot de passe

- Code 2FA (ex: 123456)

- Bouton : Se connecter

Processus :

- En cliquant sur le bouton, la page envoie une requête POST au backend sur /function/verify-2fa avec le JSON contenant username, password et otp.

- Le résultat (succès ou erreur) est affiché dans un bloc texte.

Instructions d’utilisation :

Créer un compte :

- Renseigner un nom d’utilisateur.

- Cliquer sur Créer un compte.

- Scanner les deux QR codes (mot de passe et 2FA) avec une application de lecture QR et une application Authenticator (ex: Google Authenticator).


Se connecter :

- Saisir le nom d’utilisateur.

- Entrer le mot de passe lu dans le QR code.

- Entrer le code 2FA généré par l’application Authenticator.

- Cliquer sur Se connecter.

- Voir le résultat en bas de page.


### 💻 Applications et langages utilisés :

+ Visual studio code
+ PostgreSQL / Python / Docker Desktop Kubernetes Minikube Helm Openfaas

## 🌸 Merci !
© J-IFT
