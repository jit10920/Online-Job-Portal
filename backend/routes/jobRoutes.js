const express = require('express');
const { postJob, listJobs, getJob, editJob, removeJob } = require('../controllers/jobController');
const { verifyToken, isEmployer } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/', listJobs);
router.get('/:job_id', getJob);

// Protected routes for employers
router.post('/', verifyToken, isEmployer, postJob);
router.put('/:job_id', verifyToken, isEmployer, editJob);
router.delete('/:job_id', verifyToken, isEmployer, removeJob);

module.exports = router;
