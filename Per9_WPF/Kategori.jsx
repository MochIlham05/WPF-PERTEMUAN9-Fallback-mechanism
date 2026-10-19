import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Kategori() {
  const [kategori, setkategori] = useState([]);
  const [sourceServer, setSourceServer] = useState('');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // 1. Request HTTP GET ke Server Utama
    axios.get('http://localhost:4000/api/kategori/')
      .then((res) => {
        // 2. Jika server utama merespons, simpan data ke state 'kategori'
        console.log('Berhasil mengambil data dari Server Utama (Port 4000):', res.data);
        const data = Array.isArray(res.data) ? res.data : (res.data.data || []);
        setkategori(data);
        setSourceServer('Server Utama (http://localhost:4000)');
        setLoading(false);
      })
      .catch((err) => {
        // 3. Fallback Mechanism: Jika server utama gagal, request ke server cadangan di dalam .catch()
        console.warn('Server utama gagal/tidak merespons. Beralih ke server cadangan...');

        axios.get('http://localhost:3100/apiserverb/kategori/')
          .then((res) => {
            // 4. Jika server cadangan berhasil, simpan datanya ke state 'kategori'
            console.log('Berhasil mengambil data dari Server Cadangan (Port 3100):', res.data);
            const data = Array.isArray(res.data) ? res.data : (res.data.data || []);
            setkategori(data);
            setSourceServer('Server Cadangan (http://localhost:3100)');
            setLoading(false);
          })
          .catch((err) => {
            // 5. Jika kedua server gagal, tampilkan pesan error di console
            console.error('Kedua server gagal:', err);
            setErrorMsg('Kedua server (Utama & Cadangan) gagal merespons.');
            setLoading(false);
          });
      });
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Daftar Kategori</h2>

      {sourceServer && (
        <div style={{
          marginBottom: '15px',
          padding: '10px 14px',
          backgroundColor: '#e6fffa',
          border: '1px solid #38b2ac',
          borderRadius: '6px',
          color: '#234e52'
        }}>
          <strong>Status Sumber:</strong> Data berhasil dimuat dari <u>{sourceServer}</u>
        </div>
      )}

      {errorMsg && (
        <div style={{
          marginBottom: '15px',
          padding: '10px 14px',
          backgroundColor: '#fff5f5',
          border: '1px solid #feb2b2',
          borderRadius: '6px',
          color: '#9b2c2c'
        }}>
          <strong>Peringatan:</strong> {errorMsg}
        </div>
      )}

      {loading ? (
        <p>Memuat data kategori...</p>
      ) : (
        <table border="1" cellPadding="10" cellSpacing="0" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead style={{ backgroundColor: '#f2f2f2' }}>
            <tr>
              <th style={{ width: '80px' }}>ID</th>
              <th>Nama Kategori</th>
            </tr>
          </thead>
          <tbody>
            {Array.isArray(kategori) && kategori.length > 0 ? (
              kategori.map((item, index) => (
                <tr key={item.id_kategori || item.id || index}>
                  <td>{item.id_kategori || item.id || index + 1}</td>
                  <td>{item.nama_kategori || item.nama}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="2" style={{ textAlign: 'center', color: '#888' }}>
                  Tidak ada data kategori yang tersedia.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Kategori;
