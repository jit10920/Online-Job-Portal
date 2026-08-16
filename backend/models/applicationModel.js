const pool = require('../config/db');

const createApplication = async (jobId, userId, resumeLink = null) => {
  const query = "INSERT INTO applications (job_id, user_id, resume_link) VALUES (?, ?, ?)";
  const [result] = await pool.execute(query, [jobId, userId, resumeLink]);
  return result.insertId;
};

const getApplicationsByUser = async (userId) => {
  const query = `
    SELECT a.*, j.title, j.company, j.location 
    FROM applications a
    JOIN jobs j ON a.job_id = j.id
    WHERE a.user_id = ?
    ORDER BY a.applied_at DESC
  `;
  const [rows] = await pool.execute(query, [userId]);
  return rows;
};

const getApplicationsByJob = async (jobId, employerId) => {
  const query = `
    SELECT a.*, u.name, u.email 
    FROM applications a
    JOIN users u ON a.user_id = u.id
    JOIN jobs j ON a.job_id = j.id
    WHERE a.job_id = ? AND j.employer_id = ?
    ORDER BY a.applied_at DESC
  `;
  const [rows] = await pool.execute(query, [jobId, employerId]);
  return rows;
};

const updateApplicationStatus = async (applicationId, employerId, status) => {
  const query = `
    UPDATE applications a
    JOIN jobs j ON a.job_id = j.id
    SET a.status = ?
    WHERE a.id = ? AND j.employer_id = ?
  `;
  const [result] = await pool.execute(query, [status, applicationId, employerId]);
  return result.affectedRows > 0;
};

module.exports = {
  createApplication,
  getApplicationsByUser,
  getApplicationsByJob,
  updateApplicationStatus
};
