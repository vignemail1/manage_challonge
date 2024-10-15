#!/usr/bin/env python3

import os
import sys
import argparse
import time
import pytz
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from tabulate import tabulate
import gspread
from google.oauth2.service_account import Credentials


# Charger le token API depuis le fichier .env
load_dotenv()
API_KEY = os.getenv('CHALLONGE_API_KEY')

BASE_URL = 'https://api.challonge.com/v1'

TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Europe/Paris'))

def make_request_with_retry(method, endpoint, data=None, params=None, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            response = make_request(method, endpoint, data, params)
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            print(f"Tentative {attempt + 1} échouée. Nouvelle tentative dans {delay} secondes...")
            time.sleep(delay)

def make_request(method, endpoint, data=None, params=None):
    url = f"{BASE_URL}/{endpoint}.json"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'YourApp/1.0'
    }
    
    if method == 'GET':
        if params is None:
            params = {}
        params['api_key'] = API_KEY
        response = requests.get(url, headers=headers, params=params)
    else:
        if data is None:
            data = {}
        data['api_key'] = API_KEY
        response = requests.request(method, url, headers=headers, json=data)
    
    response.raise_for_status()
    return response.json()

def import_participants_from_gsheet():
    # Load credentials from JSON key file
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), scopes=SCOPES)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    spreadsheet_id = os.getenv('GOOGLE_SHEET_ID', None)
    if spreadsheet_id is None:
        return []
    sheet_name = os.getenv('GOOGLE_SHEET_WORKSHEET')
    range_name = os.getenv('GOOGLE_SHEET_RANGE')
    
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(sheet_name)

    # Get all values from the specified range
    participants = worksheet.get(range_name)
    
    # Assuming participants are in a single column, return as a list of names
    return [row[0] for row in participants if row]

def delete_tournaments_from_date(start_date, end_date=None):
    tournaments = make_request('GET', 'tournaments')
    deleted_count = 0

    if end_date is None:
        end_date = datetime.now(TIMEZONE).date()

    for tournament in tournaments:
        created_at = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at = created_at.astimezone(TIMEZONE)
        
        if start_date <= created_at.date() <= end_date:
            make_request('DELETE', f"tournaments/{tournament['tournament']['id']}")
            deleted_count += 1

    print(f"{deleted_count} tournois supprimés avec succès.")



def delete_tournaments_by_urls(urls):
    deleted_count = 0
    for tournament_url in urls:
        try:
            make_request('DELETE', f"tournaments/{tournament_url}")
            deleted_count += 1
        except requests.exceptions.HTTPError as e:
            print(f"Erreur lors de la suppression du tournoi {tournament_url}: {e}")
    print(f"{deleted_count} tournois supprimés avec succès.")


def create_tournament(name, tournament_type, game_name='Call of Duty: Warzone', generate_participants=0, short=False):
    data = {
        'tournament': {
            'name': name,
            'tournament_type': tournament_type,
            'game_name': game_name,
            'description': 'Created via API',
            'show_rounds': 'true',
            'private': 'false',
            'quick_advance': 'true'
        }
    }
    response = make_request('POST', 'tournaments', data)
    if not short:
        print(f"Tournoi créé : {response['tournament']['full_challonge_url']}")
    
    if generate_participants > 0:
        generate_and_add_participants(response['tournament']['url'], generate_participants)
        
    return response['tournament']['url']

def add_participants(tournament_url, participants):
    data = {'participants': [{'name': p} for p in participants]}
    try:
        make_request('POST', f"tournaments/{tournament_url}/participants/bulk_add", data)
        print("Participants ajoutés avec succès.")
    except requests.HTTPError as e:
        print(f"Erreur d'import, possible qu'il y ait des doublons dans l'import ou avec les participants existant")
        print(json.dumps(data, indent=2))

def remove_all_participants(tournament_url):
    participants = make_request('GET', f"tournaments/{tournament_url}/participants")
    for participant in participants:
        make_request('DELETE', f"tournaments/{tournament_url}/participants/{participant['participant']['id']}")
    print("Tous les participants ont été supprimés.")

def set_custom_round_labels(tournament_url):
    data = {
        'tournament': {
            'custom_round_labels': [
                "Huitièmes de finale",
                "Quarts de finale",
                "Demi-finales",
                "Finale",
                "Grande Finale"
            ]
        }
    }
    make_request('PUT', f"tournaments/{tournament_url}", data)
    print("Labels de tour personnalisés ajoutés.")

def list_tournaments(start_date=None, end_date=None, participants_count=None, short=False, full_url=False, json_output=False, full_json=False):
    tournaments = make_request('GET', 'tournaments')
    filtered_tournaments = []

    if end_date is None:
        end_date = datetime.now(TIMEZONE).date()

    for tournament in tournaments:
        created_at_utc = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at_timezone = created_at_utc.astimezone(TIMEZONE)
        
        if (start_date is None or created_at_timezone.date() >= start_date) and \
           (created_at_timezone.date() <= end_date) and \
           (participants_count is None or tournament['tournament']['participants_count'] == participants_count):

            tournament_data = {
                'url': tournament['tournament']['url'],
                'full_url': tournament['tournament']['full_challonge_url'],
                'title': tournament['tournament']['name'],
                'tournament_type': tournament['tournament']['tournament_type'],
                'created_at': created_at_timezone.isoformat(),
                'participants_count': tournament['tournament']['participants_count']
            }
            
            if full_json:
                participants = make_request('GET', f"tournaments/{tournament['tournament']['url']}/participants")
                tournament_data['participants'] = [
                    {'name': p['participant']['name'], 'seed': p['participant']['seed']}
                    for p in participants
                ]
            
            if json_output:
                filtered_tournaments.append(tournament_data)
            elif short:
                filtered_tournaments.append(tournament['tournament']['url'])
            else:
                filtered_tournaments.append([
                    tournament['tournament']['url'],
                    tournament['tournament']['name'],
                    tournament['tournament']['tournament_type'],
                    created_at_timezone.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    tournament['tournament']['participants_count'],
                    tournament['tournament']['full_challonge_url'] if full_url else ''
                ])
    
    if json_output:
        print(json.dumps(filtered_tournaments, indent=2))
    elif short:
        print("\n".join(filtered_tournaments))
    elif filtered_tournaments:
        headers = ["URL", "Titre", "Type de tournoi", "Date de création", "Nombre de participants"]
        if full_url:
            headers.append("URL complète")
        print(tabulate(filtered_tournaments, headers=headers, tablefmt="grid"))
    else:
        print("Aucun tournoi trouvé correspondant aux critères spécifiés.")

def toggle_tournament_type(tournament_url):
    tournament = make_request('GET', f"tournaments/{tournament_url}")
    current_type = tournament['tournament']['tournament_type']
    new_type = 'double elimination' if current_type == 'single elimination' else 'single elimination'
    
    data = {
        'tournament': {
            'tournament_type': new_type
        }
    }
    
    make_request('PUT', f"tournaments/{tournament_url}", data)
    print(f"Le type du tournoi a été changé de {current_type} à {new_type}.")

def randomize_participants(tournament_url):
    make_request('POST', f"tournaments/{tournament_url}/participants/randomize")
    print("Les participants du tournoi ont été mélangés aléatoirement.")

def generate_and_add_participants(tournament_url, count):
    participants = [f"Team{i:03d}" for i in range(1, count + 1)]
    data = {'participants': [{'name': p} for p in participants]}
    make_request('POST', f"tournaments/{tournament_url}/participants/bulk_add", data)
    print(f"{count} participants générés et ajoutés au tournoi.")
    
def show_tournament(tournament_url, json_output=False, full_json=False):
    tournament = make_request('GET', f"tournaments/{tournament_url}")
    participants = make_request('GET', f"tournaments/{tournament_url}/participants")
    
    if full_json:
        # Retourner toutes les informations brutes de l'API
        full_data = {
            'tournament': tournament['tournament'],
            'participants': [p['participant'] for p in participants]
        }
        print(json.dumps(full_data, indent=2, ensure_ascii=False))
        return

    tournament_data = tournament['tournament']
    created_at = datetime.fromisoformat(tournament_data['created_at'].replace('Z', '+00:00')).astimezone(TIMEZONE)
    
    details = {
        'URL': tournament_data['url'],
        'Nom': tournament_data['name'],
        'Type': tournament_data['tournament_type'],
        'Jeu': tournament_data['game_name'],
        'Date de création': created_at.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'Nombre de participants': tournament_data['participants_count'],
        'État': tournament_data['state'],
        'URL complète': tournament_data['full_challonge_url'],
        'Participants': [p['participant']['name'] for p in participants]
    }
    
    if json_output:
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        headers = ['Champ', 'Valeur']
        table_data = [[k, v] for k, v in details.items() if k != 'Participants']
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        print("\nParticipants:")
        for i, participant in enumerate(details['Participants'], 1):
            print(f"{i}. {participant}")

def create_parser():
    parser = argparse.ArgumentParser(description="Gestion des tournois Challonge", epilog="Pour une full URL https://challonge.com/lnacodz7 , url : lnacodz7""")
    parser.add_argument('--timezone', help="Fuseau horaire à utiliser (par défaut: celui spécifié dans .env ou 'Europe/Paris')")
    parser.add_argument("--game", help="Nom du jeu pour tous les tournois", default="Call of Duty: Warzone")
    subparsers = parser.add_subparsers(dest='action', required=True, help='Action à effectuer')

    # Commande : list
    list_parser = subparsers.add_parser('list', help='Lister les tournois')
    list_parser.add_argument('--start_date', help="Date (YYYY-MM-DD) à partir de laquelle lister les tournois")
    list_parser.add_argument('--end_date', required=False, help="Date (YYYY-MM-DD) jusqu'à laquelle lister les tournois (par défaut: maintenant)")
    list_parser.add_argument('--participants_count', type=int, help="Filtrer par nombre de participants")
    list_parser.add_argument('--short', action='store_true', help="Afficher uniquement les URLs des tournois")
    list_parser.add_argument('--full_url', action='store_true', help="Ajouter l'URL complète en dernière colonne")
    list_parser.add_argument('--json', action='store_true', help="Sortie au format JSON")
    list_parser.add_argument('--full_json', action='store_true', help="Sortie JSON complète avec liste des participants")

    # Commande : delete
    delete_parser = subparsers.add_parser('delete', help='Supprimer les tournois')
    delete_group = delete_parser.add_mutually_exclusive_group(required=True)
    delete_group.add_argument('--urls', nargs='+', help="Liste des URLs des tournois à supprimer")
    date_group = delete_group.add_argument_group()
    date_group.add_argument('--start_date', help="Date de début (YYYY-MM-DD) à partir de laquelle supprimer les tournois")
    date_group.add_argument('--end_date', required=False, help="Date de fin (YYYY-MM-DD) jusqu'à laquelle supprimer les tournois (optionnel)")

    # Commande : create_single
    create_single_parser = subparsers.add_parser('create_single', help='Créer un tournoi à élimination simple')
    create_single_parser.add_argument('--name', required=True, help="Nom du tournoi")
    create_single_parser.add_argument('--generate_participants', type=int, default=0, help="Nombre de participants à générer automatiquement")
    create_single_parser.add_argument('--short', action='store_true', help="Afficher uniquement l'URL du tournoi créé")

    # Commande : create_double
    create_double_parser = subparsers.add_parser('create_double', help='Créer un tournoi à double élimination')
    create_double_parser.add_argument('--name', required=True, help="Nom du tournoi")
    create_double_parser.add_argument('--generate_participants', type=int, default=0, help="Nombre de participants à générer automatiquement")
    create_double_parser.add_argument('--short', action='store_true', help="Afficher uniquement l'URL du tournoi créé")

    # Commande : add_participants
    add_participants_parser = subparsers.add_parser('add_participants', help='Ajouter des participants à un tournoi')
    add_participants_parser.add_argument('--url', required=True, help="url du tournoi")
    add_participants_parser.add_argument('--participants', nargs='+', required=False, help="Liste des participants")
    add_participants_parser.add_argument('--import-gsheet', action='store_true', help="Importer la liste des participants depuis un Google Sheet")

    # Commande : remove_participants
    remove_participants_parser = subparsers.add_parser('remove_participants', help='Supprimer tous les participants d\'un tournoi')
    remove_participants_parser.add_argument('--url', required=True, help="url du tournoi")
    
    # Commande : toggle_type
    toggle_type_parser = subparsers.add_parser('toggle_type', help='Changer le type du tournoi (simple/double élimination)')
    toggle_type_parser.add_argument('--url', required=True, help="URL du tournoi")

    # Commande : randomize
    randomize_parser = subparsers.add_parser('randomize', help='Mélanger aléatoirement les participants')
    randomize_parser.add_argument('--url', required=True, help="URL du tournoi")
    
    # Commande : show
    show_parser = subparsers.add_parser('show', help='Afficher les détails d\'un tournoi')
    show_parser.add_argument('--url', required=True, help="URL du tournoi")
    show_parser.add_argument('--json', action='store_true', help="Sortie au format JSON")
    show_parser.add_argument('--full_json', action='store_true', help="Sortie JSON complète avec toutes les informations de l'API")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Configurer le fuseau horaire s'il est spécifié en ligne de commande
    global TIMEZONE
    if args.timezone:
        TIMEZONE = pytz.timezone(args.timezone)

    if args.action == 'list':
        start_date = datetime.fromisoformat(args.start_date).date() if args.start_date else None
        end_date = datetime.fromisoformat(args.end_date).date() if args.end_date else None
        list_tournaments(start_date, end_date, args.participants_count, args.short, args.full_url, args.json, args.full_json)
    elif args.action == 'delete':
        if args.start_date:
            start_date = datetime.fromisoformat(args.start_date).date()
            end_date = datetime.fromisoformat(args.end_date).date() if args.end_date else None
            delete_tournaments_from_date(start_date, end_date)
        elif args.urls:
            delete_tournaments_by_urls(args.urls)
    elif args.action in ['create_single', 'create_double']:
        tournament_type = 'single elimination' if args.action == 'create_single' else 'double elimination'
        tournament_url = create_tournament(args.name, tournament_type, args.game, args.generate_participants, args.short)
        if args.short:
            print(tournament_url)
        else:
            set_custom_round_labels(tournament_url)
    elif args.action == 'add_participants':
        participants = args.participants if args.participants else []
        
        if args.import_gsheet:
            gsheet_participants = import_participants_from_gsheet()
            participants.extend(gsheet_participants)

        if not participants:
            print("Aucun participant spécifié.")
            return
        
        add_participants(args.url, participants)
    elif args.action == 'remove_participants':
        remove_all_participants(args.url)
    elif args.action == 'toggle_type':
        toggle_tournament_type(args.url)
    elif args.action == 'randomize':
        randomize_participants(args.url)
    elif args.action == 'show':
        show_tournament(args.url, args.json, args.full_json)

if __name__ == "__main__":
    main()
