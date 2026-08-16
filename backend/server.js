const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const nunjucks = require('nunjucks');
const cookieParser = require('cookie-parser');
const path = require('path');

dotenv.config();

const authRoutes = require('./routes/authRoutes');
const jobRoutes = require('./routes/jobRoutes');
const applicationRoutes = require('./routes/applicationRoutes');
const viewRoutes = require('./routes/viewRoutes');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Static files
app.use('/static', express.static(path.join(__dirname, '../static')));

// Nunjucks Configuration
const env = nunjucks.configure(path.join(__dirname, '../templates'), {
    autoescape: true,
    express: app
});

// Polyfill url_for for Jinja compatibility
env.addGlobal('url_for', function(endpoint, params) {
    // Basic mapping for Jinja url_for to Express paths
    const routes = {
        'static': '/static/' + (params ? params.filename : ''),
        'index': '/',
        'jobs': '/jobs',
        'login': '/login',
        'register': '/register',
        'dashboard': '/dashboard',
        'create_job': '/jobs/new',
        'profile': '/profile',
        'logout': '/logout',
        'job_detail': params ? `/jobs/${params.job_id}` : '',
        'apply': params ? `/apply/${params.job_id}` : '',
        'view_profile': params ? `/profile/${params.user_id}` : ''
    };
    return routes[endpoint] || '#';
});

// Pass session to templates
app.use((req, res, next) => {
    // Extract token to populate session global
    let token = req.cookies?.token;
    if (token) {
        try {
            const jwt = require('jsonwebtoken');
            const decoded = jwt.verify(token, process.env.JWT_SECRET || 'super-secret-key-change-me');
            res.locals.session = {
                user_id: decoded.user_id,
                role: decoded.role,
                name: decoded.name || 'User',
                get: function(key, defaultVal) { return this[key] !== undefined ? this[key] : defaultVal; }
            };
        } catch(e) {
            res.locals.session = { get: function(key, defaultVal) { return defaultVal; } };
        }
    } else {
        res.locals.session = { get: function(key, defaultVal) { return defaultVal; } };
    }
    
    env.addGlobal('get_flashed_messages', () => []);
    next();
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/jobs', jobRoutes);
app.use('/api/applications', applicationRoutes);

// View Routes
app.use('/', viewRoutes);

// 404 Handler
app.use((req, res, next) => {
  res.status(404).send('Resource not found');
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
