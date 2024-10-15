# Script de gestion des tournois Challonge

Ce script Python permet de gérer les tournois sur Challonge via leur API.

## Prérequis

- Python 3.6 ou supérieur
- pipenv

## Installation de l'environnement python/pipenv

### Windows

1. Installez Python depuis [python.org](https://www.python.org/downloads/windows/)
2. Ouvrez PowerShell et exécutez :

    ```bash
    pip install pipenv
    ```

### Linux

1. Installez Python et pip avec votre gestionnaire de paquets. Par exemple, sur Ubuntu :

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```

2. Installez pipenv :

   ```bash
   pip3 install pipenv
   ```

### macOS

1. Installez Homebrew si ce n'est pas déjà fait :

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. Installez Python et pipenv :

    ```bash
    brew install python
    pip3 install pipenv
    ```

## Configuration de l'environnement

1. Clonez ce dépôt ou téléchargez le script
2. Dans le répertoire du script, créez l'environnement virtuel :

    ```bash
    pipenv install
    ```

## Obtention de votre clé API Challonge

1. Connectez-vous à votre compte Challonge
2. Allez dans les paramètres de votre compte
3. Dans la section "Developer API", copiez la Clé API (v1)

## Configuration du script

1. Créez un fichier `.env` dans le même répertoire que le script
2. Ajoutez votre clé API dans ce fichier :

   ```bash
   CHALLONGE_API_KEY=votre_clé_api_ici
   ```

## Utilisation du script

Exécutez le script avec la commande souhaitée.

Pour voir toutes les commandes disponibles :

```bash
python challonge.py --help
```

### Lister les tournois

```bash
# usage: challonge.py list [-h] [--date DATE] [--participants_count PARTICIPANTS_COUNT]

# Lister les tournois
python challonge.py list

# Lister les tournois depuis une date
python challonge.py list --date 2024-09-01

+---------+--------------------+----------------------------+--------------------------+
| Titre   | Type de tournoi    | Date de création (Paris)   |   Nombre de participants |
+=========+====================+============================+==========================+
| Test 01 | single elimination | 2024-10-10 14:37:33 CEST   |                        0 |
+---------+--------------------+----------------------------+--------------------------+
```

### Supprimer les tournois

```bash
# usage: challonge.py delete [-h] --date DATE

# Tous les tournois à partir d'une date
python challonge.py delete --date 2024-09-01
```

### Créer un tournoi à élimination simple

```bash
# usage: challonge.py create_single [-h] --name NAME
python challonge.py create_single --name "Switcharoo"
```

### Créer un tournoi à double élimination

```bash
# usage: challonge.py create_double [-h] --name NAME
python challonge.py create_double --name "Switcharoo"
```

### Ajouter des participants à un tournoi

```bash
# usage: challonge.py add_participants [-h] --tournament_id TOURNAMENT_ID --participants PARTICIPANTS [PARTICIPANTS ...]
python challonge.py add_participants --tournament_id bbkdcbam --participants "player1 x player2" "player3 x player4" "player5 x player6" "player7 x player8"
```

### Supprimer tous les participants d'un tournoi

```bash
# usage: challonge.py remove_participants [-h] --tournament_id TOURNAMENT_ID
```
