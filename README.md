# Script de gestion des tournois Challonge

Ce script Python permet de gérer les tournois sur Challonge via leur API.

Avec ce script vous pouvez :

- créer un tournoi en single (winner only) ou double elimination (winner + loser brackets)
- ajouter des participants en paramètre et/ou depuis une plage d'une feuille Google Sheet
- supprimer tous les participants d'un tournoi
- supprimer des tournois
- lister vos tournois
- mélanger la liste des participants d'un tournoi
- voir le détail d'un tournoi

Avec ce script vous pouvez facilement envisager d'automatiser votre gestion de tournois jusqu'à programmer des touches de Stream Deck.

## Prérequis

- Python 3.8 ou supérieur (Python 3.12 recommandé)
- pipenv

## Installation de l'environnement python/pipenv

### Windows

#### Option 1 : python dans Windows

1. Installez Python depuis [python.org](https://www.python.org/downloads/windows/)
    - préférez la version 3.12 qui est la version testée sinon vous devrez ajuster le fichier `Pipfile` avec la version qui vous utilisez
2. Ouvrez PowerShell et exécutez :

    ```shell
    pip install pipenv
    ```

#### Option 2 : python via WSL2

Avec WSL2 vous pouvez tourner une VM de type Linux Ubuntu qui monte vos lecteurs Windows `C:\` (qui sera disponible en tant que `/mnt/c/`)... afin de rendre accessible vos fichiers Windows dans un contexte d'execution Linux. L'environnement Linux devient alors accessible dans votre terminal Powershell qui vous proposera d'ouvrir soit un terminal Powershell soit un terminal au sein de la VM Linux.

1. Installez WSL2 via PowerShell :
    1. Appuyer sur Windows + S pour ouvrir la barre de recherche
    2. Taper "Turn Windows features on or off"
    3. Parcourir les résultats de recherche et aller sur "Windows Subsystem for Linux (WSL)"
    4. Cliquer sur Ok
    5. Ouvrir un terminal Powershell en tant qu'administrateur
    6. Taper `wsl --install`
    7. Taper ensuite `wsl --set-default-version 2`
2. Installer une distribution Linux pour WSL2
   1. Ouvrir le store Microsoft
   2. Chercher "Ubuntu" et cliquer sur Install
   3. Lancer ensuite un terminal en choisissant un terminal de type Ubuntu
   4. Au premier lancement vous serez invité à créer un compte au sein du Linux

Maintenant que WSL2 et Ubuntu sont dispo, il vous suffit d'ouvrir un terminal Ubuntu pour avoir votre environnement qui démarre automatiquement.

Ensuite les instructions sont les mêmes que pour Linux (voir ci-dessous).

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

## Création d'un accès pour Google Sheet (fonction --import-gsheet)

1. Activer Google Sheets API:
    - Aller sur [Google Cloud Console](https://console.cloud.google.com/).
    - Créer un nouveau projet ou sélectionner un projet existant selon besoin.
    - Naviguer dans "APIs & Services" > "Bibliothèque".
    - Rechercher "Google Sheets API" et l'activer.
2. Créer un compte d'accès :
    - Aller dans "APIs & Services" > "Identités".
    - Cliquer "Créer une identité" et choisir "Compte de service".
    - Définir un nom et un identifiant unique de compte de service et cliquer sur Ok.
    - Une fois créé, aller dans la liste des comptes de service puis cliquer sur votre compte de service pour accéder à ses propriétés
    - Se rendre dans l'onglet Clés et créer une clé au format JSON. Une fois créée il vous faudra immédiatement télécharger le fichier `.json` et l'ajouter dans le dossier du projet.
        - c'est ce fichier JSON qu'il faudra renseigner dans le fichier `env.txt`.
3. Partagez votre Google Sheet:
    - Ouvrir Google Sheet.
    - Cliquez sur "Partage" et ajoutez l'email associé au compte de service nouvellement créé (vous pouvez le retrouver dans le fichier JSON) avec le rôle Lecteur (pas besoin de plus).

Voilà, vous avez créé un accès en lecture à votre Google Sheet via API pour que le script puisse faire une lecture de la plage à récupérer pour la fonction `--import-gsheet`.

## Configuration du script

1. Créez un fichier `env.txt` dans le même répertoire que le script
    - vous pouvez aussi par simplicité, dupliquer le fichier exemple `env.dist`en `env.txt` et éditer les valeurs dans `env.txt`
    - **attention** ne pas y mettre de caractères accentués dans le fichier `env.txt` car le module **_python-dotenv_** utilisé pour lire le fichier `env.txt` ne le supporte pas sous Windows.
2. Ajoutez votre clé API dans ce fichier :

   ```ini
   CHALLONGE_API_KEY=votre_clé_api_ici
   ```

3. (optionnel) Vous changez également la Timezone dans laquelle vous voulez la sortie des dates/heures en ajoutant dans `env.txt` :

    ```ini
    TIMEZONE=Europe/Paris
    ```

4. (optionnel) si vous souhaitez faire un import depuis un Google Sheet et que vous avez créer votre compte de service, ajoutez les éléments suivants dans le fichier `env.txt` :

    ```ini
    GOOGLE_APPLICATION_CREDENTIALS=nom_fichier_credential_service_account.json
    # pour un document d'url https://docs.google.com/spreadsheets/d/{{GOOGLE_SHEET_ID}}/edit?gid=0#gid=0
    GOOGLE_SHEET_ID={{GOOGLE_SHEET_ID}}
    GOOGLE_SHEET_WORKSHEET=feuille_dans_spreadsheet
    GOOGLE_SHEET_RANGE=plage_colonne_au_format_A2:A33
    ```

## Utilisation du script

Exécutez le script avec la commande souhaitée.

Avant toute exécution, il faut :

- soit se mettre dans l'environnement pipenv créé avec `pipenv shell` depuis le dossier du projet pour lancer directement des commandes `./challonge <command> [options]`
- soit préfixer par `pipenv run` (méthode ici documentée et recommandée surtout pour des appels depuis d'autres programmes)

Pour voir toutes les commandes disponibles :

```shell
pipenv run challonge --help
```

### Lister les tournois

```shell
# usage: challonge list [-h] [--start_date START_DATE] [--end_date END_DATE] [--participants_count PARTICIPANTS_COUNT] [--short] [--full_url] [--json] [--full_json] [--last]

# Lister les tournois
pipenv run challonge list
```

> ```text
> ╒══════════╤═════════╤════════════════════╤══════════════════════════╤══════════════════════╕
> │ url      │ title   │ tournament_type    │ created_at               │   participants_count │
> ╞══════════╪═════════╪════════════════════╪══════════════════════════╪══════════════════════╡
> │ pl888gdr │ double  │ double elimination │ 2024-10-12 14:25:26 CEST │                    0 │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┤
> │ sf901z3a │ single  │ single elimination │ 2024-10-12 14:21:30 CEST │                    0 │
> ╘══════════╧═════════╧════════════════════╧══════════════════════════╧══════════════════════╛
> ```

```shell
# Liste les tournois au format JSON
pipenv run challonge list --json
```

> ```json
> [
>   {
>     "url": "bbkdcbam",
>     "full_url": "https://challonge.com/bbkdcbam",
>     "title": "Test 01",
>     "tournament_type": "single elimination",
>     "created_at": "2024-10-10T14:37:33.902000+02:00",
>     "participants_count": 3
>   },
>   {
>     "url": "41bhwup4",
>     "full_url": "https://challonge.com/41bhwup4",
>     "title": "Test 12 teams",
>     "tournament_type": "single elimination",
>     "created_at": "2024-10-10T15:23:50.829000+02:00",
>     "participants_count": 0
>   }
> ]
> ```

```shell
# Liste les tournois au format JSON
pipenv run challonge list --json --full_json
```

> ```json
> [
>   {
>     "url": "bbkdcbam",
>     "full_url": "https://challonge.com/bbkdcbam",
>     "title": "Test 01",
>     "tournament_type": "single elimination",
>     "created_at": "2024-10-10T14:37:33.902000+02:00",
>     "participants_count": 3,
>     "participants": [
>       {
>         "name": "Player1 x Player2",
>         "seed": 1
>       },
>       {
>         "name": "Player3 x Player4",
>         "seed": 2
>       },
>       {
>         "name": "Player5 x Player6",
>         "seed": 3
>       }
>     ]
>   },
>   {
>     "url": "41bhwup4",
>     "full_url": "https://challonge.com/41bhwup4",
>     "title": "Test 12 teams",
>     "tournament_type": "single elimination",
>     "created_at": "2024-10-10T15:23:50.829000+02:00",
>     "participants_count": 0,
>     "participants": []
>   }
> ]
> ```

```shell
# Lister les tournois
pipenv run challonge list --full_url
```

> ```text
> ╒══════════╤═════════╤════════════════════╤══════════════════════════╤══════════════════════╤════════════════════════════════╕
> │ url      │ title   │ tournament_type    │ created_at               │   participants_count │ full_url                       │
> ╞══════════╪═════════╪════════════════════╪══════════════════════════╪══════════════════════╪════════════════════════════════╡
> │ sm52p3gu │ double  │ double elimination │ 2024-10-12 08:53:33 CEST │                    0 │ https://challonge.com/sm52p3gu │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ 3wz3067p │ double  │ double elimination │ 2024-10-12 08:53:31 CEST │                    0 │ https://challonge.com/3wz3067p │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ zqtm4ysb │ double  │ double elimination │ 2024-10-12 08:53:29 CEST │                    0 │ https://challonge.com/zqtm4ysb │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ b390sf18 │ double  │ double elimination │ 2024-10-12 08:53:26 CEST │                    0 │ https://challonge.com/b390sf18 │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ gb3fmyy9 │ double  │ double elimination │ 2024-10-12 08:53:24 CEST │                    0 │ https://challonge.com/gb3fmyy9 │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ jirous70 │ double  │ double elimination │ 2024-10-12 08:53:23 CEST │                    0 │ https://challonge.com/jirous70 │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ k0fkklld │ double  │ double elimination │ 2024-10-12 08:38:29 CEST │                    0 │ https://challonge.com/k0fkklld │
> ├──────────┼─────────┼────────────────────┼──────────────────────────┼──────────────────────┼────────────────────────────────┤
> │ gp527d34 │ test    │ single elimination │ 2024-10-11 22:21:44 CEST │                    0 │ https://challonge.com/gp527d34 │
> ╘══════════╧═════════╧════════════════════╧══════════════════════════╧══════════════════════╧════════════════════════════════╛
> ```

```shell
# Lister les tournois depuis une date
pipenv run challonge list --start_date 2024-09-01
```

> ```text
> ╒══════════╤═════════╤════════════════════╤══════════════════════════╤══════════════════════╕
> │ url      │ title   │ tournament_type    │ created_at               │   participants_count │
> ╞══════════╪═════════╪════════════════════╪══════════════════════════╪══════════════════════╡
> │ sf901z3a │ single  │ single elimination │ 2024-10-12 14:21:30 CEST │                    0 │
> ╘══════════╧═════════╧════════════════════╧══════════════════════════╧══════════════════════╛
> ```

```shell
pipenv run challonge list --short --start_date 2024-09-01
```

> ```text
> bbkdcbam
> ```

### Supprimer les tournois

```shell
# usage: challonge delete [-h] (--urls URLS [URLS ...] | --start_date START_DATE) [--end_date END_DATE]

# Tous les tournois à partir d'une date
pipenv run challonge delete --start_date 2024-09-01
```

> ```text
> 8 tournois supprimés avec succès.
> ```

```shell
# Les tournois spécifiés par leur fin d'url
pipenv run challonge delete --urls bbkdcbam
```

### Créer un tournoi à élimination simple

```shell
# usage: challonge create_single [-h] --name NAME [--generate_participants GENERATE_PARTICIPANTS]
pipenv run challonge create_single --name "Switcharoo"
```

> ```text
> Tournoi créé : https://challonge.com/bbkdcbam
> Labels de tour personnalisés ajoutés.
> ```

```shell
pipenv run challonge create_single --name "Test 12 teams" --generate_participants 12
```

> ```text
> Tournoi créé : https://challonge.com/41bhwup4
> Labels de tour personnalisés ajoutés.
> ```

### Créer un tournoi à double élimination

```shell
# usage: challonge create_double [-h] --name NAME [--generate_participants GENERATE_PARTICIPANTS]
pipenv run challonge create_double --name "Switcharoo"
pipenv run challonge create_double --name "Test 8 teams" --generate_participants 8
```

### Ajouter des participants à un tournoi

```shell
# usage: challonge add_participants [-h] --url URL [--participants [PARTICIPANTS ...]] [--import-gsheet] [--generate_participants GENERATE_PARTICIPANTS]

## Ajout manuel des participants
pipenv run challonge add_participants --url bbkdcbam --participants "player1 x player2" "player3 x player4" "player5 x player6" "player7 x player8"

## Ajout automatique depuis le google Sheet référencé
pipenv run challonge add_participants --url bbkdcbam --import-gsheet

# Ajout de 12 équipes au format TeamXXX
pipenv run challonge add_participants --url yg1rl9df --generate_participants 12
```

> ```text
> Participants ajoutés avec succès.
> ```

### Supprimer tous les participants d'un tournoi

```shell
# usage: challonge remove_participants [-h] (--url URL | --last) [--accept]
pipenv run challonge remove_participants --url bbkdcba
```

> ```text
> Tous les participants ont été supprimés.
> ```

```shell
# ou bien
pipenv run challonge remove_participants --last
```

> ```text
> ┌────────────────────────┬────────────────────────────────┐
> │ Champ                  │ Valeur                         │
> ├────────────────────────┼────────────────────────────────┤
> │ URL                    │ yg1rl9df                       │
> │ Nom                    │ test add                       │
> │ Type                   │ single elimination             │
> │ Jeu                    │ Call of Duty: Warzone          │
> │ Date de création       │ 2024-10-15 14:37:50 CEST       │
> │ Nombre de participants │ 12                             │
> │ État                   │ pending                        │
> │ URL complète           │ https://challonge.com/yg1rl9df │
> └────────────────────────┴────────────────────────────────┘
> 
> Participants:
> 1. Team001
> 2. Team002
> 3. Team003
> 4. Team004
> 5. Team005
> 6. Team006
> 7. Team007
> 8. Team008
> 9. Team009
> 10. Team010
> 11. Team011
> 12. Team012
> Utilisez l'option --accept pour confirmer la suppression des participants.
> ```

```shell
# ou bien
pipenv run challonge remove_participants --last --accept
```

> ```text
> ┌────────────────────────┬────────────────────────────────┐
> │ Champ                  │ Valeur                         │
> ├────────────────────────┼────────────────────────────────┤
> │ URL                    │ yg1rl9df                       │
> │ Nom                    │ test add                       │
> │ Type                   │ single elimination             │
> │ Jeu                    │ Call of Duty: Warzone          │
> │ Date de création       │ 2024-10-15 14:37:50 CEST       │
> │ Nombre de participants │ 12                             │
> │ État                   │ pending                        │
> │ URL complète           │ https://challonge.com/yg1rl9df │
> └────────────────────────┴────────────────────────────────┘
> 
> Participants:
> 1. Team001
> 2. Team002
> 3. Team003
> 4. Team004
> 5. Team005
> 6. Team006
> 7. Team007
> 8. Team008
> 9. Team009
> 10. Team010
> 11. Team011
> 12. Team012
> Tous les participants (12) ont été supprimés du tournoi yg1rl9df.
> ```

### Changer le type d'elimination d'un tournoi

```shell
# usage: challonge toggle_type [-h] --url URL
pipenv run challonge toggle_type --url bbkdcbam
```

> ```text
> Le type du tournoi a été changé de single elimination à double elimination.
> ```

```shell
pipenv run challonge toggle_type --url bbkdcbam
```

> ```text
> Le type du tournoi a été changé de double elimination à single elimination.
> ```

### Mélanger la liste des participants

```shell
# usage: challonge randomize [-h] --url URL
pipenv run challonge randomize --url bbkdcbam
```

> ```text
> Les participants du tournoi ont été mélangés aléatoirement.
> ```
