# Panduan Menjalankan dan Mematikan Private Cloud (Nextcloud HA)

Dokumen ini berisi perintah-perintah dasar yang kamu butuhkan untuk menghidupkan (start), mematikan (stop/down), dan merestart sistem *Private Cloud* yang sudah kita bangun menggunakan Docker Compose.

---

## 1. Cara Menjalankan Sistem (Start)
Gunakan perintah ini ketika kamu baru menyalakan laptop/WSL dan ingin menghidupkan kembali server Nextcloud beserta seluruh komponennya (Load Balancer, Database, Cache, Storage).

1. Buka Terminal (WSL/Ubuntu).
2. Pindah ke direktori tempat file `docker-compose.yml` berada:
   ```bash
   cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/docker"
   ```
3. Jalankan perintah berikut:
   ```bash
   docker compose up -d
   ```
   *(Flag `-d` artinya detached mode, sistem akan berjalan di background sehingga terminal tetap bisa kamu gunakan untuk perintah lain).*

---

## 2. Cara Mematikan Sistem Sementara (Stop)
Gunakan perintah ini jika kamu ingin mematikan kontainer untuk sementara waktu (menghemat RAM/CPU laptop) tanpa menghapus *network* bawaannya.

1. Buka Terminal.
2. Pindah ke direktori docker:
   ```bash
   cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/docker"
   ```
3. Jalankan perintah stop:
   ```bash
   docker compose stop
   ```

---

## 3. Cara Mematikan Sistem Secara Penuh (Down)
Gunakan perintah ini jika kamu ingin menghentikan layanan sekaligus "merapikan" kontainer dan *network* virtual yang dibuat oleh Docker. 
**Jangan khawatir!** Data akun, file, dan database kamu **TETAP AMAN** karena kita sudah menggunakan *Docker Volumes* untuk persistensi data (kecuali kamu menggunakan flag `-v`, jangan gunakan flag itu jika ingin data aman).

1. Pindah ke direktori docker:
   ```bash
   cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/docker"
   ```
2. Jalankan perintah down:
   ```bash
   docker compose down
   ```

---

## 4. Cara Merestart Sistem (Restart)
Gunakan perintah ini jika Nextcloud terasa *error* atau kamu baru saja mengubah konfigurasi dan ingin memuat ulang (*reload*) sistemnya.

1. Pindah ke direktori docker:
   ```bash
   cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/docker"
   ```
2. Jalankan perintah restart:
   ```bash
   docker compose restart
   ```

---

## 5. Cara Cek Status Sistem (Logs & PS)
Untuk melihat kontainer apa saja yang sedang hidup dan berjalan:
```bash
cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/docker"
docker compose ps
```

Untuk melihat pesan *error* atau aktivitas *log* dari seluruh aplikasi:
```bash
docker compose logs -f
```
*(Tekan `Ctrl+C` untuk keluar dari tampilan log).*
