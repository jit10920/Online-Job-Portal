from flask import request, jsonify
import bcrypt
from models.user import create_user, get_user_by_email
from utils.auth import generate_token

def register():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    existing_user = get_user_by_email(data['email'])
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 409
        
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    role = data.get('role', 'seeker')
    
    if role not in ['seeker', 'employer']:
        return jsonify({'message': 'Invalid role'}), 400
        
    try:
        user_id = create_user(data['name'], data['email'], hashed_password, role)
        token = generate_token(user_id, role)
        return jsonify({'message': 'User created successfully', 'token': token, 'user': {'id': user_id, 'name': data['name'], 'email': data['email'], 'role': role}}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    user = get_user_by_email(data['email'])
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
        
    if bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
        token = generate_token(user['id'], user['role'])
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    return jsonify({'message': 'Invalid credentials'}), 401
