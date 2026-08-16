const { createApplication, getApplicationsByUser, getApplicationsByJob, updateApplicationStatus } = require('../models/applicationModel');

const applyForJob = async (req, res) => {
  try {
    if (req.user.role !== 'seeker') {
      return res.status(403).json({ message: 'Only seekers can apply for jobs' });
    }

    const jobId = req.params.job_id;
    const userId = req.user.user_id;
    const { resume_link } = req.body || {};

    const appId = await createApplication(jobId, userId, resume_link);
    res.status(201).json({ message: 'Application submitted successfully', application_id: appId });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const listUserApplications = async (req, res) => {
  try {
    const userId = req.user.user_id;
    const applications = await getApplicationsByUser(userId);
    res.status(200).json({ applications });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const listJobApplications = async (req, res) => {
  try {
    const jobId = req.params.job_id;
    const employerId = req.user.user_id;
    
    const applications = await getApplicationsByJob(jobId, employerId);
    res.status(200).json({ applications });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

const changeApplicationStatus = async (req, res) => {
  try {
    const applicationId = req.params.application_id;
    const employerId = req.user.user_id;
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({ message: 'Status is required' });
    }

    const validStatuses = ['pending', 'reviewed', 'accepted', 'rejected'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ message: 'Invalid status' });
    }

    const success = await updateApplicationStatus(applicationId, employerId, status);
    if (success) {
      return res.status(200).json({ message: 'Application status updated successfully' });
    }
    res.status(404).json({ message: 'Application not found or unauthorized' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

module.exports = {
  applyForJob,
  listUserApplications,
  listJobApplications,
  changeApplicationStatus
};
