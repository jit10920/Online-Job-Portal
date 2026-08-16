const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');
const dotenv = require('dotenv');

dotenv.config();

async function initializeDatabase() {
  console.log('Connecting to MySQL...');
  let connection;
  try {
    // Connect without DB first
    connection = await mysql.createConnection({
      host: process.env.DB_HOST || '127.0.0.1',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '',
      multipleStatements: true
    });

    console.log('Executing schema.sql...');
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schemaSql = fs.readFileSync(schemaPath, 'utf8');

    // Split and execute statements one by one for safety
    const sqlCommands = schemaSql.split(';').map(cmd => cmd.trim()).filter(cmd => cmd.length > 0);
    for (let command of sqlCommands) {
      await connection.query(command);
    }
    
    console.log('Database schema created successfully.');

    // Switch to the database for seeding
    await connection.query('USE job_portal');

    // Check if users exist
    const [rows] = await connection.query('SELECT COUNT(*) as count FROM users');
    if (rows[0].count === 0) {
      console.log('Inserting seed data...');
      
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash('password123', salt);

      // Insert Employer
      const [empResult] = await connection.query(
        "INSERT INTO users (name, email, password_hash, role) VALUES ('Acme Corp', 'employer@acme.com', ?, 'employer')",
        [hashedPassword]
      );
      const employerId = empResult.insertId;

      // Insert Seeker
      const [seekerResult] = await connection.query(
        "INSERT INTO users (name, email, password_hash, role) VALUES ('John Doe', 'john@example.com', ?, 'seeker')",
        [hashedPassword]
      );
      const seekerId = seekerResult.insertId;

      // Insert Job
      const [jobResult] = await connection.query(
        "INSERT INTO jobs (employer_id, title, company, description, requirements, salary, location, type) VALUES (?, 'Software Engineer', 'Acme Corp', 'Develop awesome stuff', 'Node.js, MySQL', '$100k - $120k', 'Remote', 'Full-time')",
        [employerId]
      );
      const jobId = jobResult.insertId;

      // Insert Application
      await connection.query(
        "INSERT INTO applications (job_id, user_id, resume_link, status) VALUES (?, ?, 'http://example.com/resume.pdf', 'pending')",
        [jobId, seekerId]
      );

      console.log('Seed data inserted successfully.');
      console.log(`Employer: employer@acme.com / password123`);
      console.log(`Seeker: john@example.com / password123`);
    } else {
      console.log('Database already contains data. Skipping seed.');
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    if (connection) {
      await connection.end();
    }
    process.exit();
  }
}

initializeDatabase();
