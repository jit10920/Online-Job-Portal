from flask import Blueprint
from controllers.application_controller import apply_for_job, list_user_applications, list_job_applications, change_application_status
from utils.auth import token_required, employer_required

application_bp = Blueprint('applications', __name__)

# Seeker routes
application_bp.route('/job/<int:job_id>', methods=['POST'])(token_required(apply_for_job))
application_bp.route('/me', methods=['GET'])(token_required(list_user_applications))

# Employer routes
application_bp.route('/job/<int:job_id>', methods=['GET'])(token_required(employer_required(list_job_applications)))
application_bp.route('/<int:application_id>/status', methods=['PUT'])(token_required(employer_required(change_application_status)))
