from flask import request, jsonify
from models.application import create_application, get_applications_by_user, get_applications_by_job, update_application_status

def apply_for_job(current_user, job_id):
    if current_user['role'] != 'seeker':
        return jsonify({'message': 'Only seekers can apply for jobs'}), 403
        
    data = request.get_json() or {}
    try:
        app_id = create_application(
            job_id=job_id,
            user_id=current_user['user_id'],
            resume_link=data.get('resume_link')
        )
        return jsonify({'message': 'Application submitted successfully', 'application_id': app_id}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def list_user_applications(current_user):
    try:
        applications = get_applications_by_user(current_user['user_id'])
        return jsonify({'applications': applications}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def list_job_applications(current_user, job_id):
    try:
        applications = get_applications_by_job(job_id, current_user['user_id'])
        return jsonify({'applications': applications}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def change_application_status(current_user, application_id):
    data = request.get_json()
    if not data or not data.get('status'):
        return jsonify({'message': 'Status is required'}), 400
        
    valid_statuses = ['pending', 'reviewed', 'accepted', 'rejected']
    if data['status'] not in valid_statuses:
        return jsonify({'message': 'Invalid status'}), 400
        
    try:
        success = update_application_status(
            application_id=application_id,
            employer_id=current_user['user_id'],
            status=data['status']
        )
        if success:
            return jsonify({'message': 'Application status updated successfully'}), 200
        return jsonify({'message': 'Application not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
