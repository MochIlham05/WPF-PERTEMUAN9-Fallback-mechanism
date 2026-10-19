-- =======================================================
-- SKRIP DATABASE: db_a dan db_b
-- Proyek Enkripsi-Dekripsi REST API AES-256-CBC
-- =======================================================

-- 1. DATABASE A (Menyimpan data asli dalam bentuk plaintext)
CREATE DATABASE IF NOT EXISTS db_a;
USE db_a;

-- Drop tabel jika sudah ada sebelumnya
DROP TABLE IF EXISTS produk;
DROP TABLE IF EXISTS kategori;

-- Tabel 'kategori' di db_a
CREATE TABLE kategori (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- Tabel 'produk' di db_a
CREATE TABLE produk (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_produk VARCHAR(100) NOT NULL,
    harga_produk INT NOT NULL,
    foto_produk VARCHAR(255) NOT NULL,
    id_kategori INT NOT NULL,
    FOREIGN KEY (id_kategori) REFERENCES kategori(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sample Data db_a
INSERT INTO kategori (id, nama_kategori) VALUES
(1, 'Elektronik'),
(2, 'Pakaian'),
(3, 'Makanan & Minuman');

INSERT INTO produk (id, nama_produk, harga_produk, foto_produk, id_kategori) VALUES
(1, 'Laptop Asus ROG Zephyrus', 25000000, 'laptop_asus_rog.jpg', 1),
(2, 'Smartphone Samsung S24', 18000000, 'samsung_s24.jpg', 1),
(3, 'Kemeja Flannel Pria', 250000, 'kemeja_flannel.jpg', 2),
(4, 'Kopi Arabika Gayo 250g', 85000, 'kopi_gayo.jpg', 3);


-- =======================================================
-- 2. DATABASE B (Menyimpan data produk dalam bentuk terenkripsi / ciphertext)
-- =======================================================
CREATE DATABASE IF NOT EXISTS db_b;
USE db_b;

-- Drop tabel jika sudah ada sebelumnya
DROP TABLE IF EXISTS produk;
DROP TABLE IF EXISTS kategori;

-- Tabel 'kategori' di db_b
CREATE TABLE kategori (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- Tabel 'produk' di db_b
-- Kolom-kolom teks/angka disimpan sebagai TEXT untuk menampung string ciphertext (IV:Ciphertext)
CREATE TABLE produk (
    id INT PRIMARY KEY,
    nama_produk TEXT NOT NULL,
    harga_produk TEXT NOT NULL,
    foto_produk TEXT NOT NULL,
    id_kategori TEXT NOT NULL
) ENGINE=InnoDB;

-- Opsional: Seed kategori di db_b untuk keselarasan
INSERT INTO kategori (id, nama_kategori) VALUES
(1, 'Elektronik'),
(2, 'Pakaian'),
(3, 'Makanan & Minuman');
