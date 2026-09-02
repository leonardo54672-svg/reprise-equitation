# Mes reprises — suivi des séances d'équitation

Application web installable (PWA) pour iPhone. Suivi de cartes de 10 séances.
Sans compte, sans serveur, sans base de données : **toutes les données restent dans le navigateur de l'iPhone**.

---

## 1. Arborescence

```
reprises-equitation/
├── index.html                    Application complète (HTML + CSS + JS en un seul fichier)
├── manifest.json                 Déclaration PWA (nom, icônes, mode plein écran)
├── sw.js                         Service worker (mode hors ligne)
├── README.md                     Ce document
├── icons/
│   ├── apple-touch-icon.png      180×180 — icône écran d'accueil iPhone
│   ├── icon-192.png              192×192
│   ├── icon-512.png              512×512
│   └── icon-512-maskable.png     512×512 avec marge de sécurité (Android)
└── tools/
    └── make_icons.py             Script optionnel de régénération des icônes (Python + Pillow)
```

Aucune dépendance, aucune compilation, aucun `npm install`.

---

## 2. Fonctionnement

| Écran | Comportement |
|---|---|
| Carte en cours | Numéro de carte, date d'achat, compteur `x / 10`, séances restantes, barre à 10 segments |
| Ajouter une séance | Un appui = date du jour enregistrée, aucune confirmation |
| Ajouter une autre date | Sélecteur de date natif iOS |
| Ajouter une carte de 10 séances | Sélecteur de date d'achat, puis création de la carte |
| Séances de la carte en cours | Liste antichronologique, suppression avec confirmation |
| Toutes mes séances | Total, cartes terminées, rythme moyen, et calendrier des 12 derniers mois |
| Mes cartes | Toutes les cartes avec statut, date d'achat, plage d'utilisation ; se déplient pour voir le détail |
| Exporter / Restaurer | CSV complet, réimportable |

### Modèle de données

Une **carte** = `{ numéro, date d'achat, séances[] }`.
La **carte active** est la première carte non remplie, dans l'ordre des numéros. Conséquences :

- Une carte peut être achetée à l'avance : elle passe en statut *En attente* et prend automatiquement le relais quand la précédente atteint 10 séances.
- Supprimer une séance d'une carte terminée la fait repasser *En cours* automatiquement.
- Aucune carte n'est jamais archivée manuellement : le statut se déduit du remplissage.

### Règles de gestion retenues

- **Double appui protégé** : si une séance est déjà enregistrée pour aujourd'hui, l'ajout rapide est refusé avec un message. Deux séances le même jour restent possibles via « Ajouter une autre date », avec confirmation explicite.
- **Carte non entamée** : ajouter une carte alors qu'une carte vide existe déjà déclenche une confirmation, pour éviter d'empiler des cartes fantômes.
- **Suppression d'une carte** : possible uniquement si elle ne contient aucune séance. Aucun historique ne peut être effacé par mégarde.
- **Calendrier** : 12 derniers mois glissants, une case par jour. Les séances plus anciennes restent comptées dans le total et sont signalées à droite du titre.

---

## 3. Test en local (facultatif)

Un double-clic sur `index.html` suffit pour vérifier l'interface, mais le service worker
ne s'active pas en `file://`. Pour un test complet :

```bash
cd reprises-equitation
python3 -m http.server 8000
```

Puis `http://localhost:8000` sur l'ordinateur, ou `http://<ip-du-mac>:8000` depuis l'iPhone
sur le même réseau Wi-Fi.

---

## 4. Déploiement sur GitHub Pages

**Prérequis** : un compte GitHub. HTTPS est obligatoire pour qu'une PWA soit installable ;
GitHub Pages le fournit automatiquement.

### Option A — sans ligne de commande (recommandé)

1. Sur github.com : **New repository**.
2. Nom : `reprises-equitation`. Visibilité : **Public** (Pages est gratuit sur les dépôts publics).
3. Ne pas cocher « Add a README ». **Create repository**.
4. Sur la page du dépôt vide : **uploading an existing file**.
5. Glisser **le contenu** du dossier (`index.html`, `manifest.json`, `sw.js`, `README.md`, dossiers `icons/` et `tools/`) — pas le dossier parent lui-même.
6. **Commit changes**.
7. Onglet **Settings** → **Pages**.
8. *Source* : `Deploy from a branch`. *Branch* : `main`, dossier `/ (root)`. **Save**.
9. Attendre 1 à 3 minutes. L'URL s'affiche en haut de la page :
   `https://<votre-identifiant>.github.io/reprises-equitation/`

### Option B — en ligne de commande

```bash
cd reprises-equitation
git init
git add .
git commit -m "Application de suivi des reprises"
git branch -M main
git remote add origin https://github.com/<votre-identifiant>/reprises-equitation.git
git push -u origin main
```

Puis étapes 7 à 9 ci-dessus.

### Mise à jour ultérieure

Remplacer les fichiers dans le dépôt, puis **incrémenter la version du cache** dans `sw.js`
(`var CACHE = 'reprises-v3';`). Sans cela, l'iPhone continuera de servir l'ancienne version.

---

## 5. Installation sur iPhone

1. Ouvrir **Safari** (obligatoire — Chrome iOS ne sait pas installer de PWA).
2. Aller sur `https://<votre-identifiant>.github.io/reprises-equitation/`.
3. Bouton **Partager** → **Sur l'écran d'accueil** → **Ajouter**.
4. L'application s'ouvre en plein écran, sans barre d'adresse, et fonctionne **sans réseau**
   après la première ouverture.

---

## 6. Données et sauvegarde

Stockage dans le `localStorage` de Safari, clé `reprises.v2`. Les données survivent à la
fermeture de l'application et au redémarrage du téléphone. Une base `reprises.v1` d'une
version antérieure est migrée automatiquement au premier lancement.

Format du CSV (séparateur `;`, compatible Excel français) :

```
Carte;Date achat;Statut;Seance;Date;Date ISO
1;15/01/2026;Terminee;1;15/01/2026;2026-01-15
2;10/04/2026;En cours;1;14/04/2026;2026-04-14
3;01/09/2026;En attente;0;;
```

Le bouton *Restaurer une sauvegarde* réinjecte ce fichier (les exports de la version
précédente à 5 colonnes sont également acceptés).

---

## 7. Revue de sécurité et de confidentialité

### 7.1 Surface d'attaque

| Élément | État |
|---|---|
| Serveur applicatif | Aucun |
| Base de données distante | Aucune |
| Compte utilisateur, mot de passe | Aucun |
| Dépendance tierce (npm, CDN, police web, analytics) | Aucune — vérifié automatiquement : le code ne contient aucune URL externe |
| Requête réseau après chargement | Aucune (`fetch`, `XMLHttpRequest` absents du code) |
| `eval` / `new Function` | Absents |
| Injection HTML | Impossible : tout le contenu variable est écrit via `textContent`, jamais via `innerHTML` |

Une application sans backend et sans dépendance supprime d'emblée les vecteurs les plus
courants : injection SQL, vol de session, fuite via un prestataire tiers, compromission
d'une bibliothèque npm.

### 7.2 Mesures de durcissement intégrées

- **Content-Security-Policy** restrictive déclarée dans `index.html` : seules les ressources
  du même domaine sont chargeables, les objets et iframes sont interdits, les formulaires
  ne peuvent envoyer de données nulle part.
- **`referrer: no-referrer`** : aucune information d'origine transmise.
- **Service worker cloisonné** : il n'intercepte que les requêtes `GET` de son propre domaine.
- **Import CSV traité comme une donnée hostile** : seules les dates au format `AAAA-MM-JJ`
  et les numéros entiers sont retenus, tout le reste est ignoré. Un fichier CSV piégé ne
  peut pas injecter de code (testé).

### 7.3 Risques résiduels

| # | Risque | Criticité | Analyse | Parade |
|---|---|---|---|---|
| 1 | **Origine partagée GitHub Pages** | Moyenne | Tous vos dépôts publiés sont servis depuis `<identifiant>.github.io`. Toute autre page publiée sous ce même compte partage la même origine et peut donc lire le `localStorage` de cette application | N'héberger que du code maîtrisé sous ce compte, ou utiliser un nom de domaine dédié |
| 2 | **Compromission du compte GitHub** | Moyenne | Un attaquant modifiant le dépôt pourrait publier une version piégée que l'iPhone téléchargerait à la prochaine ouverture en ligne | Authentification à deux facteurs obligatoire sur GitHub, idéalement par passkey |
| 3 | **Accès physique au téléphone** | Faible | Téléphone déverrouillé = données lisibles. L'application n'a pas de verrou propre | Code de déverrouillage et Face ID sur l'iPhone |
| 4 | **Purge du stockage par iOS** | Moyenne | Safari peut effacer le stockage local d'un site inutilisé plusieurs semaines. Une PWA installée sur l'écran d'accueil et ouverte régulièrement est peu concernée, mais le risque n'est pas nul | Export CSV après chaque carte terminée |
| 5 | **Désinstallation** | Moyenne | Supprimer l'icône de l'écran d'accueil efface les données, sans avertissement | Même parade : export CSV |
| 6 | **Perte de confidentialité par l'export** | Faible | Le CSV sort de l'application vers la destination que vous choisissez (Fichiers, iCloud, mail) | Choisir une destination maîtrisée |
| 7 | **Inférence sur vos habitudes** | Faible | Les données révèlent vos créneaux réguliers d'absence. Elles ne quittent pas le téléphone, mais un accès au CSV les exposerait | Sensibilité intrinsèquement basse : uniquement des dates |

### 7.4 Ce que l'application ne fait pas

Aucune collecte, aucune télémétrie, aucun cookie, aucune publicité, aucun identifiant
publicitaire, aucune géolocalisation, aucune permission demandée. Le code publié est
intégralement lisible : `index.html` fait environ 900 lignes et peut être relu.

### 7.5 Verdict

Le profil de risque est **faible**. Les deux points méritant une action concrète sont
l'**activation de la double authentification GitHub** (risque n°2) et l'**export CSV
périodique** (risques n°4 et 5) — le second étant déjà outillé dans l'application.

---

## 8. Personnalisation rapide

| Besoin | Où intervenir |
|---|---|
| Carte de 12 ou 15 séances | `index.html`, ligne `var SIZE = 10;` |
| Couleur de l'application | `index.html`, variables `--accent` (mode clair et mode sombre) |
| Titre sur l'écran d'accueil | `manifest.json` (`short_name`) et balise `apple-mobile-web-app-title` |
| Icône | Remplacer les fichiers de `icons/`, ou relancer `python3 tools/make_icons.py` |

Le mode sombre est géré automatiquement selon le réglage du système iOS.
