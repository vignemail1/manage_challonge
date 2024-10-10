# Script de gestion des tournois Challonge

Ce script Python permet de gérer les tournois sur Challonge via leur API.

## Prérequis

- Python 3.6 ou supérieur
- pipenv

## Installation de l'environnement python/pipenv

### Windows

1. Installez Python depuis [python.org](https://www.python.org/downloads/windows/)
2. Ouvrez PowerShell et exécutez :

    ```shell
    pip install pipenv
    ```

### Linux

1. Installez Python et pip avec votre gestionnaire de paquets. Par exemple, sur Ubuntu :

    ```shell
    sudo apt update
    sudo apt install python3 python3-pip
    ```

2. Installez pipenv :

   ```shell
   pip3 install pipenv
   ```

### macOS

1. Installez Homebrew si ce n'est pas déjà fait :

    ```shell
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. Installez Python et pipenv :

    ```shell
    brew install python
    pip3 install pipenv
    ```

## Configuration de l'environnement

1. Clonez ce dépôt ou téléchargez le script
2. Dans le répertoire du script, créez l'environnement virtuel :

    ```shell
    pipenv install
    ```

## Obtention de votre clé API Challonge

1. Connectez-vous à votre compte Challonge
2. Allez dans les paramètres de votre compte
3. Dans la section "Developer API", copiez la Clé API (v1)

## Configuration du script

1. Créez un fichier `.env` dans le même répertoire que le script
2. Ajoutez votre clé API dans ce fichier :

   ```ini
   CHALLONGE_API_KEY=votre_clé_api_ici
   ```

3. (optionnel) Vous changez également la Timezone dans laquelle vous voulez la sortie des dates/heures en ajoutant dans `.env` :

    ```ini
    TIMEZONE=Europe/Paris
    ```

## Utilisation du script

Exécutez le script avec la commande souhaitée.

Pour voir toutes les commandes disponibles :

```shell
python challonge.py --help
```

### Lister les tournois

```shell
# challonge.py list [-h] [--date DATE] [--participants_count PARTICIPANTS_COUNT] [--short] [--fullurl] [--json [--full_json]]

# Lister les tournois
python challonge.py list
```

```text
+----------+---------+--------------------+--------------------------+--------------------------+
| URL      | Titre   | Type de tournoi    | Date de création         |   Nombre de participants |
+==========+=========+====================+==========================+==========================+
| bbkdcbam | Test 01 | single elimination | 2024-10-10 14:37:33 CEST |                        3 |
+----------+---------+--------------------+--------------------------+--------------------------+
```

```shell
# Liste les tournois au format JSON
python challonge.py list --json
```

```json
[
  {
    "url": "bbkdcbam",
    "full_url": "https://challonge.com/bbkdcbam",
    "title": "Test 01",
    "tournament_type": "single elimination",
    "created_at": "2024-10-10T14:37:33.902000+02:00",
    "participants_count": 3
  },
  {
    "url": "41bhwup4",
    "full_url": "https://challonge.com/41bhwup4",
    "title": "Test 12 teams",
    "tournament_type": "single elimination",
    "created_at": "2024-10-10T15:23:50.829000+02:00",
    "participants_count": 0
  }
]
```

```shell
# Liste les tournois au format JSON
python challonge.py list --json --full_json
```

```json
[
  {
    "url": "bbkdcbam",
    "full_url": "https://challonge.com/bbkdcbam",
    "title": "Test 01",
    "tournament_type": "single elimination",
    "created_at": "2024-10-10T14:37:33.902000+02:00",
    "participants_count": 3,
    "participants": [
      {
        "name": "Unreal x Marco",
        "seed": 1
      },
      {
        "name": "Druide x Klarika",
        "seed": 2
      },
      {
        "name": "vignemail1 x Hope",
        "seed": 3
      }
    ]
  },
  {
    "url": "41bhwup4",
    "full_url": "https://challonge.com/41bhwup4",
    "title": "Test 12 teams",
    "tournament_type": "single elimination",
    "created_at": "2024-10-10T15:23:50.829000+02:00",
    "participants_count": 0,
    "participants": []
  }
]
```

```shell
# Lister les tournois
python challonge.py list --fullurl
```

```text
+----------+---------+--------------------+--------------------------+--------------------------+--------------------------------+
| URL      | Titre   | Type de tournoi    | Date de création         |   Nombre de participants | URL complète                   |
+==========+=========+====================+==========================+==========================+================================+
| bbkdcbam | Test 01 | single elimination | 2024-10-10 14:37:33 CEST |                        3 | https://challonge.com/bbkdcbam |
+----------+---------+--------------------+--------------------------+--------------------------+--------------------------------+
```

```shell
# Lister les tournois depuis une date
python challonge.py list --date 2024-09-01
```

```text
+---------+--------------------+----------------------------+--------------------------+
| Titre   | Type de tournoi    | Date de création (Paris)   |   Nombre de participants |
+=========+====================+============================+==========================+
| Test 01 | single elimination | 2024-10-10 14:37:33 CEST   |                        0 |
+---------+--------------------+----------------------------+--------------------------+
```

```shell
python challonge.py list --short --date 2024-09-01
```

```text
bbkdcbam
```

### Supprimer les tournois

```shell
# usage: challonge.py delete [-h] (--date DATE | --urls URLS [URLS ...])

# Tous les tournois à partir d'une date
python challonge.py delete --date 2024-09-01
```

```text
2 tournois supprimés avec succès.
```

```shell
# Les tournois spécifiés par leur fin d'url
python challonge.py delete --urls bbkdcbam
```

### Créer un tournoi à élimination simple

```shell
# usage: challonge.py create_single [-h] --name NAME [--generate_participants GENERATE_PARTICIPANTS]
python challonge.py create_single --name "Switcharoo"
```

```text
Tournoi créé : https://challonge.com/bbkdcbam
Labels de tour personnalisés ajoutés.
```

```shell
python challonge.py create_single --name "Test 12 teams" --generate_participants 12
```

```text
Tournoi créé : https://challonge.com/41bhwup4
Labels de tour personnalisés ajoutés.
```

### Créer un tournoi à double élimination

```shell
# usage: challonge.py create_double [-h] --name NAME [--generate_participants GENERATE_PARTICIPANTS]
python challonge.py create_double --name "Switcharoo"
python challonge.py create_double --name "Test 8 teams" --generate_participants 8
```

### Ajouter des participants à un tournoi

```shell
# usage: challonge.py add_participants [-h] --tournament_id TOURNAMENT_ID --participants PARTICIPANTS [PARTICIPANTS ...]
python challonge.py add_participants --tournament_id bbkdcbam --participants "player1 x player2" "player3 x player4" "player5 x player6" "player7 x player8"
```

```text
Participants ajoutés avec succès.
```

### Supprimer tous les participants d'un tournoi

```shell
# usage: challonge.py remove_participants [-h] --tournament_id TOURNAMENT_ID
python challonge.py remove_participants --tournament_id bbkdcba
```

```text
Tous les participants ont été supprimés.
```

### Changer le type d'elimination d'un tournoi

```shell
# usage: challonge.py toggle_type [-h] --url URL
python challonge.py toggle_type --url bbkdcbam
```

```text
Le type du tournoi a été changé de single elimination à double elimination.
```

```shell
python challonge.py toggle_type --url bbkdcbam
```

```text
Le type du tournoi a été changé de double elimination à single elimination.
```

### Mélanger la liste des participants

```shell
# usage: challonge.py randomize [-h] --url URL
python challonge.py randomize --url bbkdcbam
```

```text
Les participants du tournoi ont été mélangés aléatoirement.
```
