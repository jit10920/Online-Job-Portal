const { createJob, getAllJobs, getJobById, updateJob, deleteJob } = require('../models/jobModel');

const postJob = async (req, res) => {
  try {
    const { title, company, description, requirements, salary, location, type } = req.body;
    if (!title || !company || !description) {
      return res.status(400).json({ message: 'Missing required fields' });
    }

    const employerId = req.user.user_id;
    const jobId = await createJob(employerId, title, company, description, requirements, salary, location, type);
    
    res.status(201).json({ message: 'Job posted successfully', job_id: jobId });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const listJobs = async (req, res) => {
  try {
    const filters = {
      location: req.query.location,
      type: req.query.type,
      keyword: req.query.keyword
    };
    const jobs = await getAllJobs(filters);
    res.status(200).json({ jobs });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const getJob = async (req, res) => {
  try {
    const jobId = req.params.job_id;
    const job = await getJobById(jobId);
    if (!job) {
      return res.status(404).json({ message: 'Job not found' });
    }
    res.status(200).json({ job });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const editJob = async (req, res) => {
  try {
    const jobId = req.params.job_id;
    const employerId = req.user.user_id;
    
    if (!req.body || Object.keys(req.body).length === 0) {
      return res.status(400).json({ message: 'No data provided for update' });
    }

    const success = await updateJob(jobId, employerId, req.body);
    if (success) {
      return res.status(200).json({ message: 'Job updated successfully' });
    }
    res.status(404).json({ message: 'Job not found or unauthorized' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const removeJob = async (req, res) => {
  try {
    const jobId = req.params.job_id;
    const employerId = req.user.user_id;
    
    const success = await deleteJob(jobId, employerId);
    if (success) {
      return res.status(200).json({ message: 'Job deleted successfully' });
    }
    res.status(404).json({ message: 'Job not found or unauthorized' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

module.exports = {
  postJob,
  listJobs,
  getJob,
  editJob,
  removeJob
};
