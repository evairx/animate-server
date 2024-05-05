import os
import json
from flask import Blueprint, request, jsonify
import requests
from flask_cors import CORS
import re

bp = Blueprint('details', __name__)
CORS(bp, origins=["*"])

SETTINGS_FILE = 'settings.json'

def load_settings():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    settings_path = os.path.join(root_dir, SETTINGS_FILE)
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as file:
            return json.load(file)
    return None

def get_movies_folder():
    settings = load_settings()
    if settings:
        folder_path = settings.get("path", "")
        if folder_path:
            return folder_path
    return None

def get_episode_from_api(series_id, season_number, episode_number):
    try:
        settings = load_settings()
        api_key = settings['apiKey']
        
        id = re.search(r'\d+', series_id).group()
        response = requests.get(f'https://api.themoviedb.org/3/tv/{id}/season/{season_number}/episode/{episode_number}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        response.raise_for_status()
        episode_data = response.json()
        data = {
            'episode_number': episode_data['episode_number'],
            'name': episode_data['name'],
            'overview': episode_data['overview'],
            'still_path': f"https://image.tmdb.org/t/p/original{episode_data['still_path']}",
            'date': episode_data['air_date'],
            'runtime': episode_data['runtime']
        }
        return data
    except requests.RequestException as e:
        print(f"Error al obtener información del episodio: {str(e)}")
        return None
    
def get_season(series_id, season_number):
    try:
        settings = load_settings()
        api_key = settings['apiKey']
        
        id = re.search(r'\d+', series_id).group()
        if settings["language"] == "es":
            response = requests.get(f'https://api.themoviedb.org/3/tv/{id}/season/{season_number}?language=en',
                        headers={'Authorization': f'Bearer {api_key}'})
        else:
            response = requests.get(f'https://api.themoviedb.org/3/tv/{id}/season/{season_number}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        response.raise_for_status()
        movie_data = response.json()
        name = movie_data['name']

        if settings["language"] == "es":
            if name == "Specials":
                name = "Especiales"
            elif "Season" in name:
                season_number = name.split(" ")[-1]
                name = f"Temporada {season_number}"
                
        return name
    except requests.RequestException as e:
        print(f"Error al obtener información de la API para {series_id}: {str(e)}")
        return None
    
def get_data_details(item_name):
    try:
        settings = load_settings()
        api_key = settings['apiKey']
        
        # Extracting only the number from the item_name (folder name)
        item_number = re.search(r'\d+', item_name).group()
        
        response = requests.get(f'https://api.themoviedb.org/3/tv/{item_number}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        response.raise_for_status()
        movie_data = response.json()
        return {
            'name': movie_data['name'],
            'poster': f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}",
            "backdrop": f"https://image.tmdb.org/t/p/original{movie_data['backdrop_path']}",
            'overview': movie_data['overview'],
            'folder': item_name
        }
    except requests.RequestException as e:
        print(f"Error al obtener información de la API para {item_name}: {str(e)}")
        return {"error": "No se pudo obtener información."}

@bp.route('/<id>', methods=['GET'])
def details(id):
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    elif request.method == 'GET':
        try:
            movies_folder = get_movies_folder()
            if movies_folder:
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                folder_path = os.path.join(root_dir, movies_folder, id)
                if not os.path.exists(folder_path):
                    return jsonify({'error': 'La carpeta con el ID proporcionado no existe'}), 500

                settings = load_settings()
                if settings and settings['format'] == 'mp4':
                    seasons = []
                    for item in os.listdir(folder_path):
                        if os.path.isdir(os.path.join(folder_path, item)) and item.startswith('season-'):
                            season_number = item.split('-')[-1]
                            season_name = get_season(id, season_number)
                            season_info = {
                                'name': f'{season_name}',
                                'season_number': int(season_number),
                            }
                            episodes = []
                            season_folder = os.path.join(folder_path, item)
                            for episode_file in os.listdir(season_folder):
                                if episode_file.endswith('.mp4'):
                                    episode_number = os.path.splitext(episode_file)[0]
                                    episode_info = get_episode_from_api(id, season_number, int(episode_number))
                                    episodes.append(episode_info)
                            if episodes:
                                # Ordenar los episodios por número de episodio
                                episodes = sorted(episodes, key=lambda e: e['episode_number'])
                                season_info['episodes'] = episodes
                                seasons.append(season_info)
                else:
                    seasons = []
                    for item in os.listdir(folder_path):
                        if os.path.isdir(os.path.join(folder_path, item)) and item.startswith('season-'):
                            season_number = item.split('-')[-1]
                            season_name = get_season(id, season_number)
                            season_info = {
                                'name': f'{season_name}',
                                'season_number': int(season_number),
                            }
                            episodes = []
                            season_folder = os.path.join(folder_path, item)
                            for episode_folder in os.listdir(season_folder):
                                episode_path = os.path.join(season_folder, episode_folder)
                                if os.path.isdir(episode_path) and episode_folder.isdigit() and int(episode_folder) > 0:
                                    episode_info = get_episode_from_api(id, season_number, int(episode_folder))
                                    if episode_info:
                                        episodes.append(episode_info)
                            if episodes:
                                # Ordenar los episodios por número de episodio
                                episodes = sorted(episodes, key=lambda e: e['episode_number'])
                                season_info['episodes'] = episodes
                                seasons.append(season_info)

                movie_info = get_data_details(id)
                movie_info['seasons'] = seasons

                return jsonify(movie_info), 200
            else:
                return jsonify({'error': 'El archivo de configuración settings.json no está configurado correctamente'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'POST':
        return jsonify({'error': "method not allowed"}), 400