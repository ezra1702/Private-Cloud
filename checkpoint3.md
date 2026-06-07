# checkpoint3.md - Laporan Pengujian Sistem
**Mata Kuliah**: Administrasi Sistem Server  
**Judul Proyek**: Rancang Bangun Platform Enterprise Private Cloud Storage Berbasis Nextcloud dengan Integrasi Object Storage MinIO, Caching Redis, Keamanan SSL/TLS, dan High Availability Terotomatisasi Menggunakan Ansible Playbook Berbasis Docker Container pada WSL2  
**Distribusi Langkah**: 15 Langkah terbagi dalam 3 Blok Utama  

---

> [!IMPORTANT]
> Seluruh langkah pengujian di bawah ini dilakukan langsung di dalam lingkungan **Windows Subsystem for Linux 2 (WSL2)** yang terintegrasi dengan browser Windows Host pada alamat `localhost`. Pengujian dirancang untuk memverifikasi fungsionalitas, otomatisasi, dan ketahanan sistem (High Availability).

---

## BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI

Blok ini memverifikasi kesiapan lingkungan, keberhasilan skrip otomatisasi Ansible Playbook (`site.yml`), serta stabilitas penanganan kontainer Docker.

### Langkah 1: Pengujian Deployment Otomatis Menggunakan Ansible
* **Tujuan**: Memastikan Ansible Playbook `site.yml` dapat mengeksekusi semua task tanpa kegagalan (`failed=0`), menginstal Docker, membuat sertifikat SSL, dan meluncurkan kontainer stack di localhost WSL2 secara otomatis.
* **Langkah**: Menjalankan skrip playbook dari terminal WSL2.
* **Input**: Eksekusi perintah `ansible-playbook -i inventory.ini site.yml`.
* **Langkah Pengujian**:
  1. Masuk ke terminal WSL2 Ubuntu.
  2. Navigasi ke folder proyek: `cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/ansible"`.
  3. Jalankan perintah deployment: `ansible-playbook -i inventory.ini site.yml`.
  4. Amati baris output rekapitulasi di akhir tugas (*PLAY RECAP*).
* **Output yang Diharapkan**: Semua langkah (tugas 1 hingga 8) menampilkan status `ok` atau `changed`. Di akhir eksekusi, log rekap menampilkan status: `localhost : ok=X changed=Y unreachable=0 failed=0`.
* **Hasil**: **SUKSES**
* **Analisis**: Ansible dapat mengeksekusi playbook lokal menggunakan parameter `ansible_connection=local` secara lancar tanpa hambatan autentikasi SSH. Semua direktori `/opt/private-cloud` berhasil dibuat dan dipasangi konfigurasi yang tepat.

### Langkah 2: Pengujian Keaktifan Docker Container
* **Tujuan**: Memastikan seluruh kontainer mikroservis (HAProxy, Nextcloud 1 & 2, Database, Redis, MinIO, Prometheus, Grafana) berhasil dinyalakan oleh Ansible dan berjalan aktif pada satu virtual network bridge.
* **Langkah**: Memeriksa daftar status kontainer yang sedang berjalan melalui Docker CLI.
* **Input**: Eksekusi perintah `docker compose ps` pada direktori target.
* **Langkah Pengujian**:
  1. Buka terminal WSL2.
  2. Jalankan perintah: `docker compose -f /opt/private-cloud/docker/docker-compose.yml ps`.
* **Output yang Diharapkan**: List menampilkan 8 container berikut dengan status `Up` atau `running`:
  - `haproxy-lb` (ports 80->80, 443->443)
  - `nextcloud-app-1` (port internal 80)
  - `nextcloud-app-2` (port internal 80)
  - `mariadb-db` (port internal 3306)
  - `redis-cache` (port internal 6379)
  - `minio-storage` (port 9001->9001)
  - `prom-server` (port internal 9090)
  - `grafana-dash` (port 3000->3000)
* **Hasil**: **SUKSES**
* **Analisis**: Seluruh *container image* berhasil diunduh dan dideploy sesuai spesifikasi file Docker Compose. Port mapping untuk layanan luar (LB, MinIO Console, Grafana) terpetakan dengan benar ke host.

### Langkah 3: Pengujian Restart Container
* **Tujuan**: Memverifikasi ketahanan data relasional dan cache (data persistence) ketika kontainer database MariaDB dan cache Redis dihentikan dan dijalankan kembali.
* **Langkah**: Melakukan restart paksa pada database dan Redis, lalu memeriksa integritas data.
* **Input**: Eksekusi command `docker restart mariadb-db redis-cache`.
* **Langkah Pengujian**:
  1. Di terminal WSL2, ketik: `docker restart mariadb-db redis-cache`.
  2. Buka status kontainer: `docker ps` untuk memastikan container up kembali.
  3. Cek log MariaDB menggunakan: `docker logs mariadb-db`.
  4. Lakukan reload pada halaman Nextcloud di browser untuk memverifikasi database siap menerima kueri.
* **Output yang Diharapkan**: Kedua container kembali aktif dalam beberapa detik. Log MariaDB menunjukkan kesiapan database: `ready for connections`. Sesi pengguna di Nextcloud tetap aktif dan tidak terjadi *corruption* pada database.
* **Hasil**: **SUKSES**
* **Analisis**: Mekanisme penyimpanan persistent volume yang dipetakan ke direktori lokal host WSL2 (`/opt/private-cloud/mariadb` dan `/opt/private-cloud/redis`) berfungsi dengan benar untuk menjaga konsistensi data melintasi siklus hidup kontainer.

---

## BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER

Blok ini memverifikasi berjalannya fitur fungsional Nextcloud, otentikasi akun, pemisahan hak akses, manajemen kuota, dan sinkronisasi file pada object storage.

### Langkah 4: Pengujian Akses Web Nextcloud (HTTPS)
* **Tujuan**: Memastikan pengguna dapat mengakses antarmuka Nextcloud melalui protokol aman HTTPS (port 443) dengan SSL/TLS termination yang ditangani oleh HAProxy.
* **Langkah**: Mengakses Nextcloud menggunakan browser pada Windows Host.
* **Input**: Request HTTPS ke `https://localhost`.
* **Langkah Pengujian**:
  1. Buka browser (Chrome/Firefox/Edge) di Windows Host.
  2. Ketik alamat URL: `https://localhost` dan tekan Enter.
  3. Lewati peringatan keamanan SSL self-signed (klik *Advanced* -> *Proceed to localhost*).
* **Output yang Diharapkan**: Antarmuka web menampilkan form login Nextcloud. Lambang gembok terkunci muncul di address bar browser menandakan HTTPS aktif.
* **Hasil**: **SUKSES**
* **Analisis**: Sertifikat SSL self-signed (`haproxy.pem`) yang dibuat otomatis oleh Ansible berhasil dibaca dan diproses oleh HAProxy. Mekanisme pengalihan otomatis HTTP ke HTTPS pada port 80 juga terverifikasi bekerja.

### Langkah 5: Pengujian Login Administrator
* **Tujuan**: Memverifikasi pengguna dengan hak akses tingkat tinggi (Admin) dapat masuk ke sistem dan mengelola konfigurasi global Nextcloud.
* **Langkah**: Memasukkan username dan password administrator pada form login.
* **Input**: Username `admin` dan password `adminrootpassword`.
* **Langkah Pengujian**:
  1. Pada form login Nextcloud, masukkan username `admin`.
  2. Masukkan password `adminrootpassword`.
  3. Klik tombol *Log in*.
* **Output yang Diharapkan**: Halaman beranda Admin terbuka. Di kanan atas antarmuka, tombol akses menu *Settings* untuk konfigurasi sistem global terlihat aktif dan dapat diklik.
* **Hasil**: **SUKSES**
* **Analisis**: Nextcloud berhasil terhubung ke basis data MariaDB terpusat untuk memvalidasi kredensial administrator. Sesi berhasil disimpan di cache memori Redis.

#### Langkah 6: Pengujian Pembuatan User Baru dan Grup
* **Tujuan**: Memastikan Administrator dapat menambah akun pengguna baru, memasukkannya ke dalam grup tertentu, dan menyetel kuota penyimpanan data.
* **Langkah**: Menambahkan user `engineer1` (Grup Engineer, 10 GB), `finance1` (Grup Finance, 5 GB), `hrd1` (Grup HRD Manager, 15 GB), `developer1` (Grup Developer, 20 GB), dan `manager1` (Grup Manager, 25 GB) menggunakan panel admin.
* **Input**: Data user baru (username: `engineer1`, `finance1`, `hrd1`, `developer1`, & `manager1`).
* **Langkah Pengujian**:
  1. Login menggunakan akun `admin`.
  2. Buka menu avatar di pojok kanan atas, lalu klik *Users*.
  3. Tambahkan/buat grup `Engineer`, `Finance`, `HRD Manager`, `Developer`, dan `Manager`.
  4. Buat user `engineer1` dengan grup `Engineer` dan kuota `10 GB`.
  5. Buat user `finance1` dengan grup `Finance` dan kuota `5 GB`.
  6. Buat user `hrd1` dengan grup `HRD Manager` dan kuota `15 GB`.
  7. Buat user `developer1` dengan grup `Developer` dan kuota `20 GB`.
  8. Buat user `manager1` dengan grup `Manager` dan kuota `25 GB`.
* **Output yang Diharapkan**: Kelima akun terdaftar dalam sistem dan muncul di daftar user dengan alokasi kuota yang sesuai.
* **Hasil**: **SUKSES**
* **Analisis**: Nextcloud berhasil mengirim kueri `INSERT` ke MariaDB untuk mendaftarkan akun baru. Pembatasan kuota disk akan dibaca secara dinamis.

### Langkah 7: Pengujian Login User Biasa
* **Tujuan**: Memverifikasi pengguna non-admin dapat login dan diarahkan ke lingkungan penyimpanan file yang terisolasi dari administrator.
* **Langkah**: Login menggunakan kredensial `engineer1` dan `finance1`.
* **Input**: Username `engineer1` dan passwordnya.
* **Langkah Pengujian**:
  1. Klik tombol *Log out* pada akun Admin.
  2. Masukkan username `engineer1` dan password di form login.
  3. Klik *Log in*.
* **Output yang Diharapkan**: Dashboard pengguna biasa terbuka. Menu administrasi global (seperti Settings Admin) tidak ditampilkan di bilah navigasi.
* **Hasil**: **SUKSES**
* **Analisis**: Nextcloud berhasil membatasi hak akses berdasarkan tingkat peran pengguna (*user role*), menjaga keamanan sistem.

### Langkah 8: Pengujian Upload File
* **Tujuan**: Memverifikasi bahwa file yang diunggah pengguna berhasil disimpan secara *stateless* ke dalam bucket MinIO menggunakan API S3.
* **Langkah**: Mengunggah berkas dari folder lokal klien ke cloud storage.
* **Input**: File `Laporan_Kelistrikan1.txt`.
* **Langkah Pengujian**:
  1. Login sebagai `engineer1`.
  2. Klik ikon (+) di panel navigasi Nextcloud dan pilih *Upload file*.
  3. Pilih file `Laporan_Kelistrikan1.txt`.
  4. Buka tab baru di browser dan akses dashboard MinIO Console di `http://localhost:9001` untuk memeriksa isi bucket `nextcloud`.
* **Output yang Diharapkan**: Berkas muncul di antarmuka Nextcloud. Pada MinIO Console, di dalam bucket `nextcloud`, objek baru terkonfirmasi terbuat dan tersimpan.
* **Hasil**: **SUKSES**
* **Analisis**: Nextcloud sukses mengarahkan penulisan file biner ke MinIO via API S3. File tidak disimpan di *filesystem* kontainer lokal.

### Langkah 9: Pengujian Berbagi Tautan Publik (External Share)
* **Tujuan**: Memverifikasi bahwa pengguna dapat membuat tautan publik untuk membagikan file kepada pihak eksternal yang tidak memiliki akun.
* **Langkah**: `engineer1` membuat *Public Link* untuk laporan dan diakses dari luar.
* **Input**: Pembuatan *Share link* pada file `Laporan_Kelistrikan1.txt`.
* **Langkah Pengujian**:
  1. Di antarmuka Nextcloud, klik ikon *Share* pada file `Laporan_Kelistrikan1.txt`.
  2. Tambahkan *Share link* dan salin URL yang dihasilkan.
  3. Buka tab browser baru tanpa login (Incognito) dan akses URL tersebut.
* **Output yang Diharapkan**: Pihak eksternal dapat melihat isi dokumen teks secara langsung melalui browser tanpa autentikasi.
* **Hasil**: **SUKSES**
* **Analisis**: Fitur *Public Share* berfungsi sempurna melewati HAProxy Load Balancer, memungkinkan kolaborasi data dengan pihak luar sistem.

### Langkah 10: Pengujian Hapus File
* **Tujuan**: Memverifikasi fungsi penghapusan file bekerja dan membuang objek terkait dari penyimpanan *backend* MinIO.
* **Langkah**: Menghapus file dan memeriksa dampaknya di MinIO Console.
* **Input**: Aksi *Delete file* pada `Laporan_Kelistrikan1.txt`.
* **Langkah Pengujian**:
  1. Login ke Nextcloud. Klik ikon tiga titik pada file `Laporan_Kelistrikan1.txt` dan pilih *Delete file*.
  2. Buka menu *Deleted files* di pojok kiri bawah antarmuka Nextcloud.
  3. Cek kembali MinIO Console `http://localhost:9001` untuk melihat apakah objek masih ada.
* **Output yang Diharapkan**: File terhapus dari beranda utama, muncul di folder *Deleted files*, dan objek aslinya sudah tidak ditemukan (`0/0`) pada pencarian MinIO.
* **Hasil**: **SUKSES**
* **Analisis**: Proses penghapusan sukses menginstruksikan MariaDB untuk mengubah metadata file dan mengonfirmasi integrasi *stateless storage* bekerja dua arah.
---

## BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY

Blok ini memverifikasi keandalan load balancing HAProxy, ketahanan sistem terhadap crash (failover), dan pemulihan otomatis (recovery).

### Langkah 11: Pengujian Load Balancing
* **Tujuan**: Memastikan load balancer HAProxy aktif menerima koneksi eksternal dan mampu melacak status kesehatan kontainer Nextcloud di belakangnya secara real-time.
* **Langkah**: Mengakses portal monitoring statistik HAProxy.
* **Input**: Request HTTP ke port 1936 (`http://localhost:1936`).
* **Langkah Pengujian**:
  1. Buka browser di Windows Host.
  2. Akses alamat: `http://localhost:1936`.
  3. Masukkan username `admin` dan password `adminstats`.
* **Output yang Diharapkan**: Halaman statistik HAProxy terbuka. Pada bagian backend `nextcloud_backend`, server `app1` (`nextcloud-app-1`) dan `app2` (`nextcloud-app-2`) berstatus hijau (*Active / UP*).
* **Hasil**: **SUKSES**
* **Analisis**: HAProxy berhasil bertindak sebagai reverse proxy utama dan memonitor port HTTP kontainer backend melalui health check berkala.

### Langkah 12: Pengujian Round Robin
* **Tujuan**: Memverifikasi bahwa HAProxy mendistribusikan request klien baru secara bergantian (Round Robin) ke kontainer `nextcloud-app-1` dan `nextcloud-app-2`.
* **Langkah**: Mengirimkan request berulang tanpa cookie session (menggunakan mode Incognito/Private).
* **Input**: Akses web berulang kali dari tab Incognito yang berbeda.
* **Langkah Pengujian**:
  1. Buka browser di Windows Host.
  2. Buka jendela Incognito baru, aktifkan Developer Tools (F12) -> Application -> Cookies.
  3. Akses `https://localhost` dan amati nilai cookie `SERVERID` (`app1` atau `app2`).
  4. Tutup Incognito, buka Incognito baru, akses kembali `https://localhost`, dan periksa apakah nilai `SERVERID` berganti ke server backend lainnya.
* **Output yang Diharapkan**: Nilai cookie `SERVERID` berganti secara bergantian antara `app1` dan `app2` pada setiap sesi Incognito baru yang dibuka.
* **Hasil**: **SUKSES**
* **Analisis**: Algoritma Round Robin berjalan dengan sempurna membagi beban kerja secara adil di antara server replika backend.

### Langkah 13: Pengujian Failover Container
* **Tujuan**: Menguji kemampuan HAProxy untuk mendeteksi matinya kontainer aplikasi Nextcloud secara instan dan menghentikan pengiriman request ke kontainer yang down.
* **Langkah**: Mematikan paksa salah satu kontainer aplikasi Nextcloud.
* **Input**: Perintah `docker stop nextcloud-app-1`.
* **Langkah Pengujian**:
  1. Di terminal WSL2, jalankan: `docker stop nextcloud-app-1`.
  2. Buka halaman statistik HAProxy di `http://localhost:1936` secara cepat.
  3. Amati status server backend.
* **Output yang Diharapkan**: Dalam waktu kurang dari 3 detik, server `app1` di halaman statistik HAProxy berubah status menjadi merah (*DOWN*).
* **Hasil**: **SUKSES**
* **Analisis**: Konfigurasi parameter `check` pada backend HAProxy sukses melakukan polling TCP/HTTP secara berkala untuk memverifikasi keaktifan port backend.

### Langkah 14: Pengujian High Availability (HA)
* **Tujuan**: Memastikan pengguna tetap dapat menggunakan aplikasi (login, download, upload) tanpa downtime meskipun salah satu kontainer backend mati.
* **Langkah**: Mengakses dan melakukan upload file ketika `nextcloud-app-1` dalam kondisi *DOWN*.
* **Input**: Kondisi `nextcloud-app-1` mati, mengunggah file `Laporan_Staff.txt` menggunakan akun `developer1`.
* **Langkah Pengujian**:
  1. Pastikan status `nextcloud-app-1` masih mati (*DOWN*).
  2. Login menggunakan akun `developer1` di `https://localhost`.
  3. Lakukan pengunggahan berkas `Laporan_Staff.txt`.
  4. Cek apakah berkas berhasil terunggah dan status login Anda tidak terputus.
* **Output yang Diharapkan**: Nextcloud tetap merespon dengan cepat, proses upload berhasil 100% tanpa error, dan sesi login pengguna tidak keluar karena trafik secara otomatis dialihkan ke `nextcloud-app-2` yang aktif.
* **Hasil**: **SUKSES**
* **Analisis**: Mekanisme High Availability berhasil. Kombinasi in-memory Redis cache (menyimpan data sesi login user) dan MinIO (penyimpanan stateless bersama) membuat proses pemindahan beban trafik (failover) berjalan mulus tanpa kehilangan data sesi pengguna.

### Langkah 15: Pengujian Recovery Layanan
* **Tujuan**: Memastikan bahwa kontainer yang dinyalakan kembali secara otomatis dimasukkan kembali ke dalam daftar backend aktif oleh load balancer setelah lolos uji kesehatan.
* **Langkah**: Menyalakan kembali kontainer `nextcloud-app-1`.
* **Input**: Perintah `docker start nextcloud-app-1`.
* **Langkah Pengujian**:
  1. Di terminal WSL2, jalankan: `docker start nextcloud-app-1`.
  2. Buka dan pantau halaman statistik HAProxy `http://localhost:1936`.
* **Output yang Diharapkan**: Dalam waktu kurang dari 5 detik setelah kontainer menyala, status server `app1` di dashboard HAProxy berubah dari merah (*DOWN*) kembali menjadi hijau (*UP / Active*). Trafik kembali didistribusikan ke kontainer 1 secara normal.
* **Hasil**: **SUKSES**
* **Analisis**: Mekanisme auto-recovery HAProxy berjalan dengan benar sesuai parameter `rise 2` dan `inter 2000`, mengeliminasi intervensi manual administrator untuk memulihkan keutuhan sistem.

### Langkah 16: Pengujian Monitoring Sistem Menggunakan Prometheus
* **Tujuan**: Memastikan Prometheus active-scraping dan berhasil mengumpulkan metrik dari target (`prometheus` dan `haproxy`) secara real-time.
* **Langkah**: Mengakses halaman utama Prometheus Web UI pada port 9090 dan memverifikasi status target.
* **Input**: Request HTTP ke port 9090 (`http://localhost:9090`).
* **Langkah Pengujian**:
  1. Buka browser di Windows Host.
  2. Akses alamat: `http://localhost:9090`.
  3. Navigasi ke menu **Status** -> **Targets**.
  4. Amati status dari target `prometheus` dan `haproxy`.
* **Output yang Diharapkan**: Dashboard Prometheus berhasil terbuka. Halaman Targets menampilkan target `prometheus` dan `haproxy` dengan status **UP** (berwarna hijau).
* **Hasil**: **SUKSES**
* **Analisis**: Prometheus berhasil terintegrasi dengan load balancer HAProxy via HTTP basic authentication. Setelah mengaktifkan modul `prometheus-exporter` internal pada listener HAProxy port `1936` di `/metrics` dan menyuplai data otentikasi di `prometheus.yml`, status target monitoring untuk `haproxy` dan `prometheus` sukses terdeteksi dengan status **UP** (hijau) secara real-time.

### Langkah 17: Pengujian Monitoring Sistem Menggunakan Grafana
* **Tujuan**: Memastikan platform visualisasi monitoring Grafana aktif dan dapat diakses dari Windows Host untuk siap dihubungkan dengan data source Prometheus.
* **Langkah**: Mengakses halaman utama Grafana Dashboard pada port 3000.
* **Input**: Request HTTP ke port 3000 (`http://localhost:3000`).
* **Langkah Pengujian**:
  1. Buka browser di Windows Host.
  2. Akses alamat: `http://localhost:3000`.
  3. Masukkan username `admin` dan password `admin` (jika baru pertama kali login, ikuti instruksi ubah sandi atau lewati).
* **Output yang Diharapkan**: Dashboard Grafana berhasil terbuka dan menampilkan halaman beranda utama Grafana.
* **Hasil**: **SUKSES**
* **Analisis**: Antarmuka dashboard Grafana pada port 3000 dapat diakses dengan lancar dari Windows Host. Template dasbor Prometheus 2.0 Overview berhasil di-import dan terhubung ke datasource Prometheus secara otomatis. Grafik metrik (Uptime, Total Series, Upness) berhasil termuat secara real-time. Status N/A pada missed/skipped iterations adalah normal karena tidak ada error/missed scrapes yang terjadi pada server Prometheus, sementara metrik lainnya menunjukkan angka 0 yang mengonfirmasi kesehatan sistem 100% (sukses).
