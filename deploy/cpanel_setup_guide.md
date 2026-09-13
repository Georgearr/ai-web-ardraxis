# Panduan Deploy ke Hosting cPanel (Setup Python App)

Panduan ini menjelaskan cara melakukan hosting aplikasi **DRAX (ARDRAXIS)** di cPanel menggunakan fitur **Setup Python App** tanpa memerlukan runtime Node.js di server.

---

## Langkah 1: Upload File ke Hosting

1. Upload seluruh file project atau hubungkan via Git repository ke folder domain/subdomain di hosting Anda (misal: `/home/username/public_html` atau `/home/username/draxis`).
2. Pastikan file `app.py`, `passenger_wsgi.py`, dan `requirements.txt` berada di root folder project Anda.

---

## Langkah 2: Buat Aplikasi di Setup Python App

1. Login ke **cPanel**.
2. Cari dan buka menu **Setup Python App** (berada di kategori *Software*).
3. Klik tombol **Create Application**.
4. Isi formulir setup sebagai berikut:
   - **Python version**: Pilih `3.10`, `3.11`, atau `3.12`.
   - **Application root**: Isi nama folder lokasi project Anda (misal: `draxis` atau `public_html`).
   - **Application URL**: Pilih domain / subdomain Anda.
   - **Application startup file**: Ketik `app.py`
   - **Application Entry point**: Ketik `app` (atau `application`)
5. Klik **Create**.

---

## Langkah 3: Install Dependency Python (`requirements.txt`)

1. Setelah aplikasi dibuat, cPanel akan menampilkan baris perintah virtual environment di bagian atas, contoh:
   ```bash
   source /home/username/virtualenv/draxis/3.11/bin/activate && cd /home/username/draxis
   ```
2. Buka **Terminal** di cPanel (atau via SSH).
3. Paste & jalankan perintah dari cPanel tersebut untuk masuk ke virtual environment.
4. Jalankan perintah instalasi dependency:
   ```bash
   pip install -r requirements.txt
   ```

---

## Langkah 4: Atur Environment Variables (`.env`)

1. Buat atau ubah file `.env` di root folder project (atau di folder `backend/`).
2. Masukkan kredensial API Anda:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=0
   PORT=5001
   SECRET_KEY=ganti-dengan-secret-key-acak

   AI_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-xxxx...
   OPENROUTER_API_KEY=sk-or-xxxx...
   OPENAI_API_KEY=sk-xxxx...
   GEMINI_API_KEY=AIzaSy...
   ```

---

## Langkah 5: Restart Application

1. Kembali ke menu **Setup Python App** di cPanel.
2. Klik tombol **Restart Application**.
3. Buka domain Anda di browser:
   - `https://domainanda.com/` $\rightarrow$ Landing Page ARDRAXIS
   - `https://domainanda.com/chat` $\rightarrow$ Interface D'RAX Chat
   - `https://domainanda.com/api/v1/health` $\rightarrow$ API Health Check

---

## Troubleshoot

- **Error 500 / Internal Server Error**:
  Buka file `backend/app.log` atau error log cPanel untuk melihat detail pesan kesalahan.
- **Dependency Missing**:
  Pastikan sudah menjalankan `pip install -r requirements.txt` di terminal cPanel.
