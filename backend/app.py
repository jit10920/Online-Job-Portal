import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------------------------
# Paths & App Config
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
INSTANCE_DIR = os.path.join(PROJECT_ROOT, 'instance')
DATABASE_PATH = os.path.join(INSTANCE_DIR, 'job_portal.db')
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)
app.secret_key = os.environ.get('SECRET_KEY', 'jobconnect-secret-key-cse3206-dev')


# -------------------------------------------------------------------
# Database Helpers
# -------------------------------------------------------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'job_seeker',
            headline TEXT,
            phone TEXT,
            location TEXT,
            bio TEXT,
            skills TEXT,
            resume_url TEXT,
            linkedin_url TEXT,
            portfolio_url TEXT,
            company_name TEXT,
            company_website TEXT,
            company_size TEXT,
            company_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL DEFAULT 'Full-time',
            salary TEXT,
            description TEXT NOT NULL,
            requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            applicant_id INTEGER NOT NULL,
            cover_letter TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            currently_working INTEGER DEFAULT 0,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # Seed demo data if database is empty
    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]
    if job_count == 0:
        emp_pwd = generate_password_hash('password123')
        cursor.execute("""
            INSERT INTO users (name, email, password, role, headline, company_name, company_website, company_size, company_description, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Sarah Jenkins',
            'employer@demo.com',
            emp_pwd,
            'employer',
            'Lead Talent Partner at TechFlow Innovations',
            'TechFlow Innovations',
            'https://techflow.io',
            '51-200',
            'Building cloud-native developer tools and AI productivity suites.',
            'San Francisco, CA / Remote'
        ))
        emp_id = cursor.lastrowid

        seeker_pwd = generate_password_hash('password123')
        cursor.execute("""
            INSERT INTO users (name, email, password, role, headline, phone, location, bio, skills, resume_url, linkedin_url, portfolio_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Alex Morgan',
            'seeker@demo.com',
            seeker_pwd,
            'job_seeker',
            'Full-Stack Software Engineer | Python, Flask, React, TypeScript',
            '+1 (555) 349-2810',
            'Austin, TX',
            'Passionate software engineer with 4+ years of experience building web applications, APIs, and scalable backends.',
            'Python, Flask, React, TypeScript, PostgreSQL, Docker, Git, REST APIs',
            'https://example.com/alex-resume.pdf',
            'https://linkedin.com/in/alexmorgan-demo',
            'https://alexmorgan.dev'
        ))
        seeker_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO experience (user_id, job_title, company, start_date, end_date, currently_working, description)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (seeker_id, 'Senior Frontend Developer', 'Nexus Digital Solutions', '2023-01', '', 'Leading UI architecture for micro-frontend systems.'))

        cursor.execute("""
            INSERT INTO experience (user_id, job_title, company, start_date, end_date, currently_working, description)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (seeker_id, 'Full-Stack Developer', 'CyberCraft Studio', '2021-03', '2022-12', 'Developed Flask REST APIs and responsive UI components.'))

        demo_jobs = [
            (
                emp_id,
                'Senior Full-Stack Engineer (Python & React)',
                'TechFlow Innovations',
                'Remote / New York, NY',
                'Full-time',
                '$120,000 - $150,000 USD',
                'We are seeking an experienced Full-Stack Engineer to architect, build, and maintain mission-critical cloud applications.',
                '• 4+ years software engineering experience\n• Strong Python (Flask/FastAPI) and JavaScript (React/TypeScript)\n• Solid understanding of relational databases\n• Experience with REST APIs'
            ),
            (
                emp_id,
                'Frontend UI/UX Developer',
                'DesignCraft Labs',
                'San Francisco, CA',
                'Full-time',
                '$95,000 - $125,000 USD',
                'Join our design-engineering team to create accessible, fluid web experiences from Figma designs.',
                '• Strong mastery of semantic HTML, modern CSS, and JavaScript\n• Keen eye for typography, spacing, and micro-interactions\n• Experience with responsive design across mobile, tablet, and desktop'
            ),
            (
                emp_id,
                'Junior Backend Developer Intern',
                'CloudSphere Technologies',
                'Remote',
                'Internship',
                '$25 - $35 / hour',
                'Great opportunity for graduating students or junior developers to gain hands-on experience building backend APIs and database models.',
                '• Knowledge of Python, SQL, or Node.js\n• Eagerness to learn clean code practices and Git workflows\n• Good communication and problem-solving skills'
            )
        ]
        for j in demo_jobs:
            cursor.execute("""
                INSERT INTO jobs (employer_id, title, company, location, job_type, salary, description, requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, j)

    conn.commit()
    conn.close()


# -------------------------------------------------------------------
# Auth Decorators
# -------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an employer.', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'employer':
            flash('This action is restricted to employer accounts.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def seeker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as a job seeker.', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'job_seeker':
            flash('This action is restricted to job seekers.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------------
# Core Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    db = get_db()
    jobs_list = db.execute(
        "SELECT * FROM jobs ORDER BY created_at DESC LIMIT 6"
    ).fetchall()
    return render_template('index.html', jobs=jobs_list)


@app.route('/jobs')
def jobs():
    db = get_db()
    q = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    job_type = request.args.get('job_type', '').strip()

    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if q:
        sql += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
        term = f"%{q}%"
        params.extend([term, term, term])

    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")

    if job_type:
        sql += " AND job_type = ?"
        params.append(job_type)

    sql += " ORDER BY created_at DESC"
    job_list = db.execute(sql, params).fetchall()

    return render_template('jobs.html', jobs=job_list, q=q, location=location, job_type=job_type)


@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    db = get_db()
    job = db.execute("""
        SELECT j.*, u.name AS employer_name, u.email AS employer_email
        FROM jobs j
        JOIN users u ON j.employer_id = u.id
        WHERE j.id = ?
    """, (job_id,)).fetchone()

    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('jobs'))

    return render_template('job_detail.html', job=job)


@app.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@seeker_required
def apply(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('jobs'))

    applicant_id = session['user_id']
    existing = db.execute(
        "SELECT id FROM applications WHERE job_id = ? AND applicant_id = ?",
        (job_id, applicant_id)
    ).fetchone()
    if existing:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '').strip()
        db.execute(
            "INSERT INTO applications (job_id, applicant_id, cover_letter, status) VALUES (?, ?, ?, 'Pending')",
            (job_id, applicant_id, cover_letter)
        )
        db.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('apply.html', job=job)


@app.route('/jobs/new', methods=['GET', 'POST'])
@employer_required
def create_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        salary = request.form.get('salary', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()

        if not title or not company or not location or not description:
            flash('Please fill in all required fields.', 'danger')
            return render_template('job_form.html', job=request.form)

        db = get_db()
        db.execute("""
            INSERT INTO jobs (employer_id, title, company, location, job_type, salary, description, requirements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], title, company, location, job_type, salary, description, requirements))
        db.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('job_form.html', job=None)


@app.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@employer_required
def edit_job(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ? AND employer_id = ?", (job_id, session['user_id'])).fetchone()
    if not job:
        flash('Job not found or access denied.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        salary = request.form.get('salary', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()

        if not title or not company or not location or not description:
            flash('Please fill in all required fields.', 'danger')
            return render_template('job_form.html', job=request.form)

        db.execute("""
            UPDATE jobs
            SET title = ?, company = ?, location = ?, job_type = ?, salary = ?, description = ?, requirements = ?
            WHERE id = ? AND employer_id = ?
        """, (title, company, location, job_type, salary, description, requirements, job_id, session['user_id']))
        db.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('job_form.html', job=job)


@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
@employer_required
def delete_job(job_id):
    db = get_db()
    db.execute("DELETE FROM jobs WHERE id = ? AND employer_id = ?", (job_id, session['user_id']))
    db.commit()
    flash('Job posting deleted.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']
    role = session.get('role')

    if role == 'employer':
        jobs = db.execute("SELECT * FROM jobs WHERE employer_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        applications = db.execute("""
            SELECT a.id, a.status, a.applied_at, a.applicant_id,
                   u.name AS applicant_name, u.email,
                   j.title, j.company
            FROM applications a
            JOIN users u ON a.applicant_id = u.id
            JOIN jobs j ON a.job_id = j.id
            WHERE j.employer_id = ?
            ORDER BY a.applied_at DESC
        """, (user_id,)).fetchall()
        return render_template('employer_dashboard.html', jobs=jobs, applications=applications)
    else:
        applications = db.execute("""
            SELECT a.id, a.status, a.applied_at,
                   j.title, j.company, j.location, j.id as job_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.applicant_id = ?
            ORDER BY a.applied_at DESC
        """, (user_id,)).fetchall()
        return render_template('seeker_dashboard.html', applications=applications)


@app.route('/applications/<int:application_id>/status', methods=['POST'])
@employer_required
def update_application(application_id):
    db = get_db()
    status = request.form.get('status')

    app_record = db.execute("""
        SELECT a.id FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.id = ? AND j.employer_id = ?
    """, (application_id, session['user_id'])).fetchone()

    if not app_record:
        flash('Application not found or unauthorized.', 'danger')
        return redirect(url_for('dashboard'))

    db.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
    db.commit()
    flash(f'Application status updated to {status}.', 'success')
    return redirect(url_for('dashboard'))


# -------------------------------------------------------------------
# Profile Routes
# -------------------------------------------------------------------
@app.route('/profile')
@login_required
def profile():
    return view_profile(session['user_id'])


@app.route('/users/<int:user_id>')
def view_profile(user_id):
    db = get_db()
    profile_user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not profile_user:
        flash('User profile not found.', 'danger')
        return redirect(url_for('index'))

    experience = db.execute(
        "SELECT * FROM experience WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

    is_own_profile = session.get('user_id') == user_id
    return render_template(
        'profile.html',
        profile_user=profile_user,
        experience=experience,
        is_own_profile=is_own_profile
    )


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db = get_db()
    user_id = session['user_id']
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        headline = request.form.get('headline', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        bio = request.form.get('bio', '').strip()

        if user['role'] == 'job_seeker':
            skills = request.form.get('skills', '').strip()
            resume_url = request.form.get('resume_url', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            portfolio_url = request.form.get('portfolio_url', '').strip()

            db.execute("""
                UPDATE users
                SET name = ?, headline = ?, phone = ?, location = ?, bio = ?,
                    skills = ?, resume_url = ?, linkedin_url = ?, portfolio_url = ?
                WHERE id = ?
            """, (name, headline, phone, location, bio, skills, resume_url, linkedin_url, portfolio_url, user_id))
        else:
            company_name = request.form.get('company_name', '').strip()
            company_website = request.form.get('company_website', '').strip()
            company_size = request.form.get('company_size', '').strip()
            company_description = request.form.get('company_description', '').strip()

            db.execute("""
                UPDATE users
                SET name = ?, headline = ?, phone = ?, location = ?, bio = ?,
                    company_name = ?, company_website = ?, company_size = ?, company_description = ?
                WHERE id = ?
            """, (name, headline, phone, location, bio, company_name, company_website, company_size, company_description, user_id))

        db.commit()
        session['name'] = name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    experience = db.execute("SELECT * FROM experience WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return render_template('profile_edit.html', user=user, experience=experience)


@app.route('/profile/experience/add', methods=['POST'])
@seeker_required
def add_experience():
    job_title = request.form.get('job_title', '').strip()
    company = request.form.get('company', '').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    currently_working = 1 if 'currently_working' in request.form else 0
    description = request.form.get('description', '').strip()

    if not job_title or not company:
        flash('Job title and company are required.', 'danger')
        return redirect(url_for('edit_profile'))

    db = get_db()
    db.execute("""
        INSERT INTO experience (user_id, job_title, company, start_date, end_date, currently_working, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session['user_id'], job_title, company, start_date, end_date, currently_working, description))
    db.commit()
    flash('Work experience added!', 'success')
    return redirect(url_for('edit_profile'))


@app.route('/profile/experience/<int:exp_id>/delete', methods=['POST'])
@seeker_required
def delete_experience(exp_id):
    db = get_db()
    db.execute("DELETE FROM experience WHERE id = ? AND user_id = ?", (exp_id, session['user_id']))
    db.commit()
    flash('Experience removed.', 'success')
    return redirect(url_for('edit_profile'))


# -------------------------------------------------------------------
# Auth Routes
# -------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'job_seeker')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if role not in ['job_seeker', 'employer']:
            role = 'job_seeker'

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        cursor = db.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, role))
        db.commit()

        session.clear()
        session['user_id'] = cursor.lastrowid
        session['name'] = name
        session['role'] = role
        session['email'] = email

        flash('Registration successful! Complete your profile to get started.', 'success')
        return redirect(url_for('edit_profile'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# -------------------------------------------------------------------
# Server Runner
# -------------------------------------------------------------------
if __name__ == '__main__':
    init_db()
    print("JobConnect server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
