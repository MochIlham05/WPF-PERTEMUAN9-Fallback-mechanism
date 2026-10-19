const mysql = require('mysql2/promise');
const dotenv = require('dotenv');

dotenv.config();

// Konfigurasi Pool untuk Database A (db_a)
const poolA = mysql.createPool({
  host: process.env.DB_HOST || '127.0.0.1',
  port: Number(process.env.DB_PORT) || 3306,
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || '',
  database: process.env.DB_A_NAME || 'db_a',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Konfigurasi Pool untuk Database B (db_b)
const poolB = mysql.createPool({
  host: process.env.DB_HOST || '127.0.0.1',
  port: Number(process.env.DB_PORT) || 3306,
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || '',
  database: process.env.DB_B_NAME || 'db_b',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = {
  poolA,
  poolB
};
