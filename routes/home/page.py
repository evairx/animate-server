import os
import json
import re
from flask import Blueprint, request, jsonify
import requests
from flask_cors import CORS

bp = Blueprint('home', __name__)
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

def get_data(item_name):
    try:
        settings = load_settings()
        api_key = settings['apiKey']
        
        # Extracting only the number from the folder name
        folder_number = re.search(r'\d+', item_name).group()

        print(folder_number)
        
        response = requests.get(f'https://api.themoviedb.org/3/tv/{folder_number}?language={settings["language"]}',
                        headers={'Authorization': f'Bearer {api_key}'})
        response.raise_for_status()
        movie_data = response.json()
        return {
            'name': movie_data['name'],
            'poster': f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}",
            'id': movie_data['id'],
            'folder': item_name
        }
    except requests.RequestException as e:
        print(f"Error al obtener información de la API para {item_name}: {str(e)}")
        return {"error": "No se pudo obtener información."}

@bp.route('/', methods=['POST', 'GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    elif request.method == 'GET':
        movies_folder = get_movies_folder()
        if movies_folder:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            folder_path = os.path.join(root_dir, movies_folder)
            try:
                files = os.listdir(folder_path)
                folders_and_videos = [file for file in files if os.path.isdir(os.path.join(folder_path, file)) or file.endswith('.mp4')]
                movie_info = [get_data(os.path.splitext(item)[0]) for item in folders_and_videos]
                return jsonify(movie_info), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'El archivo de configuración settings.json no está configurado correctamente'}), 500

    elif request.method == 'POST':
        return jsonify({'error': "method not allowed"}), 400