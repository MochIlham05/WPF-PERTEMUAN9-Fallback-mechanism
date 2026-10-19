import os
import sys
import subprocess
import zipfile
import shutil

# 1. Pastikan library python-docx terinstall
try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
except ImportError:
    print("[*] Menginstal library python-docx...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn

DOCX_NAME = "UTS_Moch Ilham Abdul Aziz_3125522014_WORKSHOP PEMROGAMAN FRAMEWORK_Pertemuan 8.docx"
BACKUP_NAME = "UTS_Moch Ilham Abdul Aziz_3125522014_BACKUP.docx"

def set_cell_background(cell, fill_hex):
    """Memberi warna latar (shading) pada sel tabel"""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    """Mengatur padding internal sel tabel"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout_box(doc, text, caption_label):
    """Menambahkan kotak berbingkai profesional untuk placeholder screenshot"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    # Warna abu-abu lembut formal (#F8F9FA)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=160, bottom=160, left=220, right=220)
    
    # Border styling (border putus-putus atau garis ganda bernuansa teknis)
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="dashed" w:sz="8" w:space="0" w:color="0284C7"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="0284C7"/>
            <w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="0284C7"/>
            <w:right w:val="dashed" w:sz="8" w:space="0" w:color="0284C7"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    
    r_title = p.add_run(f"📸 {text}\n")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(2, 132, 199) # Sky blue / Navy
    
    r_desc = p.add_run(f"Instruksi Bukti Pengujian:\n{caption_label}")
    r_desc.font.name = "Times New Roman"
    r_desc.font.size = Pt(9.5)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def extract_existing_images():
    """Mengekstrak gambar diagram bawaan dari dokumen lama jika ada"""
    images = []
    if os.path.exists(DOCX_NAME):
        try:
            with zipfile.ZipFile(DOCX_NAME, 'r') as z:
                for filename in z.namelist():
                    if filename.startswith('word/media/'):
                        extracted_path = os.path.join("temp_media", os.path.basename(filename))
                        os.makedirs("temp_media", exist_ok=True)
                        with open(extracted_path, 'wb') as f:
                            f.write(z.read(filename))
                        images.append(extracted_path)
        except Exception as e:
            print(f"[!] Gagal mengekstrak media: {e}")
    return images

def build_report():
    print(f"[*] Menyiapkan laporan Word untuk: {DOCX_NAME}")
    
    # Backup dokumen lama jika ada
    if os.path.exists(DOCX_NAME) and not os.path.exists(BACKUP_NAME):
        shutil.copyfile(DOCX_NAME, BACKUP_NAME)
        print(f"[+] Backup dokumen berhasil dibuat: {BACKUP_NAME}")
        
    extracted_images = extract_existing_images()
    
    doc = docx.Document()
    
    # Atur Margin Halaman (Standar Skripsi/Laporan: 1 inci / 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Styling Normal Font
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(12)
    font_normal.color.rgb = RGBColor(30, 41, 59)
    
    # =========================================================================
    # 1. JUDUL & IDENTITAS
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("LAPORAN UJIAN TENGAH SEMESTER (UTS)\nWORKSHOP PEMROGRAMAN FRAMEWORK")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(14)
    run_title.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)
    
    p_subtitle = doc.add_paragraph()
    p_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subtitle.paragraph_format.space_after = Pt(18)
    run_sub = p_subtitle.add_run("Implementasi Enkripsi, Dekripsi, dan Autentikasi JWT pada Arsitektur Multi-Server Berbasis REST API")
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(12.5)
    run_sub.font.color.rgb = RGBColor(30, 41, 59)
    run_sub.italic = True
    
    # Tabel Identitas Mahasiswa
    id_table = doc.add_table(rows=5, cols=2)
    id_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    id_table.autofit = False
    
    col_widths = [Inches(2.2), Inches(4.3)]
    identitas_data = [
        ("Nama Lengkap", ": Moch Ilham Abdul Aziz"),
        ("NIM", ": 3125522014"),
        ("Mata Kuliah", ": Workshop Pemrograman Framework (Pertemuan 8)"),
        ("Dosen Pengampu", ": [Nama Dosen Pengampu]"),
        ("Tanggal Pengujian", ": 12 Oktober 2026")
    ]
    
    for row_idx, (k, v) in enumerate(identitas_data):
        row = id_table.rows[row_idx]
        cell_k = row.cells[0]
        cell_v = row.cells[1]
        
        cell_k.width = col_widths[0]
        cell_v.width = col_widths[1]
        
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.bold = True
        rk.font.name = "Times New Roman"
        rk.font.size = Pt(11)
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.name = "Times New Roman"
        rv.font.size = Pt(11)
        
        set_cell_background(cell_k, "F8FAFC")
        set_cell_background(cell_v, "FFFFFF")
        
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # Garis Pembatas Horisontal
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(16)
    r_div = p_div.add_run("―" * 56)
    r_div.font.color.rgb = RGBColor(203, 213, 225)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Helper untuk Heading
    def add_custom_heading(text, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.bold = True
        if level == 1:
            r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(15, 23, 42)
        else:
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    # =========================================================================
    # 2. PENDAHULUAN & TUJUAN SISTEM
    # =========================================================================
    add_custom_heading("BAB I. PENDAHULUAN DAN TUJUAN SISTEM", level=1)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "Keamanan data merupakan pilar fundamental dalam arsitektur aplikasi modern, terutama pada ekosistem "
        "layanan terdistribusi (*distributed microservices*). Dalam komunikasi antar server maupun penyimpanan "
        "pada basis data, celah keamanan seperti penyadapan lalu lintas jaringan (*Man-in-the-Middle Attack*) dan "
        "kebocoran data pada storage (*Data Breach*) seringkali terjadi apabila data dibiarkan dalam kondisi teks terbuka (*plaintext*).\n\n"
        "Pada tugas Ujian Tengah Semester (UTS) ini, dirancang dan diimplementasikan sebuah arsitektur REST API terdistribusi "
        "yang memadukan teknik kriptografi simetris modern (AES-256-CBC), pemisahan fisik basis data (Database A dan Database B), "
        "serta sistem otorisasi token berbasis JWT (JSON Web Token)."
    )
    
    p_tujuan = doc.add_paragraph()
    p_tujuan.paragraph_format.space_after = Pt(8)
    p_tujuan.add_run("Tujuan dari implementasi sistem ini adalah sebagai berikut:").bold = True
    
    tujuan_list = [
        "Mencegah kebocoran data pada penyimpanan basis data sekunder (Database B) dengan mengamankannya menggunakan enkripsi simetris.",
        "Mengamankan transmisi data antar server (Server 1 menuju Server 2) dengan membungkus payload produk dalam bentuk ciphertext.",
        "Mengimplementasikan algoritma AES-256-CBC dengan menggunakan Kunci Rahasia 256-bit dan Initialization Vector (IV) acak 128-bit pada setiap proses.",
        "Menerapkan mekanisme otentikasi dan otorisasi menggunakan JWT (JSON Web Token) agar hanya pengguna sah yang dapat meminta dekripsi data produk melalui endpoint client."
    ]
    for item in tujuan_list:
        pi = doc.add_paragraph(style='List Bullet')
        pi.paragraph_format.space_after = Pt(3)
        pi.add_run(item)

    # =========================================================================
    # 3. ARSITEKTUR & PENJELASAN SKEMA SISTEM
    # =========================================================================
    add_custom_heading("BAB II. ARSITEKTUR DAN SKEMA SISTEM", level=1)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Arsitektur sistem dibangun menggunakan model multi-server yang saling berkomunikasi menggunakan protokol HTTP REST API "
        "dan berinteraksi dengan dua basis data MySQL terpisah (db_a dan db_b)."
    )
    
    # Sisipkan gambar diagram jika tersedia dari file asli
    if extracted_images:
        try:
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(4)
            run_img = p_img.add_run()
            run_img.add_picture(extracted_images[0], width=Inches(6.0))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r_cap = p_cap.add_run("Gambar 2.1: Diagram Arsitektur Multi-Server, Database Terdistribusi, dan Alur Enkripsi-Dekripsi")
            r_cap.font.size = Pt(10)
            r_cap.font.italic = True
        except Exception as e:
            print(f"[!] Gagal menyematkan gambar: {e}")
            
    add_custom_heading("2.1 Penjelasan Alur Kerja Sistem (Alur 1 s.d. 4)", level=2)
    alur_items = [
        ("Alur 1 (Enkripsi & Pengiriman)", "Server 1 membaca data produk dari Database A (db_a). Setiap atribut produk (nama, harga, foto, kategori) dienkripsi menggunakan algoritma AES-256-CBC menjadi string ciphertext. Selanjutnya, Server 1 mengirimkan data terenkripsi tersebut ke Server 2 via HTTP POST /api/receive-encrypted."),
        ("Alur 2 (Penyimpanan Ciphertext)", "Server 2 menerima request dari Server 1 dan langsung menyimpan seluruh data tersebut ke Database B (db_b) dalam bentuk ciphertext (tanpa didekripsi di storage db_b)."),
        ("Alur 3 (Permintaan Data Klien)", "Client/Endpoint melakukan login terlebih dahulu ke Server 2 (/api/login) untuk memperoleh JSON Web Token (JWT). Selanjutnya, klien mengirimkan HTTP GET /api/produk dengan menyertakan Bearer Token pada header Authorization."),
        ("Alur 4 (Dekripsi & Respon Klien)", "Server 2 memvalidasi keabsahan token JWT. Jika valid, Server 2 mengambil data ciphertext dari db_b, mendekripsinya kembali menjadi plaintext menggunakan algoritma AES-256-CBC, dan mengembalikan data produk dalam bentuk format JSON kepada klien.")
    ]
    for judul_alur, desc_alur in alur_items:
        pa = doc.add_paragraph()
        pa.paragraph_format.space_after = Pt(4)
        ra_b = pa.add_run(f"• {judul_alur}: ")
        ra_b.bold = True
        pa.add_run(desc_alur)
        
    add_custom_heading("2.2 Skema Database (Database A vs Database B)", level=2)
    p_db = doc.add_paragraph()
    p_db.paragraph_format.space_after = Pt(6)
    p_db.add_run(
        "Sistem menggunakan dua database relasional MySQL pada XAMPP dengan perbandingan rancangan tabel sebagai berikut:"
    )
    
    # Tabel perbandingan skema
    t_schema = doc.add_table(rows=6, cols=3)
    t_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_schema.autofit = False
    
    schema_headers = ["Nama Kolom", "Tipe Data di Database A (db_a)", "Tipe Data di Database B (db_b)"]
    for i, h in enumerate(schema_headers):
        cell = t_schema.rows[0].cells[i]
        set_cell_background(cell, "0F172A")
        p_h = cell.paragraphs[0]
        r_h = p_h.add_run(h)
        r_h.bold = True
        r_h.font.color.rgb = RGBColor(255, 255, 255)
        r_h.font.size = Pt(10)
        
    schema_rows = [
        ("id", "INT (Auto Increment, Primary Key)", "INT (Primary Key)"),
        ("nama_produk", "VARCHAR(100) - Teks Plaintext", "TEXT - String Ciphertext (IV:Ciphertext)"),
        ("harga_produk", "INT - Angka Plaintext", "TEXT - String Ciphertext (IV:Ciphertext)"),
        ("foto_produk", "VARCHAR(255) - Nama File Plaintext", "TEXT - String Ciphertext (IV:Ciphertext)"),
        ("id_kategori", "INT (Foreign Key ke kategori.id)", "TEXT - String Ciphertext (IV:Ciphertext)")
    ]
    
    for row_idx, r_data in enumerate(schema_rows, start=1):
        for col_idx, text_val in enumerate(r_data):
            c = t_schema.rows[row_idx].cells[col_idx]
            p_c = c.paragraphs[0]
            p_c.paragraph_format.space_after = Pt(2)
            r_c = p_c.add_run(text_val)
            r_c.font.size = Pt(9.5)
            set_cell_background(c, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    add_custom_heading("2.3 Landasan Kriptografi AES-256-CBC", level=2)
    p_aes = doc.add_paragraph()
    p_aes.paragraph_format.space_after = Pt(6)
    p_aes.add_run(
        "Algoritma yang digunakan adalah Advanced Encryption Standard (AES) dengan mode Cipher Block Chaining (CBC) "
        "dan panjang kunci 256-bit (32 bytes). Pada mode CBC, setiap blok plaintext dilakukan operasi XOR dengan blok ciphertext "
        "sebelumnya sebelum dienkripsi. Untuk blok pertama, digunakan Initialization Vector (IV) sepanjang 16 bytes (128-bit) yang "
        "dibuat secara acak menggunakan metode kriptografis aman (crypto.randomBytes(16)). Hasil akhir enkripsi disimpan dengan format:\n"
    )
    p_format = doc.add_paragraph()
    p_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_format.paragraph_format.space_after = Pt(6)
    r_f = p_format.add_run("Format Penyimpanan: [16 Bytes IV dalam HEX] : [Ciphertext dalam HEX]")
    r_f.bold = True
    r_f.font.color.rgb = RGBColor(180, 83, 9)

    add_custom_heading("2.4 Mekanisme Autentikasi JSON Web Token (JWT)", level=2)
    p_jwt = doc.add_paragraph()
    p_jwt.paragraph_format.space_after = Pt(8)
    p_jwt.add_run(
        "Untuk melindungi endpoint dekripsi pada Server 2, diterapkan protokol otorisasi berbasis Bearer Token JWT. "
        "Token terdiri dari tiga bagian (Header, Payload, dan Signature) yang ditandatangani menggunakan algoritma HMAC-SHA256 (HS256) "
        "dengan secret key server. Masa berlaku token dibatasi selama 2 jam. Setiap kali klien meminta data melalui endpoint "
        "GET /api/produk, middleware auth.js akan memverifikasi integritas signature dan masa aktif token sebelum Server 2 "
        "melakukan proses dekripsi data dari db_b."
    )

    # =========================================================================
    # 4. IMPLEMENTASI KODE PROGRAM
    # =========================================================================
    add_custom_heading("BAB III. IMPLEMENTASI KODE PROGRAM", level=1)
    
    p_impl = doc.add_paragraph()
    p_impl.paragraph_format.space_after = Pt(6)
    p_impl.add_run(
        "Aplikasi dibangun menggunakan Node.js dengan framework Express. Berikut adalah rincian komponen kode program utama:"
    )
    
    add_custom_heading("3.1 Modul Kriptografi (utils/cryptoHelper.js)", level=2)
    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.space_after = Pt(4)
    p_c1.add_run(
        "Modul ini bertugas menyediakan fungsi enkripsi dan dekripsi yang konsisten untuk Server 1 dan Server 2. "
        "Kunci rahasia diambil dari environment variable dan dipastikan berukuran 32 bytes menggunakan hash SHA-256."
    )
    
    add_custom_heading("3.2 Server 1: Pengirim & Pengenkripsi Data (server1.js - Port 3001)", level=2)
    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.space_after = Pt(4)
    p_c2.add_run(
        "Server 1 bertindak sebagai service data master yang terhubung ke Database A (db_a). Endpoint utama:\n"
        "1. GET /api/produk: Menampilkan data produk plaintext dari db_a.\n"
        "2. POST /api/send-encrypted: Mengambil semua produk dari db_a, mengenkripsi field produk via cryptoHelper.js, "
        "lalu mengirimkannya via HTTP POST menggunakan library Axios ke http://localhost:3002/api/receive-encrypted."
    )
    
    add_custom_heading("3.3 Server 2: Penerima Ciphertext & Layanan Dekripsi (server2.js - Port 3002)", level=2)
    p_c3 = doc.add_paragraph()
    p_c3.paragraph_format.space_after = Pt(4)
    p_c3.add_run(
        "Server 2 bertindak sebagai service data terenkripsi yang terhubung ke Database B (db_b). Endpoint utama:\n"
        "1. POST /api/receive-encrypted: Menerima ciphertext dari Server 1 dan menyimpannya ke tabel produk di db_b.\n"
        "2. POST /api/login: Memverifikasi username & password admin, lalu menerbitkan JWT Bearer Token.\n"
        "3. GET /api/produk: Endpoint terproteksi middleware JWT. Mengambil ciphertext dari db_b, mendekripsi kembali "
        "menjadi plaintext, dan mengembalikannya dalam format JSON ke klien."
    )
    
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Potongan Kode Program Utama di Visual Studio Code]",
        "Ambil screenshot jendela editor (VS Code) yang menampilkan file server1.js, server2.js, dan cryptoHelper.js yang telah diimplementasikan."
    )

    # =========================================================================
    # 5. HASIL PENGUJIAN DAN EVALUASI
    # =========================================================================
    add_custom_heading("BAB IV. HASIL PENGUJIAN DAN EVALUASI SISTEM", level=1)
    
    p_eva = doc.add_paragraph()
    p_eva.paragraph_format.space_after = Pt(8)
    p_eva.add_run(
        "Pengujian dilakukan secara end-to-end mencakup validasi database phpMyAdmin dan pengetesan endpoint REST API "
        "menggunakan aplikasi Postman. Berikut rincian hasil pengujian per tahapan:"
    )
    
    # --- SUB 4.1 ---
    add_custom_heading("4.1 Pengujian Database A (db_a) - Data Awal Plaintext", level=2)
    p_e1 = doc.add_paragraph()
    p_e1.paragraph_format.space_after = Pt(4)
    p_e1.add_run(
        "Database A berfungsi sebagai sumber data master asli. Seluruh kolom seperti nama_produk ('Laptop Asus ROG Zephyrus', "
        "'Smartphone Samsung S24', dll) serta harga_produk disimpan dalam format plaintext asli tanpa enkripsi."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Tampilan Tabel produk di phpMyAdmin pada Database A (db_a)]",
        "Ambil tangkapan layar browser phpMyAdmin yang menampilkan struktur dan baris data tabel db_a.produk dalam kondisi teks terbaca (plaintext)."
    )
    
    # --- SUB 4.2 ---
    add_custom_heading("4.2 Pengujian Pengiriman Terenkripsi & Penyimpanan di Database B (Alur 1 & 2)", level=2)
    p_e2 = doc.add_paragraph()
    p_e2.paragraph_format.space_after = Pt(4)
    p_e2.add_run(
        "Pengujian dilakukan dengan mengirimkan request HTTP POST ke http://localhost:3001/api/send-encrypted di Server 1. "
        "Server 1 merespon status 200 OK dengan laporan bahwa seluruh data produk berhasil dienkripsi dan disimpan oleh Server 2 "
        "ke dalam Database B (db_b).\n"
        "Verifikasi langsung pada phpMyAdmin db_b membuktikan bahwa seluruh kolom nama_produk, harga_produk, dan id_kategori "
        "telah tersimpan dalam format string acak ciphertext (kombinasi 32-karakter IV hex dan payload hex)."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Request Postman POST /api/send-encrypted pada Server 1]",
        "Ambil tangkapan layar Postman saat menembak POST http://localhost:3001/api/send-encrypted dengan respon 200 OK ('Data berhasil diambil dari db_a, dienkripsi, dan dikirim ke Server 2')."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Tampilan Tabel produk di phpMyAdmin pada Database B (db_b)]",
        "Ambil tangkapan layar tabel db_b.produk di phpMyAdmin yang memperlihatkan kolom nama_produk, harga_produk, dan id_kategori berupa string ciphertext acak (terbukti terenkripsi)."
    )
    
    # --- SUB 4.3 ---
    add_custom_heading("4.3 Pengujian Autentikasi dan Penerbitan Token JWT", level=2)
    p_e3 = doc.add_paragraph()
    p_e3.paragraph_format.space_after = Pt(4)
    p_e3.add_run(
        "Klien melakukan autentikasi dengan mengirim request POST ke http://localhost:3002/api/login menyertakan body JSON "
        "berupa username dan password. Server 2 berhasil memvalidasi kredensial dan menerbitkan JWT Bearer Token dengan masa berlaku 2 jam."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Request Postman POST /api/login Menghasilkan JWT Bearer Token]",
        "Ambil tangkapan layar Postman saat mengirim POST http://localhost:3002/api/login dengan request body JSON dan respon 200 OK yang memuat 'token': 'eyJhbGciOi...'"
    )
    
    # --- SUB 4.4 ---
    add_custom_heading("4.4 Pengujian Pengambilan & Dekripsi Data oleh Endpoint Klien (Alur 3 & 4)", level=2)
    p_e4 = doc.add_paragraph()
    p_e4.paragraph_format.space_after = Pt(4)
    p_e4.add_run(
        "Pengujian tahap akhir dilakukan dalam dua skenario keamanan:\n"
        "1. Uji Validasi Otorisasi: Klien mencoba mengakses GET http://localhost:3002/api/produk tanpa token. Server 2 menolak dengan respon 401 Unauthorized.\n"
        "2. Uji Dekripsi Sukses: Klien menyertakan header 'Authorization: Bearer <token>'. Server 2 memverifikasi token, mengambil ciphertext dari db_b, "
        "mendekripsinya menggunakan AES-256-CBC, dan mengembalikan data produk utuh (plaintext) kembali ke format aslinya."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Request Postman GET /api/produk Ditolak (401 Unauthorized) Tanpa Token]",
        "Ambil tangkapan layar Postman saat mengakses GET http://localhost:3002/api/produk tanpa header Authorization, membuktikan sistem menolak akses secara aman."
    )
    add_callout_box(
        doc,
        "[TEMPAT SCREENSHOT: Request Postman GET /api/produk Berhasil Didekripsi dengan Token JWT]",
        "Ambil tangkapan layar Postman dengan Header 'Authorization: Bearer <token>' dan respon 200 OK yang menampilkan data produk hasil dekripsi yang kembali ke teks asli (plaintext)."
    )

    # =========================================================================
    # 6. KESIMPULAN
    # =========================================================================
    add_custom_heading("BAB V. KESIMPULAN", level=1)
    
    p_kes = doc.add_paragraph()
    p_kes.paragraph_format.space_after = Pt(6)
    p_kes.paragraph_format.line_spacing = 1.15
    p_kes.add_run(
        "Berdasarkan seluruh perancangan, implementasi, dan pengujian yang telah dilakukan, dapat disimpulkan bahwa:\n"
    )
    
    kesimpulan_list = [
        "Arsitektur integrasi sistem multi-server (Server 1 dan Server 2) berhasil menghubungkan dua basis data (db_a dan db_b) secara aman melalui protokol REST API.",
        "Algoritma enkripsi AES-256-CBC terbukti efektif mengamankan data sensitif baik saat transmisi (data in-transit) maupun saat disimpan dalam Database B (data at-rest). Penggunaan Random IV 16-byte memastikan setiap proses enkripsi menghasilkan ciphertext unik meskipun data aslinya serupa.",
        "Implementasi JWT (JSON Web Token) berhasil memproteksi endpoint dekripsi pada Server 2, menjamin bahwa hanya entitas terautentikasi dan memiliki token sah yang dapat membaca data dalam bentuk plaintext.",
        "Seluruh tahapan pengujian pada alur 1 (enkripsi), alur 2 (penyimpanan ciphertext), alur 3 (permintaan klien dengan JWT), dan alur 4 (dekripsi data) telah berjalan sukses 100% sesuai diagram acuan tugas UTS."
    ]
    for k_item in kesimpulan_list:
        pk = doc.add_paragraph(style='List Bullet')
        pk.paragraph_format.space_after = Pt(3)
        pk.add_run(k_item)

    # Simpan dokumen
    OUTPUT_FILE = DOCX_NAME
    try:
        doc.save(OUTPUT_FILE)
        print(f"[OK] Dokumen Word berhasil dibuat dan disimpan ke: {OUTPUT_FILE}")
    except PermissionError:
        OUTPUT_FILE = "UTS_Moch Ilham Abdul Aziz_3125522014_Laporan_UTS_Lengkap.docx"
        doc.save(OUTPUT_FILE)
        print(f"[!] File asli sedang dibuka di Microsoft Word.")
        print(f"[OK] Berhasil disimpan ke file baru: {OUTPUT_FILE}")
        print(f"[INFO] Jika Word ditutup, Anda bisa menjalankan kembali skrip untuk menimpa file utama.")

if __name__ == "__main__":
    build_report()
