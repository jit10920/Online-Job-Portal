# JobConnect — Online Job Portal

Project 43 for CSE 3206 Software Engineering Sessional.

The assigned scenario is **Online Job Portal** and the provided lab sheet recommends the **Spiral** process model for this project — see [`docs/PROCESS_MODEL.md`](docs/PROCESS_MODEL.md) for the full justification and cycle-by-cycle breakdown.

## Technology Stack

- Backend: Python + Flask
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask session + Werkzeug password hashing

## MVP Features

### Job Seekers
- Register/login
- Browse jobs
- Search by keyword and location
- Filter by job type
- View job details
- Apply with a cover letter
- Track application status
- Maintain a professional profile: headline, bio, location, skills, resume/
  LinkedIn/portfolio links, and a multi-entry work experience timeline

### Employers
- Register/login
- Post jobs
- Edit jobs
- Delete jobs
- View applications
- Change application status
- Maintain a company profile (name, website, size, description)
- Open an applicant's profile directly from the applications table

## Run Locally

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/WSL:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
python backend/app.py
```

Open:
`http://127.0.0.1:5000`

The SQLite database is created automatically at `instance/job_portal.db`.

## Suggested GitHub Team Workflow

Use three feature branches as required by the lab:

- `member1-auth`
- `member2-jobs`
- `member3-applications`

Each member should make meaningful commits, push the feature branch, open a Pull Request, review another member's PR, and merge through GitHub.

## Suggested Future Extensions

- Profile photo / avatar upload
- Admin dashboard
- Email notifications
- Saved jobs
- Pagination
- Advanced filtering
- Resume parsing
- Production database such as MySQL/PostgreSQL
