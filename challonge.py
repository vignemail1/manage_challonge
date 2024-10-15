#!/usr/bin/env python3

import os
import sys
import argparse
import time
import pytz
from datetime import datetime
import requests
from dotenv import load_dotenv
from tabulate import tabulate

# Charger le token API depuis le fichier .env
load_dotenv()
API_KEY = os.getenv('CHALLONGE_API_KEY')

BASE_URL = 'https://api.challonge.com/v1'

paris_tz = pytz.timezone('Europe/Paris')



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
    for tournament in tournaments:
        created_at = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at = created_at.astimezone(paris_tz)
        if created_at.date() >= date:
            make_request('DELETE', f"tournaments/{tournament['tournament']['id']}")
    print("Tournois supprimés avec succès.")


def create_tournament(name, tournament_type):
    data = {
        'tournament': {
            'name': name,
            'tournament_type': tournament_type,
            'game_name': 'Call of Duty: Warzone',
            'description': 'Created via API',
            'show_rounds': 'true',
            'private': 'false'
        }
    }
    response = make_request('POST', 'tournaments', data)
    print(f"Tournoi créé : {response['tournament']['full_challonge_url']}")
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

def list_tournaments(date=None, participants_count=None):
    tournaments = make_request('GET', 'tournaments')
    filtered_tournaments = []
    
    for tournament in tournaments:
        created_at_utc = datetime.fromisoformat(tournament['tournament']['created_at'].replace('Z', '+00:00'))
        created_at_paris = created_at_utc.astimezone(paris_tz)
        
        if (date is None or created_at_paris.date() >= date) and \
           (participants_count is None or tournament['tournament']['participants_count'] == participants_count):
            filtered_tournaments.append([
                tournament['tournament']['name'],
                tournament['tournament']['tournament_type'],
                created_at_paris.strftime('%Y-%m-%d %H:%M:%S %Z'),
                tournament['tournament']['participants_count']
            ])
    
    if filtered_tournaments:
        headers = ["Titre", "Type de tournoi", "Date de création (Paris)", "Nombre de participants"]
        print(tabulate(filtered_tournaments, headers=headers, tablefmt="grid"))
    else:
        print("Aucun tournoi trouvé correspondant aux critères spécifiés.")

def create_parser():
    parser = argparse.ArgumentParser(description="Gestion des tournois Challonge")
    subparsers = parser.add_subparsers(dest='action', required=True, help='Action à effectuer')

    # Commande : list
    list_parser = subparsers.add_parser('list', help='Lister les tournois')
    list_parser.add_argument('--date', help="Date (YYYY-MM-DD) à partir de laquelle lister les tournois")
    list_parser.add_argument('--participants_count', type=int, help="Filtrer par nombre de participants")

    # Commande : delete
    delete_parser = subparsers.add_parser('delete', help='Supprimer les tournois')
    delete_parser.add_argument('--date', required=True, help="Date (YYYY-MM-DD) à partir de laquelle supprimer les tournois")

    # Commande : create_single
    create_single_parser = subparsers.add_parser('create_single', help='Créer un tournoi à élimination simple')
    create_single_parser.add_argument('--name', required=True, help="Nom du tournoi")

    # Commande : create_double
    create_double_parser = subparsers.add_parser('create_double', help='Créer un tournoi à double élimination')
    create_double_parser.add_argument('--name', required=True, help="Nom du tournoi")

    # Commande : add_participants
    add_participants_parser = subparsers.add_parser('add_participants', help='Ajouter des participants à un tournoi')
    add_participants_parser.add_argument('--tournament_id', required=True, help="ID du tournoi")
    add_participants_parser.add_argument('--participants', nargs='+', required=True, help="Liste des participants")

    # Commande : remove_participants
    remove_participants_parser = subparsers.add_parser('remove_participants', help='Supprimer tous les participants d\'un tournoi')
    remove_participants_parser.add_argument('--tournament_id', required=True, help="ID du tournoi")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.action == 'list':
        date = datetime.fromisoformat(args.date).date() if args.date else None
        list_tournaments(date, args.participants_count)
    elif args.action == 'delete':
        date = datetime.fromisoformat(args.date).date()
        delete_tournaments_from_date(date)
    elif args.action in ['create_single', 'create_double']:
        tournament_type = 'single elimination' if args.action == 'create_single' else 'double elimination'
        tournament_id = create_tournament(args.name, tournament_type)
        set_custom_round_labels(tournament_id)
    elif args.action == 'add_participants':
        add_participants(args.tournament_id, args.participants)
    elif args.action == 'remove_participants':
        remove_all_participants(args.tournament_id)

if __name__ == "__main__":
    main()
