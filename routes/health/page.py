from flask import Blueprint, request,jsonify
from flask_cors import CORS

bp = Blueprint('health', __name__)
CORS(bp, origins=["*"])

@bp.route('/health', methods=['POST', 'GET', 'OPTIONS'])
def verify():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    elif request.method == 'GET':
        return jsonify('ok'), 200
    elif request.method == 'POST':
        return jsonify({'error': "method not allowed"}), 400