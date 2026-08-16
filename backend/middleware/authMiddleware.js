const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
  let token = req.cookies?.token;
  const authHeader = req.headers['authorization'];
  if (!token && authHeader && authHeader.startsWith('Bearer ')) {
    token = authHeader.split(' ')[1];
  }

  if (!token) {
    if (req.accepts('html')) {
        return res.redirect('/login');
    }
    return res.status(401).json({ message: 'Token is missing' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'super-secret-key-change-me');
    req.user = decoded;
    next();
  } catch (err) {
    res.clearCookie('token');
    if (req.accepts('html')) return res.redirect('/login');
    return res.status(401).json({ message: 'Token is invalid' });
  }
};

const optionalAuth = (req, res, next) => {
  let token = req.cookies?.token;
  if (!token && req.headers['authorization']) {
      token = req.headers['authorization'].split(' ')[1];
  }
  if (token) {
      try {
          req.user = jwt.verify(token, process.env.JWT_SECRET || 'super-secret-key-change-me');
      } catch (err) {
          res.clearCookie('token');
      }
  }
  next();
};

const isEmployer = (req, res, next) => {
  if (req.user && req.user.role === 'employer') {
    next();
  } else {
    if (req.accepts('html')) return res.redirect('/');
    return res.status(403).json({ message: 'Employer access required' });
  }
};

module.exports = {
  verifyToken,
  optionalAuth,
  isEmployer
};
