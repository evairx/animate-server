import os
import sys
import json
from flask import Flask
from routes.home import page as home
from routes.details import page as details
from routes.episode import page as episode
from routes.health import page as health

SETTINGS_FILE = 'settings.json'

def load_settings():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(current_dir)
    settings_path = os.path.join(current_dir, SETTINGS_FILE)
    print(settings_path)
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as file:
            return json.load(file)
    return None

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