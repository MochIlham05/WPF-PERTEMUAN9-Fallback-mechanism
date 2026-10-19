const crypto = require('crypto');
const dotenv = require('dotenv');

dotenv.config();

const ALGORITHM = 'aes-256-cbc';
const RAW_KEY = process.env.AES_SECRET_KEY || '12345678901234567890123456789012';

// Pastikan Key selalu tepat 32 bytes (256 bits)
const KEY = crypto.createHash('sha256').update(String(RAW_KEY)).digest();

/**
 * Enkripsi string teks biasa menjadi ciphertext menggunakan AES-256-CBC
 * @param {string|number} text - Data plaintext yang akan dienkripsi
 * @returns {string} - Hasil enkripsi berformat 'ivHex:encryptedHex'
 */
function encrypt(text) {
  if (text === null || text === undefined) {
    return '';
  }

  const textToEncrypt = String(text);
  // IV (Initialization Vector) wajib 16 bytes untuk AES-CBC
  const iv = crypto.randomBytes(16);

  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);
  let encrypted = cipher.update(textToEncrypt, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  // Menggabungkan IV dan Ciphertext dengan pemisah ':'
  return `${iv.toString('hex')}:${encrypted}`;
}

/**
 * Dekripsi ciphertext kembali ke plaintext string
 * @param {string} cipherTextWithIv - String terenkripsi berformat 'ivHex:encryptedHex'
 * @returns {string} - Plaintext hasil dekripsi
 */
function decrypt(cipherTextWithIv) {
  if (!cipherTextWithIv || typeof cipherTextWithIv !== 'string' || !cipherTextWithIv.includes(':')) {
    return cipherTextWithIv;
  }

  const [ivHex, encryptedHex] = cipherTextWithIv.split(':');
  if (!ivHex || !encryptedHex) {
    return cipherTextWithIv;
  }

  const iv = Buffer.from(ivHex, 'hex');
  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);

  let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}

/**
 * Helper untuk mengenkripsi satu objek produk
 * @param {object} product - Objek produk dari database A
 * @returns {object} - Objek dengan atribut yang terenkripsi
 */
function encryptProduct(product) {
  return {
    id: product.id, // ID dibiarkan atau dipertahankan sebagai integer PK
    nama_produk: encrypt(product.nama_produk),
    harga_produk: encrypt(product.harga_produk),
    foto_produk: encrypt(product.foto_produk),
    id_kategori: encrypt(product.id_kategori),
    // Bila terdapat nama_kategori dari JOIN
    ...(product.nama_kategori ? { nama_kategori: encrypt(product.nama_kategori) } : {})
  };
}

/**
 * Helper untuk mendekripsi satu objek produk
 * @param {object} encryptedProduct - Objek produk dari database B
 * @returns {object} - Objek dengan atribut yang didekripsi
 */
function decryptProduct(encryptedProduct) {
  return {
    id: encryptedProduct.id,
    nama_produk: decrypt(encryptedProduct.nama_produk),
    harga_produk: Number(decrypt(encryptedProduct.harga_produk)) || decrypt(encryptedProduct.harga_produk),
    foto_produk: decrypt(encryptedProduct.foto_produk),
    id_kategori: Number(decrypt(encryptedProduct.id_kategori)) || decrypt(encryptedProduct.id_kategori),
    ...(encryptedProduct.nama_kategori ? { nama_kategori: decrypt(encryptedProduct.nama_kategori) } : {})
  };
}

module.exports = {
  encrypt,
  decrypt,
  encryptProduct,
  decryptProduct
};
