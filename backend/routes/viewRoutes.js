const express = require('express');
const { getAllJobs, getJobById } = require('../models/jobModel');
const { getApplicationsByUser, getApplicationsByJob } = require('../models/applicationModel');
const { verifyToken, optionalAuth, isEmployer } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/', optionalAuth, (req, res) => {
    res.render('index.html');
});

router.get('/login', (req, res) => {
    res.render('login.html');
});

const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { getUserByEmail, createUser } = require('../models/userModel');

router.post('/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        const user = await getUserByEmail(email);
        if (user && await bcrypt.compare(password, user.password_hash)) {
            const token = jwt.sign({ user_id: user.id, role: user.role, name: user.name }, process.env.JWT_SECRET || 'super-secret-key-change-me', { expiresIn: '1d' });
            res.cookie('token', token, { httpOnly: true });
            return res.redirect('/dashboard');
        }
        res.render('login.html', { error: 'Invalid credentials' });
    } catch(err) {
        res.render('login.html', { error: 'Server error' });
    }
});

router.get('/register', (req, res) => {
    res.render('register.html');
});

router.post('/register', async (req, res) => {
    const { name, email, password, role } = req.body;
    try {
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        const userRole = role === 'employer' ? 'employer' : 'seeker';
        const userId = await createUser(name, email, hashedPassword, userRole);
        const token = jwt.sign({ user_id: userId, role: userRole, name }, process.env.JWT_SECRET || 'super-secret-key-change-me', { expiresIn: '1d' });
        res.cookie('token', token, { httpOnly: true });
        res.redirect('/dashboard');
    } catch(err) {
        res.render('register.html', { error: 'Error registering' });
    }
});

router.get('/jobs', optionalAuth, async (req, res) => {
    const filters = {
        location: req.query.location,
        type: req.query.job_type,
        keyword: req.query.q
    };
    try {
        const jobs = await getAllJobs(filters);
        res.render('jobs.html', { jobs, q: req.query.q, location: req.query.location, job_type: req.query.job_type });
    } catch(err) {
        res.render('jobs.html', { jobs: [] });
    }
});

router.get('/jobs/:job_id', optionalAuth, async (req, res) => {
    try {
        const job = await getJobById(req.params.job_id);
        if (!job) return res.status(404).send('Not found');
        res.render('job_detail.html', { job });
    } catch(err) {
        res.status(500).send('Error');
    }
});

router.get('/apply/:job_id', verifyToken, async (req, res) => {
    try {
        const job = await getJobById(req.params.job_id);
        res.render('apply.html', { job });
    } catch(err) {
        res.status(500).send('Error');
    }
});

const { createApplication } = require('../models/applicationModel');
router.post('/apply/:job_id', verifyToken, async (req, res) => {
    if (req.user.role !== 'seeker') return res.redirect('/dashboard');
    try {
        await createApplication(req.params.job_id, req.user.user_id, req.body.resume_link);
        res.redirect('/dashboard');
    } catch(err) {
        res.status(500).send('Error applying');
    }
});

router.get('/dashboard', verifyToken, async (req, res) => {
    try {
        if (req.user.role === 'employer') {
            const jobs = await getAllJobs();
            const employerJobs = jobs.filter(j => j.employer_id === req.user.user_id);
            res.render('employer_dashboard.html', { jobs: employerJobs });
        } else {
            const applications = await getApplicationsByUser(req.user.user_id);
            res.render('seeker_dashboard.html', { applications });
        }
    } catch (err) {
        res.status(500).send('Error');
    }
});

router.get('/jobs/new', verifyToken, isEmployer, (req, res) => {
    res.render('job_form.html');
});

const { createJob } = require('../models/jobModel');
router.post('/jobs/new', verifyToken, isEmployer, async (req, res) => {
    const { title, company, description, requirements, salary, location, type } = req.body;
    try {
        await createJob(req.user.user_id, title, company, description, requirements, salary, location, type);
        res.redirect('/dashboard');
    } catch(err) {
        res.render('job_form.html', { error: 'Error creating job' });
    }
});

router.get('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/');
});

module.exports = router;
