import os
import sys
import json
from flask import Flask
from routes.home import page as home
from routes.details import page as details
from routes.episode import page as episode
from routes.health import page as health

SETTINGS_FILE = 'settings.json'

def prod():
    if getattr(sys, 'frozen', False):  
        return True
    else:
        return False

dev = prod()

print(f"Running in production mode: {dev}")

def load_settings():
    current_dir = os.getcwd()
    settings_path = os.path.join(current_dir, SETTINGS_FILE)

    if os.path.exists(settings_path):
        with open(settings_path, 'r') as file:
            return json.load(file)
    else:
        default_settings = {
            'path': '',
            'format': 'mp4',
            'language': 'en',
            'apiKey': ''
        }
        with open(settings_path, 'w') as file:
            json.dump(default_settings, file)
        print(f"Settings created on: {settings_path}")
        return default_settings
    
settings = load_settings()

def start_flask():
    print("""
      ,---.          ,--.                    ,--.              ,---.                                       
     /  O  \ ,--,--, `--',--,--,--. ,--,--.,-'  '-. ,---.     '   .-' ,---. ,--.--.,--.  ,--.,---. ,--.--. 
    |  .-.  ||      \,--.|        |' ,-.  |'-.  .-'| .-. :    `.  `-.| .-. :|  .--' \  `'  /| .-. :|  .--' 
    |  | |  ||  ||  ||  ||  |  |  |\ '-'  |  |  |  \   --.    .-'    \   --.|  |     \    / \   --.|  |    
    `--' `--'`--''--'`--'`--`--`--' `--`--'  `--'   `----'    `-----' `----'`--'      `--'   `----'`--'                                                                                                                                                           
    """)
    #sys.stdout = open(os.devnull, 'w')
    #sys.stderr = open(os.devnull, 'w')
    app.run(host='0.0.0.0', port=80, use_reloader=False)

if settings is not None and 'path' in settings:
    app = Flask(__name__,
        static_url_path='/public', 
        static_folder=settings['path']
    )
    app.register_blueprint(home.bp)
    app.register_blueprint(details.bp)
    app.register_blueprint(episode.bp)
    app.register_blueprint(health.bp)

    app.debug = False

    if __name__ == '__main__':
      start_flask()