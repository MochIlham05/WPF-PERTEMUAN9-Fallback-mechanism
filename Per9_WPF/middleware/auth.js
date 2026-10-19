const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const JWT_SECRET = process.env.JWT_SECRET || 'jwt_secret_key_uts_wpf_enkripsi_2026';

/**
 * Middleware untuk memvalidasi JWT Token pada header Authorization
 */
function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'] || req.headers['Authorization'];

  if (!authHeader) {
    return res.status(401).json({
      success: false,
      message: 'Akses ditolak: Token autentikasi tidak ditemukan pada header Authorization.'
    });
  }

  // Format header: "Bearer <token>"
  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return res.status(401).json({
      success: false,
      message: 'Format token tidak valid. Gunakan format: Bearer <token>'
    });
  }

  const token = parts[1];

  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({
        success: false,
        message: 'Token tidak valid atau telah kedaluwarsa.',
        error: err.message
      });
    }

    // Simpan informasi user hasil decode ke request
    req.user = decoded;
    next();
  });
}

module.exports = {
  verifyToken
};
