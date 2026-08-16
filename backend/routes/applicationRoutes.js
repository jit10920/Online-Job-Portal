const express = require('express');
const { applyForJob, listUserApplications, listJobApplications, changeApplicationStatus } = require('../controllers/applicationController');
const { verifyToken, isEmployer } = require('../middleware/authMiddleware');

const router = express.Router();

// Seeker routes
router.post('/job/:job_id', verifyToken, applyForJob);
router.get('/me', verifyToken, listUserApplications);

// Employer routes
router.get('/job/:job_id', verifyToken, isEmployer, listJobApplications);
router.put('/:application_id/status', verifyToken, isEmployer, changeApplicationStatus);

module.exports = router;
