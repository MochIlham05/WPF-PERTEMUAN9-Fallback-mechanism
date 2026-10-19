const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const { poolB } = require('./config/database');
const { verifyToken } = require('./middleware/auth');
const { decryptProduct } = require('./utils/cryptoHelper');

dotenv.config();

const app = express();
const PORT = process.env.PORT_SERVER_2 || 3100;
const JWT_SECRET = process.env.JWT_SECRET || 'jwt_secret_key_uts_wpf_enkripsi_2026';
const AUTH_USERNAME = process.env.AUTH_USERNAME || 'admin';
const AUTH_PASSWORD = process.env.AUTH_PASSWORD || 'password123';

app.use(cors());
app.use(express.json());

// Endpoint Kategori Server Cadangan (Server B)
app.get('/apiserverb/kategori', async (req, res) => {
  try {
    const [rows] = await poolB.query('SELECT * FROM kategori ORDER BY id ASC');
    return res.status(200).json(rows);
  } catch (error) {
    console.error('Error saat membaca kategori db_b:', error);
    return res.status(500).json({ error: error.message });
  }
});

// 1. Root Endpoint Info Server 2
app.get('/', (req, res) => {
  res.json({
    status: 'ONLINE',
    server: 'Server 2 (Port 3002)',
    connected_database: process.env.DB_B_NAME || 'db_b',
    endpoints: {
      receive_encrypted: 'POST /api/receive-encrypted (Dari Server 1)',
      login_jwt: 'POST /api/login (Autentikasi Client)',
      get_decrypted_products: 'GET /api/produk (Terproteksi JWT)',
      get_raw_ciphertext: 'GET /api/produk/ciphertext (Inspeksi data terenkripsi di db_b)'
    }
  });
});

// 2. POST /api/receive-encrypted - Menerima data terenkripsi dari Server 1 dan menyimpannya langsung ke db_b
app.post('/api/receive-encrypted', async (req, res) => {
  try {
    const { payload } = req.body;

    if (!payload || !Array.isArray(payload) || payload.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Payload data produk terenkripsi tidak ditemukan atau kosong.'
      });
    }

    console.log(`[Server 2] Menerima ${payload.length} item terenkripsi dari Server 1.`);

    // Simpan atau perbarui record ke db_b dalam kondisi ciphertext
    const upsertQuery = `
      INSERT INTO produk (id, nama_produk, harga_produk, foto_produk, id_kategori)
      VALUES (?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        nama_produk = VALUES(nama_produk),
        harga_produk = VALUES(harga_produk),
        foto_produk = VALUES(foto_produk),
        id_kategori = VALUES(id_kategori)
    `;

    for (const item of payload) {
      await poolB.query(upsertQuery, [
        item.id,
        item.nama_produk,
        item.harga_produk,
        item.foto_produk,
        item.id_kategori
      ]);
    }

    console.log(`[Server 2] Berhasil menyimpan ciphertext ke Database B (db_b).`);

    return res.status(200).json({
      success: true,
      message: 'Data terenkripsi berhasil diterima dan disimpan langsung ke Database B (db_b).',
      saved_count: payload.length
    });
  } catch (error) {
    console.error('[Server 2] Gagal menyimpan ciphertext ke db_b:', error);
    return res.status(500).json({
      success: false,
      message: 'Terjadi kesalahan saat menyimpan ciphertext ke Database B',
      error: error.message
    });
  }
});

// 3. POST /api/login - Endpoint login autentikasi & generate JWT Token
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({
      success: false,
      message: 'Username dan password wajib diisi.'
    });
  }

  // Verifikasi kredensial
  if (username === AUTH_USERNAME && password === AUTH_PASSWORD) {
    const payload = {
      username: username,
      role: 'administrator',
      loginAt: new Date().toISOString()
    };

    // Buat JWT token (kedaluwarsa 2 jam)
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });

    return res.status(200).json({
      success: true,
      message: 'Login berhasil.',
      token_type: 'Bearer',
      token: token,
      expires_in: '2 hours',
      user: {
        username: username,
        role: 'administrator'
      }
    });
  } else {
    return res.status(401).json({
      success: false,
      message: 'Kredensial login salah. Silakan periksa username dan password.'
    });
  }
});

// 4. GET /api/produk - Endpoint terproteksi JWT untuk Endpoint/Client
// Mengambil ciphertext dari db_b -> didekripsi kembali menjadi plaintext -> return JSON
app.get('/api/produk', verifyToken, async (req, res) => {
  try {
    const query = `
      SELECT id, nama_produk, harga_produk, foto_produk, id_kategori
      FROM produk
      ORDER BY id ASC
    `;
    const [rows] = await poolB.query(query);

    if (rows.length === 0) {
      return res.status(200).json({
        success: true,
        message: 'Database B (db_b) masih kosong. Jalankan sinkronisasi dari Server 1 terlebih dahulu.',
        total: 0,
        data: []
      });
    }

    // Dekripsi setiap record ciphertext dari db_b
    const decryptedProducts = rows.map((item) => decryptProduct(item));

    return res.status(200).json({
      success: true,
      message: 'Data terenkripsi berhasil diambil dari db_b dan didekripsi kembali menjadi plaintext.',
      requested_by: req.user.username,
      total: decryptedProducts.length,
      data: decryptedProducts
    });
  } catch (error) {
    console.error('[Server 2] Gagal mengambil atau mendekripsi data dari db_b:', error);
    return res.status(500).json({
      success: false,
      message: 'Terjadi kesalahan saat mendekripsi data dari Database B',
      error: error.message
    });
  }
});

// 5. GET /api/produk/ciphertext - Endpoint untuk melihat isi fisik Database B (dalam kondisi ciphertext)
app.get('/api/produk/ciphertext', async (req, res) => {
  try {
    const [rows] = await poolB.query('SELECT * FROM produk ORDER BY id ASC');
    return res.status(200).json({
      success: true,
      message: 'Data mentah (ciphertext) yang tersimpan langsung di Database B (db_b)',
      total: rows.length,
      data: rows
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: 'Gagal membaca tabel ciphertext di db_b',
      error: error.message
    });
  }
});

// Menjalankan Server 2
app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`🛡️ Server 2 berjalan aktif di http://localhost:${PORT}`);
  console.log(`📡 Terhubung ke Database B (${process.env.DB_B_NAME || 'db_b'})`);
  console.log(`🔐 Autentikasi JWT aktif untuk Endpoint Client`);
  console.log(`====================================================`);
});
