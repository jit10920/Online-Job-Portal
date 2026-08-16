const pool = require('../config/db');

const createUser = async (name, email, passwordHash, role = 'seeker') => {
  const query = 'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)';
  const [result] = await pool.execute(query, [name, email, passwordHash, role]);
  return result.insertId;
};

const getUserByEmail = async (email) => {
  const query = 'SELECT * FROM users WHERE email = ?';
  const [rows] = await pool.execute(query, [email]);
  return rows.length > 0 ? rows[0] : null;
};

const getUserById = async (id) => {
  const query = 'SELECT id, name, email, role, created_at FROM users WHERE id = ?';
  const [rows] = await pool.execute(query, [id]);
  return rows.length > 0 ? rows[0] : null;
};

module.exports = {
  createUser,
  getUserByEmail,
  getUserById
};
