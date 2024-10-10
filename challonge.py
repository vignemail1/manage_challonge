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

def delete_tournaments_from_date(date):
    tournaments = make_request('GET', 'tournaments')
    deleted_count = 0
    for tournament in tournaments:
        created_at = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at = created_at.astimezone(TIMEZONE)
        if created_at.date() >= date:
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


def create_tournament(name, tournament_type, game_name = 'Call of Duty: Warzone', generate_participants=0):
    data = {
        'tournament': {
            'name': name,
            'tournament_type': tournament_type,
            'game_name': game_name,
            'description': 'Created via API',
            'show_rounds': 'true',
            'private': 'false'
        }
    }
    response = make_request('POST', 'tournaments', data)
    print(f"Tournoi créé : {response['tournament']['full_challonge_url']}")
    
    if generate_participants > 0:
        generate_and_add_participants(response['tournament']['url'], generate_participants)
        
    return response['tournament']['id']

def add_participants(tournament_id, participants):
    data = {'participants': [{'name': p} for p in participants]}
    make_request('POST', f"tournaments/{tournament_id}/participants/bulk_add", data)
    print("Participants ajoutés avec succès.")

def remove_all_participants(tournament_id):
    participants = make_request('GET', f"tournaments/{tournament_id}/participants")
    for participant in participants:
        make_request('DELETE', f"tournaments/{tournament_id}/participants/{participant['participant']['id']}")
    print("Tous les participants ont été supprimés.")

def set_custom_round_labels(tournament_id):
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
    make_request('PUT', f"tournaments/{tournament_id}", data)
    print("Labels de tour personnalisés ajoutés.")

def list_tournaments(date=None, participants_count=None, short=False, full_url=False, json_output=False, full_json=False):
    tournaments = make_request('GET', 'tournaments')
    filtered_tournaments = []
    
    for tournament in tournaments:
        created_at_utc = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at_timezone = created_at_utc.astimezone(TIMEZONE)
        
        if (date is None or created_at_timezone.date() >= date) and \
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

def create_parser():
    parser = argparse.ArgumentParser(description="Gestion des tournois Challonge")
    parser.add_argument('--timezone', help="Fuseau horaire à utiliser (par défaut: celui spécifié dans .env ou Europe/Paris)")
    parser.add_argument("--game", help="Nom du jeu pour tous les tournois", default="Call of Duty: Warzone")
    subparsers = parser.add_subparsers(dest='action', required=True, help='Action à effectuer')

    # Commande : list
    list_parser = subparsers.add_parser('list', help='Lister les tournois')
    list_parser.add_argument('--date', help="Date (YYYY-MM-DD) à partir de laquelle lister les tournois")
    list_parser.add_argument('--participants_count', type=int, help="Filtrer par nombre de participants")
    list_parser.add_argument('--short', action='store_true', help="Afficher uniquement les URLs des tournois")
    list_parser.add_argument('--full_url', action='store_true', help="Ajouter l'URL complète en dernière colonne")
    list_parser.add_argument('--json', action='store_true', help="Sortie au format JSON")
    list_parser.add_argument('--full_json', action='store_true', help="Sortie JSON complète avec liste des participants")

    # Commande : delete
    delete_parser = subparsers.add_parser('delete', help='Supprimer les tournois')
    delete_group = delete_parser.add_mutually_exclusive_group(required=True)
    delete_group.add_argument('--date', help="Date (YYYY-MM-DD) à partir de laquelle supprimer les tournois")
    delete_group.add_argument('--urls', nargs='+', help="Liste des URLs des tournois à supprimer")

    # Commande : create_single
    create_single_parser = subparsers.add_parser('create_single', help='Créer un tournoi à élimination simple')
    create_single_parser.add_argument('--name', required=True, help="Nom du tournoi")
    create_single_parser.add_argument('--generate_participants', type=int, default=0, help="Nombre de participants à générer automatiquement")

    # Commande : create_double
    create_double_parser = subparsers.add_parser('create_double', help='Créer un tournoi à double élimination')
    create_double_parser.add_argument('--name', required=True, help="Nom du tournoi")
    create_double_parser.add_argument('--generate_participants', type=int, default=0, help="Nombre de participants à générer automatiquement")

    # Commande : add_participants
    add_participants_parser = subparsers.add_parser('add_participants', help='Ajouter des participants à un tournoi')
    add_participants_parser.add_argument('--tournament_id', required=True, help="ID du tournoi")
    add_participants_parser.add_argument('--participants', nargs='+', required=True, help="Liste des participants")

    # Commande : remove_participants
    remove_participants_parser = subparsers.add_parser('remove_participants', help='Supprimer tous les participants d\'un tournoi')
    remove_participants_parser.add_argument('--tournament_id', required=True, help="ID du tournoi")
    
    # Commande : toggle_type
    toggle_type_parser = subparsers.add_parser('toggle_type', help='Changer le type du tournoi (simple/double élimination)')
    toggle_type_parser.add_argument('--url', required=True, help="URL du tournoi")

    # Commande : randomize
    randomize_parser = subparsers.add_parser('randomize', help='Mélanger aléatoirement les participants')
    randomize_parser.add_argument('--url', required=True, help="URL du tournoi")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Configurer le fuseau horaire s'il est spécifié en ligne de commande
    global TIMEZONE
    if args.timezone:
        TIMEZONE = pytz.timezone(args.timezone)

    if args.action == 'list':
        date = datetime.fromisoformat(args.date).date() if args.date else None
        list_tournaments(date, args.participants_count, args.short, args.full_url, args.json, args.full_json)
    elif args.action == 'delete':
        if args.date:
            date = datetime.fromisoformat(args.date).date()
            delete_tournaments_from_date(date)
        elif args.urls:
            delete_tournaments_by_urls(args.urls)
    elif args.action in ['create_single', 'create_double']:
        tournament_type = 'single elimination' if args.action == 'create_single' else 'double elimination'
        tournament_url = create_tournament(args.name, tournament_type, args.game, args.generate_participants)
        set_custom_round_labels(tournament_url)
    elif args.action == 'add_participants':
        add_participants(args.tournament_id, args.participants)
    elif args.action == 'remove_participants':
        remove_all_participants(args.tournament_id)
    elif args.action == 'toggle_type':
        toggle_tournament_type(args.url)
    elif args.action == 'randomize':
        randomize_participants(args.url)

if __name__ == "__main__":
    main()
