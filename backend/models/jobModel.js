const pool = require('../config/db');

const createJob = async (employerId, title, company, description, requirements, salary, location, type = 'Full-time') => {
  const query = `
    INSERT INTO jobs (employer_id, title, company, description, requirements, salary, location, type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;
  const [result] = await pool.execute(query, [
    employerId, title, company, description, requirements || null, salary || null, location || null, type
  ]);
  return result.insertId;
};

const getAllJobs = async (filters = {}) => {
  let query = "SELECT * FROM jobs WHERE status = 'open'";
  const params = [];

  if (filters.location) {
    query += " AND location LIKE ?";
    params.push(`%${filters.location}%`);
  }
  if (filters.type) {
    query += " AND type = ?";
    params.push(filters.type);
  }
  if (filters.keyword) {
    query += " AND (title LIKE ? OR description LIKE ? OR company LIKE ?)";
    params.push(`%${filters.keyword}%`, `%${filters.keyword}%`, `%${filters.keyword}%`);
  }

  query += " ORDER BY created_at DESC";
  const [rows] = await pool.execute(query, params);
  return rows;
};

const getJobById = async (jobId) => {
  const query = "SELECT * FROM jobs WHERE id = ?";
  const [rows] = await pool.execute(query, [jobId]);
  return rows.length > 0 ? rows[0] : null;
};

const updateJob = async (jobId, employerId, updates) => {
  const allowedFields = ['title', 'company', 'description', 'requirements', 'salary', 'location', 'type', 'status'];
  const updateClauses = [];
  const params = [];

  for (const [key, value] of Object.entries(updates)) {
    if (allowedFields.includes(key)) {
      updateClauses.push(`${key} = ?`);
      params.push(value);
    }
  }

  if (updateClauses.length === 0) return false;

  const query = `UPDATE jobs SET ${updateClauses.join(', ')} WHERE id = ? AND employer_id = ?`;
  params.push(jobId, employerId);

  const [result] = await pool.execute(query, params);
  return result.affectedRows > 0;
};

const deleteJob = async (jobId, employerId) => {
  const query = "DELETE FROM jobs WHERE id = ? AND employer_id = ?";
  const [result] = await pool.execute(query, [jobId, employerId]);
  return result.affectedRows > 0;
};

module.exports = {
  createJob,
  getAllJobs,
  getJobById,
  updateJob,
  deleteJob
};
