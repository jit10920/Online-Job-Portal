from flask import Blueprint
from controllers.job_controller import post_job, list_jobs, get_job, edit_job, remove_job
from utils.auth import token_required, employer_required

job_bp = Blueprint('jobs', __name__)

job_bp.route('/', methods=['GET'])(list_jobs)
job_bp.route('/<int:job_id>', methods=['GET'])(get_job)

# Protected routes for employers
job_bp.route('/', methods=['POST'])(token_required(employer_required(post_job)))
job_bp.route('/<int:job_id>', methods=['PUT'])(token_required(employer_required(edit_job)))
job_bp.route('/<int:job_id>', methods=['DELETE'])(token_required(employer_required(remove_job)))
