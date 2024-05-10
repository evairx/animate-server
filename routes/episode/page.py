import os
import json
import sys
import re
from flask import Blueprint, jsonify
import requests
from flask_cors import CORS

bp = Blueprint('episode', __name__)
CORS(bp, origins=["*"])

SETTINGS_FILE = 'settings.json'

def prod():
    if getattr(sys, 'frozen', False):  
        return True
    else:
        return False
    
dev = prod()

if dev:
    def load_settings():
        current_dir = os.getcwd()
        settings_path = os.path.join(current_dir, SETTINGS_FILE)

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as file:
                return json.load(file)
        return None
else:
    def load_settings():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        settings_path = os.path.join(root_dir, SETTINGS_FILE)
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as file:
                return json.load(file)
        return None

def get_episode_from_api(series_id, season_number, episode_number):
    try:
        settings = load_settings()
        api_key = settings['apiKey']
        
        id = re.search(r'\d+', series_id).group()

        episode_response = requests.get(f'https://api.themoviedb.org/3/tv/{id}/season/{season_number}/episode/{episode_number}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        episode_response.raise_for_status()
        episode_data = episode_response.json()
        # Fetching season data
        season_response = requests.get(f'https://api.themoviedb.org/3/tv/{id}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        season_response.raise_for_status()
        seasons_data = season_response.json()
        titleSerie = seasons_data['name'] 
        if not titleSerie:
            raise ValueError("Season name not found")
        data = {
            'episode_number': episode_data['episode_number'],
            'titleSerie': titleSerie,  # Añadiendo el nombre de la serie a los datos
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


def get_episode_file_path(settings, series_id, season_number, episode_number):
    if settings:
        movies_folder = settings.get("path", "")
        if movies_folder:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            folder_path = os.path.join(root_dir, movies_folder, series_id)
            if os.path.exists(folder_path):
                episode_folder = os.path.join(folder_path, f"season-{season_number}")
                if os.path.exists(episode_folder):
                    if settings['format'] == 'mp4':
                        for root, dirs, files in os.walk(episode_folder):
                            for file in files:
                                if file == f"{episode_number}.mp4":
                                    # Constructing the full file path including the folder hierarchy
                                    file_path = os.path.join(root, file)
                                    return file_path
                    elif settings['format'] == 'hls':
                        hls_folder = os.path.join(episode_folder, episode_number)
                        if os.path.exists(hls_folder):
                            hls_file = os.path.join(hls_folder, "output.m3u8")
                            if os.path.exists(hls_file):
                                return hls_file
                    elif settings['format'] == 'dash':
                        dash_folder = os.path.join(episode_folder, episode_number)
                        if os.path.exists(dash_folder):
                            dash_file = os.path.join(dash_folder, "output.mpd")
                            if os.path.exists(dash_file):
                                return dash_file
    return None

@bp.route('/<id>/<season>/<episode>', methods=['GET'])
def get_episode(id, season, episode):
    # Remove the "season-" prefix
    season_number = season.replace("season-", "")
    episode_info = get_episode_from_api(id, season_number, episode)
    if episode_info:
        settings = load_settings()
        episode_file_path = get_episode_file_path(settings, id, season_number, episode)
        if episode_file_path:
            # Construct the public link to the episode file based on the format
            if settings['format'] == 'mp4':
                public_link = f"public/{id}/{season}/{episode}.mp4"
            elif settings['format'] == 'hls':
                public_link = f"public/{id}/{season}/{episode}/output.m3u8"
            elif settings['format'] == 'dash':
                public_link = f"public/{id}/{season}/{episode}/output.mpd"
            episode_info['link'] = public_link
            return jsonify(episode_info)
        else:
            return jsonify({'error': 'El episodio no existe en la carpeta'}), 404
    else:
        return jsonify({'error': 'No se pudo obtener información del episodio'}), 500