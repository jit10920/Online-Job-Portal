from flask import request, jsonify
from models.job import create_job, get_all_jobs, get_job_by_id, update_job, delete_job

def post_job(current_user):
    data = request.get_json()
    required = ['title', 'company', 'description']
    if not data or not all(k in data for k in required):
        return jsonify({'message': 'Missing required fields'}), 400
        
    try:
        job_id = create_job(
            employer_id=current_user['user_id'],
            title=data['title'],
            company=data['company'],
            description=data['description'],
            requirements=data.get('requirements'),
            salary=data.get('salary'),
            location=data.get('location'),
            job_type=data.get('type', 'Full-time')
        )
        return jsonify({'message': 'Job posted successfully', 'job_id': job_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def list_jobs():
    filters = {
        'location': request.args.get('location'),
        'type': request.args.get('type'),
        'keyword': request.args.get('keyword')
    }
    try:
        jobs = get_all_jobs(filters)
        return jsonify({'jobs': jobs}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def get_job(job_id):
    try:
        job = get_job_by_id(job_id)
        if not job:
            return jsonify({'message': 'Job not found'}), 404
        return jsonify({'job': job}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def edit_job(current_user, job_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided for update'}), 400
        
    try:
        success = update_job(job_id, current_user['user_id'], **data)
        if success:
            return jsonify({'message': 'Job updated successfully'}), 200
        return jsonify({'message': 'Job not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def remove_job(current_user, job_id):
    try:
        success = delete_job(job_id, current_user['user_id'])
        if success:
            return jsonify({'message': 'Job deleted successfully'}), 200
        return jsonify({'message': 'Job not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
