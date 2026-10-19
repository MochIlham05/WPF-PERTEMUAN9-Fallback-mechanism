# Proyek Implementasi Enkripsi - Dekripsi REST API (AES-256-CBC & JWT)

Implementasi arsitektur REST API terdistribusi menggunakan **Node.js (Express)**, enkripsi simetris **AES-256-CBC**, autentikasi **JWT (JSON Web Token)**, dan **MySQL (XAMPP)**.

---

## 📐 Arsitektur Sistem

Berdasarkan skema arsitektur:
```
+-------------+         (1) HTTP POST          +-------------+
|  Server 1   | -----------------------------> |  Server 2   |
| (Port 3001) |       (Data Terenkripsi)       | (Port 3002) |
+------+------+                                +------+------+
       |                                              |
       | Query Plaintext                              | Simpan / Ambil Ciphertext
       v                                              v
+-------------+                                +-------------+
| Database A  |                                | Database B  |
|   (db_a)    |                                |   (db_b)    |
| (Plaintext) |                                | (Ciphertext)|
+-------------+                                +------+------+
                                                      ^
                                                      | (4) GET Plaintext
                                                      |     (Terproteksi JWT)
                                                      |
                                               +------+------+
                                               | Client App  |
                                               |  (Postman)  |
                                               +-------------+
```

1. **Database A (`db_a`)**: Menyimpan data produk dan kategori dalam bentuk teks biasa (plaintext).
2. **Database B (`db_b`)**: Menyimpan data produk dalam bentuk teks terenkripsi (ciphertext).
3. **Server 1 (Port 3001)**:
   - Mengambil data dari `db_a`.
   - Mengenkripsi field produk menggunakan algoritma **AES-256-CBC**.
   - Mengirim data terenkripsi via HTTP POST ke Server 2 (`/api/receive-encrypted`).
4. **Server 2 (Port 3002)**:
   - Menerima payload terenkripsi dan menyimpannya langsung ke `db_b`.
   - Menyediakan endpoint login untuk autentikasi dan menghasilkan **JWT Token**.
   - Menyediakan endpoint terproteksi JWT untuk Client: mengambil ciphertext dari `db_b`, mendekripsi dengan AES-256-CBC, lalu mengembalikan plaintext dalam format JSON.

---

## 🗂️ Struktur File Proyek

```
UTS_WPF/
├── config/
│   └── database.js          # Konfigurasi koneksi MySQL poolA (db_a) & poolB (db_b)
├── middleware/
│   └── auth.js              # Middleware verifikasi JWT Bearer Token
├── utils/
│   └── cryptoHelper.js      # Modul enkripsi & dekripsi AES-256-CBC
├── .env                     # Variabel environment & rahasia
├── .env.example             # Template variabel environment
├── package.json             # Dependensi Express, mysql2, axios, jwt, dotenv
├── schema.sql               # Skrip pembuatan database db_a, db_b, dan sample data
├── server1.js               # Service Server 1 (Port 3001)
├── server2.js               # Service Server 2 (Port 3002)
├── postman_collection.json  # File koleksi Postman siap import
└── README.md                # Dokumentasi & panduan pengujian
```

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Prasyarat
- **Node.js** (v16 ke atas)
- **XAMPP** (Pastikan service Apache dan MySQL sudah berjalan / *Started*)

### 2. Eksekusi Skrip Database MySQL
1. Buka browser dan buka **phpMyAdmin** (`http://localhost/phpmyadmin`) atau terminal MySQL.
2. Buka tab **SQL**, salin dan jalankan seluruh isi file `schema.sql`.
3. Skrip akan membuat:
   - Database `db_a` beserta tabel `kategori` & `produk` terisi 4 data awal.
   - Database `db_b` beserta tabel `kategori` & `produk` (disiapkan untuk ciphertext).

### 3. Install Dependensi Node.js
Buka terminal / PowerShell di direktori `c:\xampp\htdocs\UTS_WPF`, lalu jalankan:
```bash
npm install
```

### 4. Konfigurasi `.env`
Pastikan file `.env` sudah sesuai dengan pengaturan XAMPP Anda:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=
DB_A_NAME=db_a
DB_B_NAME=db_b

PORT_SERVER_1=3001
PORT_SERVER_2=3002
SERVER_2_URL=http://localhost:3002

AES_SECRET_KEY=kunci_rahasia_aes_256_bit_32byts
JWT_SECRET=jwt_secret_key_uts_wpf_enkripsi_2026

AUTH_USERNAME=admin
AUTH_PASSWORD=password123
```

### 5. Jalankan Kedua Server
Buka 2 tab terminal terpisah:

**Terminal 1 (Server 2 - Port 3002):**
```bash
npm run start:server2
```

**Terminal 2 (Server 1 - Port 3001):**
```bash
npm run start:server1
```

---

## 🧪 Langkah Pengujian Menggunakan Postman

Anda dapat mengimpor file [postman_collection.json](file:///c:/xampp/htdocs/UTS_WPF/postman_collection.json) langsung ke aplikasi Postman (*File -> Import -> Pilih postman_collection.json*).

Berikut alur pengujian step-by-step:

### Langkah 1: Cek Data Plaintext di Server 1 (db_a)
- **Method:** `GET`
- **URL:** `http://localhost:3001/api/produk`
- **Tujuan:** Memastikan data plaintext di database `db_a` terbaca dengan benar.

### Langkah 2: Lakukan Enkripsi & Kirim ke Server 2
- **Method:** `POST`
- **URL:** `http://localhost:3001/api/send-encrypted`
- **Headers:** None
- **Tujuan:** Server 1 mengambil data dari `db_a`, mengenkripsinya dengan AES-256-CBC, lalu menembakkannya via HTTP POST ke Server 2. Server 2 kemudian menyimpan ciphertext ke `db_b`.
- **Response Sukses:**
  ```json
  {
    "success": true,
    "message": "Data berhasil diambil dari db_a, dienkripsi (AES-256-CBC), dan dikirim ke Server 2.",
    "server2_response": {
      "success": true,
      "message": "Data terenkripsi berhasil diterima dan disimpan langsung ke Database B (db_b).",
      "saved_count": 4
    }
  }
  ```

### Langkah 3: Verifikasi Fisik Ciphertext di Server 2 (db_b)
- **Method:** `GET`
- **URL:** `http://localhost:3002/api/produk/ciphertext`
- **Tujuan:** Membuktikan bahwa di database `db_b`, data kolom `nama_produk`, `harga_produk`, dll. benar-benar tersimpan dalam bentuk string ciphertext acak (format `IV:Ciphertext`).

### Langkah 4: Coba Akses Endpoint Didekripsi Tanpa Token (Uji Proteksi)
- **Method:** `GET`
- **URL:** `http://localhost:3002/api/produk`
- **Headers:** Kosongkan Authorization
- **Hasil:** Status `401 Unauthorized` dengan pesan penolakan akses.

### Langkah 5: Login untuk Mendapatkan Token JWT
- **Method:** `POST`
- **URL:** `http://localhost:3002/api/login`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
  ```json
  {
    "username": "admin",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": "2 hours"
  }
  ```
  *(Salin nilai `token` tersebut)*

### Langkah 6: Ambil Data Plaintext Didekripsi (Client Request Terproteksi)
- **Method:** `GET`
- **URL:** `http://localhost:3002/api/produk`
- **Headers:**
  - `Authorization`: `Bearer <MASUKKAN_TOKEN_DARI_LANGKAH_5>`
- **Response:** Server 2 mengambil ciphertext dari `db_b`, mendekripsinya dengan AES-256-CBC, dan mengembalikan hasil plaintext yang utuh.

---

## 🔒 Detail Mekanisme Kriptografi AES-256-CBC

1. **Algoritma:** `aes-256-cbc` (Advanced Encryption Standard dengan panjang kunci 256 bit dan mode Cipher Block Chaining).
2. **Kunci (Key):** Diambil dari string rahasia 32 bytes pada environment variable dan di-hash SHA-256 untuk memastikan integritas 256 bit.
3. **Initialization Vector (IV):** Dihasilkan secara acak sebesar 16 bytes (`crypto.randomBytes(16)`) pada setiap proses enkripsi demi mencegah serangan pola (*pattern analysis*).
4. **Format Penyimpanan:** String berformat `${ivHex}:${encryptedHex}` sehingga IV dan ciphertext dapat dipisahkan secara presisi saat proses dekripsi.
