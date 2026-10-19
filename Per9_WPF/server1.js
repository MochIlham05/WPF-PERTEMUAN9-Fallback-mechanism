const express = require('express');
const cors = require('cors');
const axios = require('axios');
const dotenv = require('dotenv');
const { poolA } = require('./config/database');
const { encryptProduct } = require('./utils/cryptoHelper');

dotenv.config();

const app = express();
const PORT = process.env.PORT_SERVER_1 || 4000;
const SERVER_2_URL = process.env.SERVER_2_URL || 'http://localhost:3100';

app.use(cors());
app.use(express.json());

// Endpoint Kategori Server Utama
app.get('/api/kategori', async (req, res) => {
  try {
    const [rows] = await poolA.query('SELECT * FROM kategori ORDER BY id ASC');
    return res.status(200).json(rows);
  } catch (error) {
    console.error('Error saat membaca kategori db_a:', error);
    return res.status(500).json({ error: error.message });
  }
});

// 1. Root Endpoint Info Server 1
app.get('/', (req, res) => {
  res.json({
    status: 'ONLINE',
    server: 'Server 1 (Port 3001)',
    connected_database: process.env.DB_A_NAME || 'db_a',
    endpoints: {
      get_plaintext_products: 'GET /api/produk',
      create_new_product: 'POST /api/produk',
      encrypt_and_send_to_server2: 'POST /api/send-encrypted'
    }
  });
});

// 2. GET /api/produk - Mengambil data plaintext dari db_a
app.get('/api/produk', async (req, res) => {
  try {
    const query = `
      SELECT p.id, p.nama_produk, p.harga_produk, p.foto_produk, p.id_kategori, k.nama_kategori
      FROM produk p
      LEFT JOIN kategori k ON p.id_kategori = k.id
      ORDER BY p.id ASC
    `;
    const [rows] = await poolA.query(query);

    return res.status(200).json({
      success: true,
      message: 'Berhasil mengambil data produk dari Database A (db_a)',
      total: rows.length,
      data: rows
    });
  } catch (error) {
    console.error('Error saat membaca db_a:', error);
    return res.status(500).json({
      success: false,
      message: 'Terjadi kesalahan saat membaca data dari Database A',
      error: error.message
    });
  }
});

// 3. POST /api/produk - Menambahkan produk baru ke db_a (Plaintext)
app.post('/api/produk', async (req, res) => {
  try {
    const { nama_produk, harga_produk, foto_produk, id_kategori } = req.body;

    if (!nama_produk || !harga_produk || !foto_produk || !id_kategori) {
      return res.status(400).json({
        success: false,
        message: 'Field nama_produk, harga_produk, foto_produk, dan id_kategori wajib diisi.'
      });
    }

    const query = `
      INSERT INTO produk (nama_produk, harga_produk, foto_produk, id_kategori)
      VALUES (?, ?, ?, ?)
    `;
    const [result] = await poolA.query(query, [
      nama_produk,
      Number(harga_produk),
      foto_produk,
      Number(id_kategori)
    ]);

    return res.status(201).json({
      success: true,
      message: 'Produk berhasil ditambahkan ke Database A (db_a)',
      inserted_id: result.insertId
    });
  } catch (error) {
    console.error('Error saat menambah produk ke db_a:', error);
    return res.status(500).json({
      success: false,
      message: 'Terjadi kesalahan saat menambahkan data ke Database A',
      error: error.message
    });
  }
});

// 4. POST /api/send-encrypted - Mengambil dari db_a, enkripsi dengan AES-256-CBC, lalu kirim via HTTP POST ke Server 2
app.post('/api/send-encrypted', async (req, res) => {
  try {
    // Langkah 1: Ambil data dari db_a
    const query = `
      SELECT id, nama_produk, harga_produk, foto_produk, id_kategori
      FROM produk
      ORDER BY id ASC
    `;
    const [rows] = await poolA.query(query);

    if (rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Tidak ada data produk ditemukan di Database A (db_a).'
      });
    }

    // Langkah 2: Enkripsi setiap record produk menggunakan AES-256-CBC
    const encryptedProducts = rows.map((item) => encryptProduct(item));

    console.log(`[Server 1] Berhasil mengenkripsi ${encryptedProducts.length} produk.`);

    // Langkah 3: Kirim data terenkripsi via HTTP POST ke Server 2
    const targetUrl = `${SERVER_2_URL}/api/receive-encrypted`;
    console.log(`[Server 1] Mengirim payload terenkripsi ke Server 2: ${targetUrl}`);

    const responseServer2 = await axios.post(targetUrl, {
      source: 'Server 1 (Port 3001)',
      timestamp: new Date().toISOString(),
      total_items: encryptedProducts.length,
      payload: encryptedProducts
    });

    return res.status(200).json({
      success: true,
      message: 'Data berhasil diambil dari db_a, dienkripsi (AES-256-CBC), dan dikirim ke Server 2.',
      server2_response: responseServer2.data,
      sample_encrypted_data: encryptedProducts.slice(0, 2) // Contoh 2 item terenkripsi untuk inspeksi
    });
  } catch (error) {
    console.error('[Server 1] Gagal melakukan enkripsi atau pengiriman ke Server 2:', error.message);
    const detail = error.response ? error.response.data : error.message;
    return res.status(500).json({
      success: false,
      message: 'Gagal mengirim data terenkripsi ke Server 2',
      error: detail
    });
  }
});

// Menjalankan Server 1
app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`🚀 Server 1 berjalan aktif di http://localhost:${PORT}`);
  console.log(`📡 Terhubung ke Database A (${process.env.DB_A_NAME || 'db_a'})`);
  console.log(`====================================================`);
});
