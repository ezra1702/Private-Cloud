# checkpoint1.md - Laporan Perancangan Proyek (Edisi Enterprise-Grade)
**Mata Kuliah**: Administrasi Sistem Server  
**Judul Proyek**: Rancang Bangun Platform Enterprise Private Cloud Storage Berbasis Nextcloud dengan Integrasi Object Storage MinIO, Caching Redis, Keamanan SSL/TLS, dan High Availability Terotomatisasi Menggunakan Ansible Roles Berbasis Docker Container pada WSL2  
**Lingkungan Simulasi**: Windows Subsystem for Linux 2 (WSL2) - Ubuntu 22.04 LTS (Tanpa VirtualBox)

> [!IMPORTANT]
> **5 Topik Utama Administrasi Sistem Server yang Diimplementasikan:**
> 1. **Docker – Kontainer**: Orkestrasi multi-kontainer Nextcloud, MariaDB, Redis, MinIO, Prometheus, dan Grafana.
> 2. **Web Server**: Konfigurasi reverse proxy SSL/TLS HTTPS pada HAProxy/Nginx.
> 3. **Manajemen User**: Manajemen otentikasi internal, grup, dan kuota penyimpanan pada Nextcloud.
> 4. **Infrastructure as Code (Ansible)**: Otomatisasi modular deployment menggunakan Ansible Playbook (hybrid task-file).
> 5. **High Availability (HA)**: Load balancing Round Robin, session stickiness, failover otomatis, dan stateless backend.
> *(Sesuai ketentuan, topik Virtualisasi fisik/VirtualBox dilewati (skip) dan difokuskan pada WSL2).*

---

## A. PERENCANAAN PROYEK

### 1. Judul
**"Rancang Bangun Platform Enterprise Private Cloud Storage Berbasis Nextcloud dengan Integrasi Object Storage MinIO, Caching Redis, Keamanan SSL/TLS, dan High Availability Terotomatisasi Menggunakan Ansible Roles Berbasis Docker Container pada WSL2"**

### 2. Latar Belakang
Teknologi penyimpanan awan privat (*private cloud storage*) telah menjadi standar kebutuhan institusi modern yang menuntut keamanan data tingkat tinggi, kepatuhan regulasi (*data residency*), serta efisiensi biaya. Nextcloud hadir sebagai solusi open-source terkemuka untuk kolaborasi dan penyimpanan file. Namun, penerapan Nextcloud dalam skala industri tidak bisa hanya mengandalkan arsitektur tunggal (*single instance*) karena rentan terhadap kegagalan perangkat keras/lunak dan penurunan performa saat diakses banyak pengguna secara bersamaan.

Untuk menaikkan kelas sistem dari tingkat dasar (*basic*) menjadi berstandar industri (*enterprise-grade*), rancangan proyek ini di-upgrade secara menyeluruh dengan mengintegrasikan lima konsep arsitektur mutakhir:
1. **Penyimpanan Terpisah (Stateless Application & Object Storage)**: Alih-alih menyimpan file langsung pada filesystem lokal kontainer (yang tidak skalabel), proyek ini mengintegrasikan **MinIO** sebagai penyimpanan objek S3-compatible lokal. Server Nextcloud menjadi sepenuhnya *stateless*, artinya data biner disimpan di MinIO dan metadata disimpan di MariaDB. Ini mempermudah replikasi server aplikasi Nextcloud tanpa takut terjadi ketidaksinkronan data filesystem lokal.
2. **Optimalisasi Kecepatan & Penguncian Transaksi (Caching & Locking)**: Penggunaan database relasional untuk menampung data session dan manajemen kunci file (*file locking*) sangat memperlambat respons aplikasi. Integrasi **Redis** bertindak sebagai in-memory database berkecepatan tinggi yang secara khusus menangani *transactional file locking* dan cache memori global, meminimalisir beban I/O pada database utama.
3. **Pengamanan Enkripsi End-to-End (SSL/TLS Termination)**: Keamanan transmisi data dijamin dengan mengimplementasikan SSL/TLS pada Load Balancer utama. Akses HTTP otomatis dialihkan (*redirect*) ke HTTPS menggunakan sertifikat SSL yang dideploy secara aman.
4. **Otomatisasi Infrastruktur Modular (Ansible Roles)**: Otomatisasi dengan Ansible ditingkatkan dari skrip tunggal (*monolithic playbook*) menjadi arsitektur modular berbasis **Ansible Roles**. Setiap modul (common, docker, ssl-cert, database, redis, minio, loadbalancer, nextcloud) didefinisikan secara terpisah, bersih, dan mengikuti praktik terbaik DevOps.
5. **Visibilitas Sistem (Monitoring & Observability)**: Penambahan stack pemantauan **Prometheus** dan **Grafana** memberikan administrator kemampuan untuk memantau penggunaan sumber daya CPU/RAM kontainer, statistik lalu lintas data, status ketersediaan (*uptime*), serta visualisasi metrik penting melalui dashboard interaktif.

#### Mengapa WSL2 (Bukan VirtualBox)?
Dalam proyek ini, penggunaan hypervisor tradisional seperti Oracle VM VirtualBox secara eksplisit **dihindari** karena:
- **Alokasi Memori Dinamis**: WSL2 menggunakan alokasi RAM dinamis. Ketika kontainer sedang idle, WSL2 mengembalikan memori RAM ke OS Windows, berbeda dengan VirtualBox yang menahan alokasi memori secara statis semenjak VM diaktifkan.
- **Efisiensi Kinerja**: Docker berjalan langsung di atas kernel Linux native bawaan WSL2 (menggunakan WSL2 backend), menghasilkan performa disk I/O dan jaringan yang setara dengan server fisik Linux, tanpa overhead emulasi hardware.
- **Port-Forwarding Otomatis**: Integrasi WSL2 memudahkan port yang diekspos kontainer Docker di WSL2 (seperti port 80, 443, 3000, dan 9001) langsung dipetakan dan dapat diakses dari browser Windows host melalui `localhost`.

### 3. Rumusan Masalah
1. Bagaimana mengonfigurasi dan mengintegrasikan ekosistem multi-kontainer (Nextcloud, MariaDB, Redis, MinIO, HAProxy, Prometheus, Grafana) ke dalam virtual network Docker bridge terisolasi di WSL2?
2. Bagaimana merancang konfigurasi *Primary Storage* pada Nextcloud agar terhubung ke API S3 milik kontainer MinIO secara *stateless* dan konsisten?
3. Bagaimana mengonfigurasi Load Balancer HAProxy untuk mengaktifkan enkripsi SSL/TLS, menolak request HTTP tidak aman (redirection ke HTTPS), dan memproses pembagian beban kerja berbasis Session Stickiness?
4. Bagaimana merancang skrip otomatisasi deployment berbasis Ansible Roles agar modular, *idempotent*, dan dapat dijalankan di target host localhost WSL2 tanpa menggunakan kata sandi manual?
5. Bagaimana mengimplementasikan sistem monitoring real-time menggunakan Prometheus dan Grafana untuk memantau metrik kontainer dan performa Load Balancer secara terpusat?

### 4. Tujuan
1. Membangun platform Enterprise Private Cloud Storage menggunakan Nextcloud yang berjalan di atas kontainer Docker pada lingkungan WSL2.
2. Mengintegrasikan Redis untuk penanganan memori cache dan mekanisme locking transaksi file Nextcloud.
3. Mengonfigurasi MinIO sebagai penyimpanan file utama bersertifikasi S3-compatible yang mendukung failover I/O data.
4. Mengamankan kanal komunikasi data menggunakan sertifikat SSL/TLS HTTPS pada Load Balancer utama.
5. Menyusun kode otomatisasi deployment terstruktur berbasis Ansible Roles.
6. Membangun dashboard visualisasi monitoring menggunakan Prometheus dan Grafana.

### 5. Manfaat
- **Bagi Mahasiswa**: Memperoleh pengalaman praktis tingkat lanjut dalam merancang sistem dengan arsitektur mikroservis modern, mengintegrasikan teknologi caching, object storage, enkripsi jaringan SSL, monitoring sistem, serta otomatisasi modular (Ansible Roles) di atas kernel Linux WSL2.
- **Bagi Institusi**: Menyediakan cetak biru arsitektur komputasi awan privat mandiri yang andal (*highly available*), terenkripsi aman (HTTPS), memiliki pemantauan visual, dan terotomatisasi secara instan untuk kebutuhan lab komputer atau server internal divisi.

### 6. Deskripsi Umum Sistem
Sistem yang dirancang adalah platform Enterprise Private Cloud Storage berbasis Nextcloud dengan redundansi ganda dan infrastruktur mandiri. Sistem berjalan di lingkungan WSL2 (Ubuntu 22.04 LTS) menggunakan orkestrasi kontainer Docker. 

Arsitektur sistem terdiri dari komponen berikut:
1. **Load Balancer (HAProxy/Nginx)**: Bertindak sebagai titik masuk utama (port 80 & 443). Komponen ini memegang sertifikat SSL/TLS, memproses dekripsi data (*SSL termination*), dan membagi request secara Round Robin ke dua replika server aplikasi Nextcloud. Pengguna yang mengakses via HTTP (port 80) akan otomatis diarahkan ke HTTPS (port 443).
2. **Replika Nextcloud (nextcloud-app-1 & nextcloud-app-2)**: Dua kontainer aplikasi web Nextcloud independen. Server aplikasi bersifat *stateless*; data sesi disimpan sementara pada Redis, berkas file disimpan pada MinIO, dan metadata disimpan pada MariaDB.
3. **Redis Caching & Locking**: Kontainer in-memory storage yang menangani manajemen sesi user dan *transactional file locking*. Redis memastikan transfer file tidak bentrok saat dua replika Nextcloud mengakses metadata secara paralel.
4. **MariaDB Database**: Menyimpan informasi relasional seperti data autentikasi user, riwayat aktivitas file, konfigurasi sistem, dan data penandaan (tags).
5. **MinIO Object Storage**: Menyediakan penyimpanan berbasis objek (S3-compatible) berkinerja tinggi sebagai tempat penyimpanan file utama dokumen Nextcloud. MinIO berjalan secara terisolasi dan menyimpan datanya pada disk lokal host yang dipasang secara persisten.
6. **Prometheus & Grafana (Monitoring)**: Prometheus bertindak sebagai penarik data metrik (*pull-based collector*) dari container stats dan HAProxy exporter. Grafana menampilkan grafik kinerja RAM, CPU, I/O disk, dan status ketersediaan sistem secara real-time.

### 7. Topik Mata Kuliah yang Digunakan dan Keterkaitannya dengan Proyek
Proyek ini mengimplementasikan secara mendalam 5 topik utama dari materi mata kuliah Administrasi Sistem Server, dengan membatasi maksimal 5 topik dan mengecualikan topik Virtualisasi secara fisik (VirtualBox) untuk memfokuskan seluruh simulasi pada WSL2:

1. **Docker – Kontainer**:
   - *Keterkaitan*: Merupakan fondasi utama untuk menjalankan seluruh microservices (Nextcloud, MariaDB, Redis, MinIO, HAProxy, Prometheus, Grafana) dalam kontainer terisolasi di WSL2. Menggunakan Docker Compose untuk orkestrasi multi-kontainer dan Docker Bridge Network untuk isolasi komunikasi antar-layanan.
2. **Web Server**:
   - *Keterkaitan*: Menggunakan Apache (yang dibundel di dalam kontainer Nextcloud) sebagai web server backend untuk mengeksekusi script PHP, serta mengonfigurasi HAProxy/Nginx sebagai reverse proxy eksternal yang menangani enkripsi SSL/TLS (HTTPS) dan pengalihan otomatis (*redirection*) port 80 ke 443.
3. **Manajemen User**:
   - *Keterkaitan*: Diimplementasikan melalui sistem autentikasi database internal Nextcloud untuk manajemen akun pengguna, pembagian hak akses berbasis grup (Admin, Engineer, Finance, HRD Manager, Developer, Manager), serta penerapan kuota penyimpanan disk (storage quota) guna membatasi kapasitas pengunggahan file ke MinIO.
4. **Infrastructure as Code (Ansible)**:
   - *Keterkaitan*: Digunakan untuk mengotomatisasi seluruh siklus hidup infrastruktur secara modular menggunakan struktur **Ansible Roles**. Ansible mengotomatisasi instalasi Docker, penyalinan file konfigurasi load balancer/database/monitoring, pembuatan direktori proyek, pembuatan sertifikat SSL self-signed, hingga peluncuran stack kontainer di target host WSL2.
5. **High Availability (HA)**:
   - *Keterkaitan*: Diimplementasikan melalui redundansi server aplikasi Nextcloud (dua kontainer aktif-aktif), load balancing Round Robin dengan cookie-based session stickiness pada HAProxy, serta pemisahan data aplikasi secara *stateless* menggunakan MinIO Object Storage dan Redis Cache/Lock untuk menjamin ketahanan sistem saat terjadi kegagalan node.

---

## B. ANALISIS SISTEM

### 1. Analisis Kebutuhan Fungsional
Kebutuhan fungsional sistem mencakup:
- **Autentikasi & Keamanan Sesi**:
  - Validasi login pengguna melalui database relasional terpusat.
  - Enkripsi SSL/TLS HTTPS pada layer akses browser untuk melindungi transfer kata sandi dan file.
  - Sesi login tetap aktif (*session persistence*) ketika trafik dialihkan antar replika aplikasi Nextcloud berkat konfigurasi `cookie SERVERID` pada Load Balancer.
- **Operasi File & Penyimpanan Stateless**:
  - File yang diunggah pengguna dialirkan via API S3 ke MinIO Object Storage, bukan ditulis ke folder lokal kontainer Nextcloud.
  - Mendukung operasi standar: unggah file besar, unduh file, pembuatan folder, pengubahan nama, dan penghapusan file.
  - Kecepatan penulisan file dibantu oleh Redis lock untuk mencegah bentrok modifikasi file simultan (*write collision*).
- **Manajemen User (Panel Admin)**:
  - Administrator dapat mengelola pembuatan akun baru, pembagian grup user, pembatasan kuota disk space, dan monitoring log Nextcloud.
- **High Availability & Failover Otomatis**:
  - Load balancer membagi trafik HTTP/HTTPS menggunakan algoritma Round Robin secara dinamis.
  - Jika salah satu kontainer Nextcloud mati, Load Balancer mendeteksi kegagalan tersebut dalam waktu kurang dari 3 detik dan menghentikan pengiriman request ke kontainer tersebut hingga kontainer aktif kembali.
- **Monitoring Visual**:
  - Menyediakan dashboard Grafana yang menampilkan penggunaan CPU, konsumsi RAM setiap kontainer, kapasitas penyimpanan disk MinIO, dan status kontainer.
- **Otomatisasi Modular**:
  - Proses deploy dilakukan secara otomatis melalui konfigurasi file Ansible Roles yang terbagi per layanan.

### 2. Analisis Kebutuhan Nonfungsional
- **Keamanan (Security)**: Enkripsi HTTPS wajib diaktifkan. Jaringan database, Redis, dan MinIO diisolasi dalam sub-net internal Docker bridge network, sehingga tidak dapat diakses langsung dari Windows host atau jaringan LAN publik (hanya port HAProxy, MinIO Console, dan Grafana yang dipetakan ke host).
- **Ketersediaan (Availability)**: Sistem dirancang tanpa SPoF pada lapisan aplikasi. Target toleransi kegagalan: Uptime layanan tetap 100% meskipun salah satu instansi Nextcloud mati.
- **Kinerja (Performance)**: Pemanfaatan Redis untuk caching memangkas latency akses dashboard Nextcloud di bawah 1 detik di lingkungan lokal.
- **Persistensi (Data Persistence)**: Semua data database MariaDB, data objek MinIO, sertifikat SSL, dan dashboard Grafana disimpan pada Docker Named Volume yang dipetakan ke penyimpanan persisten harddisk host.
- **Modularitas (Maintainability)**: Struktur kode Ansible terorganisir dengan arsitektur Roles yang memisahkan logic deklarasi antar service.

### 3. Analisis Pengguna Sistem
1. **System Administrator (SysAdmin)**:
   - Bertanggung jawab atas pengelolaan infrastruktur WSL2, orkestrasi kontainer Docker, dan deployment via skrip Ansible.
   - Memantau kondisi kesehatan server melalui dashboard Grafana dan log terpusat.
   - Mengelola kebijakan admin Nextcloud (user, group, kuota, integrasi aplikasi).
2. **End-User (Pengguna Biasa)**:
   - Mengakses platform cloud storage melalui antarmuka web yang aman (HTTPS) di browser Windows.
   - Mengelola berkas pribadi mereka sesuai batas kuota yang ditentukan administrator.

### 4. Analisis Infrastruktur
Deployment dijalankan secara terpusat pada host lokal menggunakan WSL2:
- **Hardware (Host PC)**:
  - CPU: Intel Core i5 / AMD Ryzen 5 (Minimum 4 Cores / 8 Threads)
  - RAM: 16 GB (Direkomendasikan agar alokasi RAM dinamis WSL2 dapat menjalankan multi-container stack yang mencakup Monitoring Prometheus-Grafana secara lancar).
  - Storage: SSD dengan ruang kosong minimal 20 GB.
- **Software**:
  - Windows 10/11 Home atau Pro dengan WSL2.
  - Linux Distro: Ubuntu 22.04 LTS terpasang di WSL2.
  - Docker Engine Community Edition v24.0+ & Docker Compose Plugin v2.20+.
  - Ansible Core v2.14+ terpasang di WSL2 Ubuntu.
  - **Docker Base Images**:
    - `haproxy:2.8-alpine` (Load balancer)
    - `nextcloud:apache` (Web engine & server aplikasi)
    - `mariadb:10.11` (Database relasional metadata)
    - `redis:7-alpine` (Cache & file locking)
    - `minio/minio:latest` (S3 Object Storage)
    - `prom/prometheus:latest` (Monitoring server)
    - `grafana/grafana:latest` (Monitoring dashboard)

---

## C. DESAIN SISTEM

### 1. Arsitektur Sistem
Menjelaskan bagaimana aliran lalu lintas data dan request pengguna masuk dari browser Windows, melewati Load Balancer SSL, menuju server aplikasi Nextcloud stateless, serta interaksinya dengan Redis dan MinIO.

```text
                     +-------------------------------------------------+
                     |                 Windows Host                    |
                     |           [ Web Browser (Chrome) ]              |
                     +--------------------+----------------------------+
                                          |
                                          | HTTPS (Port 443) / HTTP (Port 80)
                                          v
+-----------------------------------------+---------------------------------------------------+
| WSL2 (Ubuntu 22.04 LTS Engine)                                                              |
|                                                                                             |
|   +-------------------------------------------------------------------------------------+   |
|   | Docker Bridge Network: 'cloud-network' (172.20.0.0/16)                             |   |
|   |                                                                                     |   |
|   |                       +---------------------------------------+                     |   |
|   |                       |    [ haproxy-lb ] (IP: 172.20.0.2)    |                     |   |
|   |                       |    - SSL Termination (Decrypt HTTPS)  |                     |   |
|   |                       |    - Round Robin & Stickiness Cookie  |                     |   |
|   |                       +-------+-----------------------+-------+                     |   |
|   |                               |                       |                             |   |
|   |                 (Round Robin) |                       | (Round Robin)               |   |
|   |                               v                       v                             |   |
|   |                   +-----------+-----------+       +-----------+-----------+         |   |
|   |                   |  [ nextcloud-app-1 ]  |       |  [ nextcloud-app-2 ]  |         |   |
|   |                   |    (IP: 172.20.0.3)   |       |    (IP: 172.20.0.4)   |         |   |
|   |                   +-----+-------+-----+---+       +---+-------+-----+-----+         |   |
|   |                         |       |     |               |       |     |               |   |
|   |      +------------------+       |     +----------+----+       |     +--------+      |   |
|   |      |                          |                |            |              |      |   |
|   |      | SQL Query                | Redis Session  |            | SQL Query    |      |   |
|   |      | (Port 3306)              | & Lock (6379)  |            | (Port 3306)  |      |   |
|   |      |                          v                |            |              |      |   |
|   |      |                  +-------+-------+        |            |              |      |   |
|   |      |                  |   [ redis ]   |        |            |              |      |   |
|   |      |                  | (172.20.0.7)  |        |            |              |      |   |
|   |      |                  +---------------+        |            |              |      |   |
|   |      |                                           |            |              |      |   |
|   |      v                                           |            v              |      |   |
|   |   +--+------------+                              |         +--+------------+ |      |   |
|   |   | [mariadb-db]  |                              |         | [mariadb-db]  | |      |   |
|   |   | (172.20.0.5)  |                              |         | (172.20.0.5)  | |      |   |
|   |   +---------------+                              |         +---------------+ |      |   |
|   |                                                  |                           |      |   |
|   |                                                  v S3 API Request (Port 9000)|      |   |
|   |                                       +----------+-----------+               |      |   |
|   |                                       |   [ minio-storage ]  |               |      |   |
|   |                                       |    (IP: 172.20.0.6)  |               |      |   |
|   |                                       +----------+-----------+               |      |   |
|   |                                                  |                           |      |   |
|   +--------------------------------------------------|---------------------------+      |
|                                                      v                                  |
|                                   +------------------+------------------+               |
|                                   |        Persistent Local Host Disk   |               |
|                                   |  Mount Directory: /opt/private-cloud|               |
|                                   +-------------------------------------+               |
+---------------------------------------------------------------------------------------------+
```

### 2. Topologi Jaringan
Menampilkan pemetaan port eksternal yang diekspos ke Windows Host dan segmentasi IP internal dalam virtual network Docker bridge `cloud-network`.

```text
                                       [ WINDOWS CLIENT ]
                                                |
================================================|==================================== (WSL2 Boundary)
                                                | Port Mapping:
                                                | - Port 80/443 -> HAProxy LB
                                                | - Port 9001 -> MinIO Console
                                                | - Port 3000 -> Grafana Dashboard
                                                v
                                   +-------------------------+
                                   |   WSL2 Ethernet (eth0)  |
                                   |    (IP: 172.29.x.x)     |
                                   +------------+------------+
                                                |
================================================|==================================== (Docker Network)
                                                | Bridge Network (cloud-network)
                                                v
                                +---------------+---------------+
                                |     Docker Bridge Network     |
                                |        'cloud-network'        |
                                |      Subnet: 172.20.0.0/16    |
                                |      Gateway: 172.20.0.1      |
                                +---------------+---------------+
                                                |
   +----------+----------+----------+-----------+-----------+----------+----------+----------+
   |172.20.0.2|172.20.0.3|172.20.0.4|172.20.0.5 |172.20.0.6 |172.20.0.7|172.20.0.8|172.20.0.9|
   v          v          v          v           v           v          v          v          v
+----------+ +----------+ +----------+ +-----------+ +----------+ +----------+ +----------+ +----------+
|haproxy-lb| |nextcloud-| |nextcloud-| |mariadb-db | |  minio-  | |  redis-  | |prom-     | |grafana-  |
|          | |app-1     | |app-2     | |           | |storage   | |cache     | |server    | |dashboard |
|Port 80/  | |Port 80   | |Port 80   | |Port 3306  | |Port 9000/| |Port 6379 | |Port 9090 | |Port 3000 |
|443       | |          | |          | |           | |9001      | |          | |          | |          |
+----------+ +----------+ +----------+ +-----------+ +----------+ +----------+ +----------+ +----------+
```

### 3. Diagram Alur Sistem (Flowchart)
Menjelaskan logika penanganan request pengguna, proses pemeriksaan kesehatan kontainer oleh load balancer, autentikasi sesi, dan sinkronisasi penyimpanan file.

```text
               +-------------------+
               |       Mulai       |
               +---------+---------+
                         |
                         v
               +---------+---------+
               |  Request User ke  |
               |  https://localhost|
               +---------+---------+
                         |
                         v
               +---------+---------+
               |  SSL/TLS Handshake|
               |  di Load Balancer |
               +---------+---------+
                         |
                         v
               +---------+---------+
               |   Diterima oleh   |
               |  Load Balancer    |
               +---------+---------+
                         |
                         v
            { Cek Cookie SERVERID ada? }
             /                        \
         (Tidak)                      (Ya)
           /                            \
          v                              v
+---------+---------+          { Validasi Server Target }
| Pilih Server via  |          { (Sesuai Cookie ID)     }
| Round Robin       |           /                      \
+---------+---------+       (Aktif)                  (Mati)
          |                   /                          \
          v                  v                            v
   { Server Aktif? }---> [Kirim Trafik]         [Arahkan ke Server]
    /             \                             [Aktif Lainnya    ]
 (Ya)            (Tidak)                                 |
  /                 \                                    |
 v                   v                                   v
[Kirim Trafik]  [Tampilkan Error 503]            [Perbarui Cookie  ]
     |          [Service Unavailable]            [SERVERID         ]
     v                                                   |
[Proses PHP di]                                          |
[Nextcloud App]                                          |
     |                                                   |
     +-------------------+<------------------------------+
                         |
                         v
         { Cek Session Cache di Redis }
                         |
                         v
           { Halaman Login / Beranda }
                         |
             { Tindakan Pengguna: Upload }
                         |
                         v
           +-----------------------------+
           | 1. Simpan metadata ke DB    |
           |    (MariaDB)                |
           | 2. Kunci transaksi file     |
           |    di Redis Cache           |
           | 3. Upload file ke MinIO     |
           |    Object Storage (S3 API)  |
           +-----------------------------+
                         |
                         v
               +---------+---------+
               |      Selesai      |
               +-------------------+
```

### 4. Diagram Komunikasi Antar Komponen (Sequence Diagram)
Mengilustrasikan interaksi dinamis dan kronologis antar komponen sistem saat melayani permintaan unggah file.

```text
Klien (Browser)   HAProxy LB   Nextcloud App   Redis Cache   MariaDB DB   MinIO Storage
     |                |              |              |            |              |
     |--- 1. HTTPS -->|              |              |            |              |
     |   (Upload Req) |-- 2. HTTP -->|              |            |              |
     |                |  (Forward)   |              |            |              |
     |                |              |-- 3. Lock -> |            |              |
     |                |              |   (Acquire)  |            |              |
     |                |              |<- 4. Locked -|            |              |
     |                |              |              |            |              |
     |                |              |------------ 5. SQL Query -------------->|
     |                |              |             (Write metadata)             |
     |                |              |<----------- 6. Success Ack--------------|
     |                |              |              |            |              |
     |                |              |================ 7. PUT S3 API ==========>|
     |                |              |                 (Write Object Data)      |
     |                |              |<=============== 8. HTTP 200 OK ==========|
     |                |              |              |            |              |
     |                |              |-- 9. Unlock->|            |              |
     |                |              |   (Release)  |            |              |
     |                |              |<-10. Unlocked|            |              |
     |                |<-- 11. OK ---|              |            |              |
     |<--12. Success--|  (HTTP 201)  |              |            |              |
```

### 5. Diagram Input-Process-Output (IPO)
Pembagian masukan data, proses logis di tingkat kontainer, dan keluaran yang dihasilkan untuk arsitektur ini.

| Input | Process | Output |
| :--- | :--- | :--- |
| **1. Pengguna & Client**: <br>- Kredensial login (Username/Password).<br>- HTTP/HTTPS request.<br>- Berkas dokumen (Upload). | **1. Gateway & LB**: <br>- SSL Termination (Dekripsi TLS ke HTTP).<br>- Distribusi trafik via Round Robin.<br>- Pengecekan status kesehatan kontainer Nextcloud. | **1. Akses Pengguna**: <br>- Dashboard Nextcloud ter-render via HTTPS.<br>- Konsistensi sesi pengguna (tidak perlu login ulang). |
| **2. Kueri & Transaksi**: <br>- SQL queries.<br>- Token otentikasi.<br>- Request penguncian file. | **2. Aplikasi & Caching**: <br>- Autentikasi user via DB MariaDB.<br>- Transactional file locking di Redis.<br>- In-memory user cache di Redis.<br>- Pengiriman data via protokol S3. | **2. Penyimpanan**: <br>- Metadata terdaftar di MariaDB.<br>- File terunggah tersimpan sebagai Object di MinIO. |
| **3. Otomatisasi & Admin**: <br>- Perintah Ansible Playbook (`site.yml`).<br>- Metrik container yang ditarik oleh Prometheus. | **3. Monitoring & Otomasi**: <br>- Eksekusi provisioning Ansible berdasarkan peran (*Roles*).<br>- Penarikan data metrik kontainer oleh Prometheus.<br>- Visualisasi data pada Grafana. | **3. Status & Laporan**: <br>- Konfigurasi otomatis selesai.<br>- Dashboard monitoring Grafana aktif menampilkan data visual. |

### 6. Desain Manajemen User
- **Grup & Pembatasan Kuota**:
  - **Admin**: Memiliki kontrol penuh atas administrasi Nextcloud, konfigurasi plugin, pembuatan grup, dan user baru. Kuota: **Unlimited**.
  - **Regular User**: Terbagi menjadi grup `Engineer` (kuota: **10 GB**), `Finance` (kuota: **5 GB**), `HRD Manager` (kuota: **15 GB**), `Developer` (kuota: **20 GB**), dan `Manager` (kuota: **25 GB**). Ini membatasi volume file biner yang diunggah ke MinIO.
- **Otentikasi**:
  - Nextcloud memverifikasi username dan password terenkripsi dari tabel internal MariaDB.

### 7. Desain High Availability (HA) & Failover
- **Load Balancing**: HAProxy secara dinamis membagi request ke `nextcloud-app-1` dan `nextcloud-app-2` dengan perbandingan beban 50:50.
- **Pemeriksaan Kesehatan (Health Checks)**: HAProxy mengirimkan HTTP request request ke backend setiap 2 detik. Jika terjadi kegagalan sebanyak 3 kali berturut-turut, backend dianggap mati dan trafik dialihkan secara real-time ke node yang sehat dalam waktu di bawah 3 detik.
- **Session Stickiness**: HAProxy menyisipkan cookie `SERVERID` pada browser klien. Ini memastikan klien yang sama selalu diarahkan ke instansi backend yang sama selama instansi tersebut sehat.
- **Penyimpanan Terbagi (Stateless Architecture)**: Karena data biner Nextcloud disimpan di satu kontainer MinIO terpusat via API S3, kedua kontainer Nextcloud bersifat stateless. Masalah sinkronisasi filesystem lokal yang sering menjadi SPoF diatasi sepenuhnya.

### 8. Desain Otomatisasi Infrastruktur (Ansible Roles via Task Files)
Otomatisasi dikelompokkan secara modular menggunakan berkas tugas (*task files*) YAML di dalam folder `roles/` tanpa membuat sub-folder bertingkat untuk menjaga kesederhanaan workspace:

```text
ansible/
├── ansible.cfg               # Parameter default Ansible
├── inventory.ini             # IP target (localhost untuk WSL2)
├── site.yml                  # Playbook utama yang memanggil berkas-berkas tugas
└── roles/
    ├── common.yml            # Update apt repositori, install utilities dasar
    ├── docker.yml            # Install Docker Engine & Docker Compose
    ├── certificates.yml      # Pembuatan SSL/TLS self-signed certificates secara otomatis
    ├── database.yml          # Setup konfigurasi & direktori MariaDB
    ├── redis.yml             # Setup direktori & konfigurasi Redis
    ├── minio.yml             # Setup direktori & inisialisasi bucket MinIO
    ├── loadbalancer.yml      # Konfigurasi HAProxy dengan HTTPS dan cookie stickiness
    └── nextcloud.yml         # Konfigurasi Nextcloud terintegrasi ke MariaDB, Redis, & MinIO
```

### 9. Desain Docker Container
Multi-container stack dikonfigurasi melalui berkas `docker-compose.yml` dengan rincian berikut:

| Nama Kontainer | Base Image | Port Eksternal | Port Internal | Deskripsi |
| :--- | :--- | :--- | :--- | :--- |
| `haproxy-lb` | `haproxy:2.8-alpine` | `80`, `443` | `80`, `443` | Load Balancer SSL Termination |
| `nextcloud-app-1`| `nextcloud:apache` | - | `80` | Aplikasi Nextcloud Instance 1 |
| `nextcloud-app-2`| `nextcloud:apache` | - | `80` | Aplikasi Nextcloud Instance 2 |
| `mariadb-db` | `mariadb:10.11` | - | `3306` | Relational database untuk metadata |
| `redis-cache` | `redis:7-alpine` | - | `6379` | In-memory cache & locking |
| `minio-storage`  | `minio/minio` | `9000`, `9001` | `9000`, `9001` | Object Storage S3-compatible |
| `prom-server` | `prom/prometheus` | - | `9090` | Perekam metrik monitoring |
| `grafana-dash`   | `grafana/grafana` | `3000` | `3000` | Dashboard visualisasi monitoring |

---

## D. STRUKTUR WORKSPACE PROYEK (YANG AKAN DIKERJAKAN)

Berikut adalah struktur folder lengkap yang direncanakan untuk diimplementasikan dalam workspace `c:\Users\USER\Desktop\System Administator\Private-Cloud\`:

```text
Private-Cloud/
├── task.txt                        # Instruksi tugas dari dosen (telah di-upgrade)
├── checkpoint1.md                  # Laporan perancangan sistem (Berkas ini)
│
├── ansible/                        # Otomatisasi Ansible
│   ├── ansible.cfg                 # Global settings
│   ├── inventory.ini               # Host target (localhost WSL2)
│   ├── site.yml                    # Playbook utama
│   └── roles/                      # Direktori Roles Modular
│       ├── common.yml
│       ├── docker.yml
│       ├── certificates.yml
│       ├── database.yml
│       ├── redis.yml
│       ├── minio.yml
│       ├── loadbalancer.yml
│       └── nextcloud.yml
│
├── docker/                         # Docker Compose Stack
│   └── docker-compose.yml          # Konfigurasi multi-container
│
└── config/                         # Berkas konfigurasi khusus service
    ├── haproxy/
    │   └── haproxy.cfg             # Konfigurasi HAProxy SSL & Stickiness
    ├── nginx/
    │   └── nginx.conf              # Konfigurasi alternatif Nginx Load Balancer
    ├── prometheus/
    │   └── prometheus.yml          # Konfigurasi target scraping metrik
    └── grafana/
        └── provisioning/           # Auto-provisioning data sources & dashboard
```
