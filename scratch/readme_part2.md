## BAB III: ANALISIS KEBUTUHAN SISTEM

### 3.1 Analisis Kebutuhan Fungsional (Functional Requirements)
Analisis kebutuhan fungsional mendefinisikan secara menyeluruh seluruh kapabilitas operasional, perilaku interaktif, serta alur pemrosesan data yang wajib dipenuhi oleh platform Enterprise Private Cloud Storage agar dapat beroperasi sesuai dengan sasaran rekayasa sistem. Kebutuhan fungsional dijabarkan ke dalam beberapa poin bahasan paragraf di bawah ini:

Pertama, sistem harus menyediakan antarmuka pengguna berbasis grafis (*Graphical User Interface* - GUI) yang responsif dan dapat diakses secara universal menggunakan peramban web modern pada komputer klien. Antarmuka tersebut wajib menyediakan fungsionalitas manajemen file yang lengkap, meliputi pengunggahan berkas (*upload*) secara asinkron dengan indikator progres visual, pengunduhan berkas (*download*) dengan keutuhan data terjamin, pembuatan folder direktori baru untuk manajemen berkas, serta penghapusan berkas (*delete*) secara sinkron. Pengguna juga harus dapat melihat pratinjau berkas gambar atau dokumen teks secara langsung di browser tanpa perlu mengunduh berkas fisik terlebih dahulu.

Kedua, dari sisi manajemen akses keamanan dan hak pengguna, sistem wajib menyediakan fungsionalitas pembatasan akses berbasis peran (*Role-Based Access Control* - RBAC) secara granular. Administrator sistem harus memiliki halaman dashboard khusus yang terisolasi dari pengguna biasa untuk mengelola akun pengguna, mendaftarkan kredensial baru, mengelompokkan pengguna ke dalam divisi kerja tertentu (seperti grup `Engineer`, `Finance`, `HRD Manager`, `Developer`, `Manager`), serta menetapkan batas maksimal kuota penyimpanan (*storage quota limits*) yang berbeda-beda secara dinamis sesuai kebijakan operasional organisasi. Pengguna non-admin harus terbatasi hak aksesnya secara mutlak dan tidak boleh melihat atau memodifikasi berkas milik pengguna lain kecuali jika file tersebut secara sengaja dibagikan melalui fitur kolaborasi tautan publik (*public sharing link*).

Ketiga, untuk memastikan aspek ketersediaan tinggi, load balancer HAProxy wajib melakukan pemantauan status kesehatan (*health checks*) terhadap port server aplikasi backend secara periodik. Load balancer harus mampu mendeteksi matinya kontainer Nextcloud secara real-time dan secara otomatis mengalihkan rute koneksi klien baru ke kontainer cadangan yang sehat tanpa memicu pesan error koneksi pada browser klien. Data sesi aktif pengguna harus dipertahankan secara terpusat agar pengguna tidak dipaksa melakukan login ulang saat terjadi pengalihan beban kerja (*failover*).

Keempat, sistem pemantauan harus secara otomatis mengumpulkan metrik kinerja dari load balancer HAProxy dan database Prometheus secara berkala. Metrik-metrik yang dikumpulkan meliputi tingkat penggunaan memori RAM, persentase pemakaian CPU, latensi transfer data, status UP/DOWN kontainer, jumlah koneksi aktif, serta tingkat kegagalan scraping. Informasi mentah tersebut harus diolah dan diprovisikan ke dalam dasbor Grafana secara dinamis dalam bentuk grafik visualisasi interaktif untuk memudahkan proses diagnostik oleh administrator jaringan.

### 3.2 Analisis Kebutuhan Nonfungsional (Non-Functional Requirements)
Analisis kebutuhan nonfungsional menetapkan batasan kualitas rekayasa, batasan operasional, performa, ketahanan, keamanan, dan pemeliharaan sistem yang menjamin platform cloud storage layak digunakan pada lingkungan industri:
1. **Keamanan Informasi (Security)**: Seluruh transaksi komunikasi data antara browser klien dan load balancer terdepan wajib dilindungi menggunakan enkripsi SSL/TLS 1.3/1.2 terpusat (*SSL Termination*). Sertifikat enkripsi yang digunakan harus memiliki panjang kunci enkripsi minimal RSA 2048-bit dengan algoritma penandatanganan aman SHA-256 guna meminimalkan risiko serangan penyadapan data (*eavesdropping*). Kredensial login pengguna di dalam database MariaDB harus disimpan dalam bentuk hash satu arah menggunakan algoritma bcrypt/argon2 yang aman terhadap serangan *rainbow table*. Akses ke portal pemantauan Prometheus dan HAProxy Stats wajib dilindungi menggunakan otentikasi dasar HTTP (*basic auth*) untuk mencegah akses ilegal.
2. **Ketersediaan dan Ketahanan Tinggi (Availability & Fault Tolerance)**: Sistem harus memiliki keandalan operasional dengan target waktu respons failover otomatis ketika terjadi kerusakan node backend aplikasi di bawah 3 detik. *Single point of failure* (SPOF) pada lapisan aplikasi harus dieliminasi total melalui redundansi server aktif-aktif. Kegagalan operasional pada salah satu kontainer Nextcloud tidak boleh mengakibatkan hilangnya status sesi login pengguna atau korupsi pada file biner yang sedang diakses.
3. **Kinerja Sistem (Performance)**: Latensi load balancing HAProxy dalam menyalurkan request HTTP/HTTPS klien harus di bawah 50 milidetik. Kecepatan transfer baca-tulis file biner yang diarahkan ke Object Storage MinIO via API S3 harus dioptimalkan dengan meminimalkan penggunaan penyimpanan buffer lokal kontainer Nextcloud. Caching memori Redis harus memiliki latensi respons di bawah 5 milidetik untuk operasi transaksi session check.
4. **Skalabilitas (Scalability)**: Arsitektur server aplikasi Nextcloud harus dirancang secara *stateless*. Hal ini berarti tidak ada status sesi pengguna atau file biner fisik yang ditulis secara lokal pada filesystem kontainer Nextcloud. Konsep ini memudahkan proses penskalaan horizontal secara instan, di mana administrator dapat menambah kontainer aplikasi Nextcloud baru di belakang load balancer kapan saja tanpa perlu melakukan sinkronisasi manual filesystem lokal.
5. **Otomatisasi dan Pemeliharaan (Automation & Maintainability)**: Seluruh siklus deployment, instalasi dependensi, pembuatan sertifikat enkripsi, penulisan konfigurasi, hingga orkestrasi kontainer harus dapat dideploy dari nol secara utuh dan idempotent menggunakan script Ansible Playbook. Administrator harus dapat me-rebuild atau memulihkan seluruh container stack secara otomatis tanpa intervensi instruksi manual di terminal.

### 3.3 Analisis Peran Pengguna (User Roles)
Sistem membedakan tingkat previlese dan alokasi resource berdasarkan peran pengguna guna menjaga privasi, pembagian beban kerja, dan isolasi data secara terstruktur:
1. **System Administrator (Admin)**: Memiliki kendali penuh terhadap seluruh sistem. Admin dapat mengakses dashboard Nextcloud Settings untuk melakukan manajemen akun, mengatur batasan kuota disk divisi kerja, memantau grafik analitik kinerja container stack pada Grafana port 3000, memodifikasi berkas konfigurasi di host target, serta menjalankan playbook otomatisasi Ansible.
2. **Engineer User (Divisi Rekayasa)**: Pengguna reguler dalam grup `Engineer` dengan alokasi kuota penyimpanan disk sebesar 10 GB. Alokasi kuota ini dirancang untuk menampung file laporan teknis, file skema sirkuit, gambar topologi jaringan, dan dokumen rekayasa yang berukuran sedang. Engineer dapat mengunggah, mengunduh, mengedit berkas teks secara kolaboratif, serta membagikan tautan publik ke klien eksternal.
3. **Finance User (Divisi Keuangan)**: Pengguna reguler dalam grup `Finance` dengan kapasitas kuota penyimpanan disk sebesar 5 GB. Kapasitas ini dibatasi karena divisi keuangan keuangan mayoritas hanya menangani dokumen administrasi, tabel spreadsheet keuangan, PDF invoice, dan laporan bulanan berukuran kecil yang tidak memakan banyak ruang penyimpanan.
4. **HRD Manager User (Divisi Sumber Daya Manusia)**: Pengguna dalam grup `HRD Manager` dengan kuota disk sebesar 15 GB, dialokasikan untuk menyimpan data rekrutmen karyawan, berkas identitas staf, dokumen evaluasi kerja bulanan, serta dokumen legal perusahaan.
5. **Developer User (Divisi Pengembangan Software)**: Pengguna dalam grup `Developer` dengan kuota disk sebesar 20 GB. Kapasitas kuota yang besar ini dialokasikan untuk mendukung penyimpanan repositori source code proyek, file instalasi software (executable/build), dokumentasi API, serta file aset desain aplikasi.
6. **Manager User (Divisi Manajemen Eksekutif)**: Pengguna dalam grup `Manager` dengan kuota disk tertinggi sebesar 25 GB. Kuota ini diberikan untuk mendukung penyimpanan file presentasi bisnis berukuran besar, rekaman video koordinasi manajemen, arsip kebijakan perusahaan, serta laporan analisis tahunan.

### 3.4 Analisis Kebutuhan Infrastruktur
Untuk memastikan simulasi arsitektur Enterprise Private Cloud Storage ini berjalan dengan performa optimal di komputer host Windows, administrator menganalisis alokasi sumber daya sebagai berikut:
- **Perangkat Keras (Hardware)**: Dibutuhkan prosesor multi-core modern (minimal 4 Core / 8 Thread) seperti Intel Core i5/Ryzen 5 dengan dukungan fitur hardware virtualization aktif di BIOS. Memori RAM fisik host minimal 16 GB, karena total alokasi memori yang dikonsumsi oleh WSL2 dan 8 kontainer Docker berkisar antara 4 GB hingga 6 GB saat beban trafik tinggi. Penyimpanan minimal SSD dengan ruang kosong 20 GB untuk mengakomodasi container image, volume database MariaDB, penyimpanan log audit, dan media penyimpanan MinIO S3 bucket.
- **Perangkat Lunak (Software)**: Windows 10/11 Pro/Enterprise 64-bit dengan Windows Subsystem for Linux 2 (WSL2) terpasang. Distro Linux Ubuntu 22.04 LTS dipasang di dalam WSL2 sebagai hypervisor utama. Docker Engine versi terbaru beserta plugin Docker Compose V2 dipasang di dalam kernel Ubuntu. Ansible Engine versi 2.12+ terinstal di WSL2 untuk bertindak sebagai controller deployment otomatis.

---

## BAB IV: DESAIN SISTEM

### 4.1 Topology Jaringan Virtual (Network Topology)
Desain topologi jaringan virtual sistem memanfaatkan Docker Bridge Network internal (`cloud-network`) dengan alokasi subnet kelas B `172.20.0.0/16`. Topologi ini memisahkan lalu lintas data eksternal dan internal demi menjaga keamanan data backend.

```text
    [ CLIENT BROWSER (Windows Host) ] 
                   │
                   │ HTTPS Port 443 (Dekripsi TLS di HAProxy)
                   ▼
    +─────────────────────────────────────────────────────────────+
    | WSL2 Virtual Interface (WSL IP: 172.20.0.1 Bridge Gateway)  |
    |                                                             |
    |  +───────────────────────────────────────────────────────+  |
    |  | Docker bridge: cloud-network (Subnet: 172.20.0.0/16)  |  |
    |  |                                                       |  |
    |  |   ┌───────────────────────────────────────────────┐   |  |
    |  |   |             HAProxy LB (haproxy-lb)           |   |  |
    |  |   |             IP: 172.20.0.7 / Port 80,443      |   |  |
    |  |   └───────────────┬───────────────────────┬───────┘   |  |
    |  |                   │                       │           |  |
    |  |                   ▼ app1                  ▼ app2      |  |
    |  |          ┌────────────────┐      ┌────────────────┐   |  |
    |  |          | Nextcloud 1    |      | Nextcloud 2    |   |  |
    |  |          | 172.20.0.5:80  |      | 172.20.0.6:80  |   |  |
    |  |          └──────┬───┬─────┘      └──────┬───┬─────┘   |  |
    |  |                 │   │                   │   │         |  |
    |  |    MariaDB SQL  │   │ Redis Session     │   │         |  |
    |  |    Port 3306    │   │ Port 6379         │   │         |  |
    |  |                 ▼   └───────┐   ┌───────┘   ▼         |  |
    |  |      ┌───────────────┐      ▼   ▼      ┌───────────┐  |  |
    |  |      |  MariaDB DB   |   ┌──────────┐  | MinIO S3  |  |  |
    |  |      |  172.20.0.2   |   |  Redis   |  | 172.20.0.4|  |  |
    |  |      └───────────────┘   |172.20.0.3|  | Port 9000 |  |  |
    |  |                          └──────────┘  └───────────┘  |  |
    |  |                                              ▲        |  |
    |  |                                              │        |  |
    |  |   ┌───────────────┐      Pull Metrics        │        |  |
    |  |   |  Prometheus   |◄──Scrape (Port 1936)─────┘        |  |
    |  |   |  172.20.0.8   |                                   |  |
    |  |   └───────▲───────┘                                   |  |
    |  |           │ Pull Metrics                              |  |
    |  |   ┌───────┴───────┐                                   |  |
    |  |   |    Grafana    |                                   |  |
    |  |   |  172.20.0.9   |                                   |  |
    |  |   └───────────────┘                                   |  |
    |  +───────────────────────────────────────────────────────+  |
    +─────────────────────────────────────────────────────────────+
```

### 4.2 Desain Alur Sistem Login dan Upload (UML Sequence)
Desain alur komunikasi antar komponen memisahkan proses verifikasi sesi, validasi data relasional, dan transmisi data biner ke object storage secara stateless.

```text
Browser          HAProxy LB      Nextcloud App      Redis Cache      MariaDB DB      MinIO S3
  │                  │                 │                 │               │               │
  │───HTTPS Login───►│                 │                 │               │               │
  │                  │───Route (RR)───►│                 │               │               │
  │                  │                 │──Query User────►│               │               │
  │                  │                 │◄─Verify Hash────│               │               │
  │                  │                 │──Set Session───►│               │               │
  │                  │                 │◄──Confirm Session─│               │               │
  │◄─Set Cookie HTTP─│◄─HTTP 200 OK────│                 │               │               │
  │                  │                 │                 │               │               │
  │───HTTPS Upload──►│                 │                 │               │               │
  │                  │──Check Cookie──►│                 │               │               │
  │                  │                 │──Acquire Lock──►│               │               │
  │                  │                 │◄──Lock Granted──│               │               │
  │                  │                 │──────Simpan Metadata SQL───────►│               │
  │                  │                 │◄─────Confirm Write Success──────│               │
  │                  │                 │                                 │               │
  │                  │                 │──────────────Kirim Objek via S3 API────────────►│
  │                  │                 │◄─────────────Confirm S3 Upload Success──────────│
  │                  │                 │                                 │               │
  │                  │                 │──Release Lock─►│               │               │
  │                  │                 │◄──Lock Free─────│               │               │
  │◄──Upload Success─│◄──HTTP 200 OK───│                 │               │               │
```

### 4.3 Diagram Alur Sistem Failover (HA State Machine)
Berikut adalah diagram alur logika mesin status (*state machine*) HAProxy Load Balancer saat mendeteksi kegagalan server backend dan melakukan recovery:

```text
       ┌────────────────────────┐
       │   Status Server: UP    │◄──────────────────────────────┐
       │      (Warna Hijau)     │                               │
       └───────────┬────────────┘                               │
                   │                                            │
           TCP Check Gagal?                               L4OK Check Sukses
                   │                                      2x berturut-turut?
                   ▼                                            │
       ┌────────────────────────┐                               │
  ┌───►│ Status: Check Failing  │                               │
  │    │     (Polling TCP)      │                               │
  │    └───────────┬────────────┘                               │
  │                │                                            │
  │        TCP Check Sukses? ────► (Kembali ke UP)              │
  │                │                                            │
  │        Gagal 3x beruntun?                                   │
  │                │                                            │
  │                ▼                                            │
  │    ┌────────────────────────┐                               │
  │    │  Status Server: DOWN   │───────────────────────────────┘
  └────│  (Trafik dialihkan ke  │
       │    server cadangan)    │
       └────────────────────────┘
```

### 4.4 Diagram Input-Process-Output (IPO)
Berikut adalah representasi visual dari diagram alur Input-Process-Output (IPO) untuk fungsionalitas sistem utama:

| Komponen Alur | Upload Berkas | Download Berkas | Failover Layanan |
| :--- | :--- | :--- | :--- |
| **INPUT** | File lokal, kredensial user, folder tujuan. | ID berkas unik, cookie session browser target. | Kegagalan port HTTP backend Nextcloud 1. |
| **PROCESS** | 1. Akuisisi lock di Redis.<br>2. Verifikasi kuota via MariaDB.<br>3. Tulis metadata ke MariaDB.<br>4. Streaming data via S3 API ke MinIO.<br>5. Bebaskan lock di Redis. | 1. Baca metadata dari MariaDB.<br>2. Ambil token streaming via S3 API.<br>3. Stream berkas dari MinIO Console.<br>4. Transfer file via HAProxy ke browser. | 1. TCP Check HAProxy gagal 3x.<br>2. Tandai status server 1 DOWN.<br>3. Alihkan trafik ke server 2.<br>4. Re-otentikasi otomatis via Redis. |
| **OUTPUT** | File tersimpan di MinIO, kuota berkurang. | Berkas diunduh sukses, keutuhan checksum terjamin. | Sistem tetap responsif, sesi login aktif. |

### 4.5 Desain Manajemen User dan Kuota
Sistem manajemen penyimpanan Nextcloud menerapkan isolasi ruang kerja logic (*workspace isolation*) berdasarkan divisi kerja. Struktur direktori internal Nextcloud di MinIO memetakan path untuk tiap pengguna secara unik pada bucket `nextcloud`. Kebijakan alokasi kuota dikelola secara dinamis di level database. Setiap kali file baru diunggah, Nextcloud menghitung total file size terpakai pada kueri basis data MariaDB, membandingkannya dengan alokasi grup user. Jika kuota tersisa tidak mencukupi, operasi upload ditolak sebelum biner ditransmisikan.

---

## BAB V: DETAIL BERKAS KONFIGURASI DAN REKAYASA TEKNIS

### 5.1 Berkas Docker Compose (`docker/docker-compose.yml`)
Berkas ini bertindak sebagai orkestrator kontainer yang mendefinisikan image, dependensi, volume persistent host ke kontainer, dan virtual network.
```yaml
version: '3.8'

services:
  mariadb-db:
    image: mariadb:10.11
    container_name: mariadb-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: adminrootpassword
      MYSQL_DATABASE: nextcloud_db
      MYSQL_USER: nextcloud_user
      MYSQL_PASSWORD: nextcloudpassword
    volumes:
      - /opt/private-cloud/mariadb:/var/lib/mysql
    networks:
      - cloud-network

  redis-cache:
    image: redis:7-alpine
    container_name: redis-cache
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - /opt/private-cloud/redis:/data
    networks:
      - cloud-network

  minio-storage:
    image: minio/minio:latest
    container_name: minio-storage
    restart: always
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadminpassword
    ports:
      - "9001:9001"
    volumes:
      - /opt/private-cloud/minio:/data
    command: server /data --console-address ":9001"
    networks:
      - cloud-network

  nextcloud-app-1:
    image: nextcloud:apache
    container_name: nextcloud-app-1
    restart: always
    environment:
      MYSQL_HOST: mariadb-db:3306
      MYSQL_DATABASE: nextcloud_db
      MYSQL_USER: nextcloud_user
      MYSQL_PASSWORD: nextcloudpassword
      REDIS_HOST: redis-cache
      OBJECTSTORE_S3_HOST: minio-storage
      OBJECTSTORE_S3_PORT: 9000
      OBJECTSTORE_S3_KEY: minioadmin
      OBJECTSTORE_S3_SECRET: minioadminpassword
      OBJECTSTORE_S3_BUCKET: nextcloud
      OBJECTSTORE_S3_SSL: "false"
      OBJECTSTORE_S3_USEPATHSTYLE: "true"
      OBJECTSTORE_S3_USEPATH_STYLE: "true"
    depends_on:
      - mariadb-db
      - redis-cache
      - minio-storage
    networks:
      - cloud-network

  nextcloud-app-2:
    image: nextcloud:apache
    container_name: nextcloud-app-2
    restart: always
    environment:
      MYSQL_HOST: mariadb-db:3306
      MYSQL_DATABASE: nextcloud_db
      MYSQL_USER: nextcloud_user
      MYSQL_PASSWORD: nextcloudpassword
      REDIS_HOST: redis-cache
      OBJECTSTORE_S3_HOST: minio-storage
      OBJECTSTORE_S3_PORT: 9000
      OBJECTSTORE_S3_KEY: minioadmin
      OBJECTSTORE_S3_SECRET: minioadminpassword
      OBJECTSTORE_S3_BUCKET: nextcloud
      OBJECTSTORE_S3_SSL: "false"
      OBJECTSTORE_S3_USEPATHSTYLE: "true"
      OBJECTSTORE_S3_USEPATH_STYLE: "true"
    depends_on:
      - mariadb-db
      - redis-cache
      - minio-storage
    networks:
      - cloud-network

  haproxy-lb:
    image: haproxy:2.8-alpine
    container_name: haproxy-lb
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "1936:1936"
    volumes:
      - /opt/private-cloud/config/haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
      - /opt/private-cloud/config/ssl/haproxy.pem:/usr/local/etc/haproxy/ssl/haproxy.pem:ro
    depends_on:
      - nextcloud-app-1
      - nextcloud-app-2
    networks:
      - cloud-network

  prom-server:
    image: prom/prometheus:latest
    container_name: prom-server
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - /opt/private-cloud/config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - cloud-network

  grafana-dash:
    image: grafana/grafana:latest
    container_name: grafana-dash
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - /opt/private-cloud/config/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - cloud-network

networks:
  cloud-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### Analisis Teknik Rekayasa Berkas `docker-compose.yml`
Penjelasan mendalam mengenai parameter konfigurasi orkestrasi kontainer di atas adalah sebagai berikut:
- **Layanan `mariadb-db`**: Menggunakan image basis data MariaDB versi 10.11 yang bersertifikasi LTS. Pengaturan parameter `MYSQL_DATABASE`, `MYSQL_USER`, dan `MYSQL_PASSWORD` mengotomatisasi pembuatan database default `nextcloud_db` beserta hak akses user. Pemetaan volume `- /opt/private-cloud/mariadb:/var/lib/mysql` mengaitkan direktori database kontainer secara fisik ke penyimpanan host WSL2. Hal ini sangat penting untuk menjaga kegigihan data relasional melintasi siklus hidup kontainer.
- **Layanan `redis-cache`**: Dijalankan dengan perintah tambahan `redis-server --appendonly yes`. Berbeda dengan perilaku Redis bawaan yang menyimpan data secara periodik ke file `.rdb` (yang dapat menyebabkan kehilangan data sesi beberapa menit terakhir jika terjadi crash mendadak), opsi *Append-Only File* (AOF) memaksa Redis mencatat setiap instruksi modifikasi data sesi yang masuk secara real-time ke dalam log fisik `/data/appendonly.aof` setiap detik. Ini memberikan ketahanan kehilangan data yang jauh lebih tinggi.
- **Layanan `minio-storage`**: Layanan Object Storage ini memetakan konsol administrator visual pada port eksternal `9001` agar dapat dikelola secara grafis oleh administrator dari browser Windows. Sementara port data API S3 (`9000`) sengaja dibiarkan tertutup ke jaringan publik dan hanya diakses secara privat oleh kontainer Nextcloud di dalam virtual bridge network internal demi meminimalisasi vektor serangan eksploitasi API luar.
- **Layanan `nextcloud-app-1` & `nextcloud-app-2`**: Merupakan replika server aplikasi web Nextcloud. Untuk merealisasikan arsitektur *stateless*, kontainer ini dikonfigurasi menggunakan variabel lingkungan khusus. Variabel `REDIS_HOST: redis-cache` mengarahkan penyimpanan sesi login PHP langsung ke Redis cache terpusat. Sementara parameter `OBJECTSTORE_S3_*` mengalihkan penyimpanan file primer Nextcloud ke API S3 MinIO. Penggunaan parameter `OBJECTSTORE_S3_USEPATHSTYLE: "true"` dan `OBJECTSTORE_S3_USEPATH_STYLE: "true"` wajib diisi untuk menginstruksikan modul SDK AWS S3 internal Nextcloud untuk melakukan resolusi path URL menggunakan skema alamat *Path-Style* (seperti `http://minio-storage:9000/nextcloud`) alih-alih skema *Virtual-Host Style* (seperti `http://nextcloud.minio-storage:9000`) yang tidak didukung oleh resolusi DNS internal bridge network Docker Compose default.
- **Layanan `haproxy-lb`**: Layanan ini bergantung penuh (`depends_on`) pada keaktifan kontainer `nextcloud-app-1` dan `nextcloud-app-2`. Volume dipetakan secara *read-only* (`:ro`) untuk menjaga integritas file sertifikat gabungan `haproxy.pem` dan file konfigurasi `haproxy.cfg` agar tidak dimodifikasi secara ilegal dari dalam kontainer.
- **Layanan `prom-server` & `grafana-dash`**: Merupakan stack pemantauan terisolasi. Prometheus memetakan port `9090` ke host luar untuk visualisasi kueri PromQL, sedangkan Grafana memetakan port `3000` untuk menyajikan dasbor monitoring interaktif.

### 5.2 Berkas Konfigurasi HAProxy (`config/haproxy/haproxy.cfg`)
Berkas ini bertindak sebagai pintu gerbang utama untuk mendistribusikan beban trafik dan menangani sertifikat TLS.
```haproxy
global
    log stdout format raw local0
    maxconn 4096

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend http_frontend
    bind *:80
    http-request redirect scheme https unless { ssl_fc }

frontend https_frontend
    bind *:443 ssl crt /usr/local/etc/haproxy/ssl/haproxy.pem
    default_backend nextcloud_backend

backend nextcloud_backend
    balance roundrobin
    cookie SERVERID insert indirect nocache
    server app1 nextcloud-app-1:80 check cookie app1
    server app2 nextcloud-app-2:80 check cookie app2

listen stats
    bind *:1936
    stats enable
    stats uri /
    stats refresh 5s
    stats auth admin:adminstats
    http-request use-service prometheus-exporter if { path /metrics }
```

#### Analisis Teknik Rekayasa Berkas `haproxy.cfg`
Penjelasan mendalam mengenai parameter konfigurasi gerbang load balancer HAProxy adalah sebagai berikut:
- **Blok `global` dan `defaults`**: Batas koneksi maksimum disetel ke `maxconn 4096` untuk membatasi konsumsi memori RAM kontainer HAProxy saat terjadi lonjakan trafik. Opsi `option httplog` mengaktifkan pencatatan log detail transaksi HTTP, termasuk kode status HTTP respons, waktu latensi, byte ditransmisikan, dan header client IP. Parameter `timeout client 50000ms` dan `timeout server 50000ms` diatur tinggi guna memfasilitasi lalu lintas pengunggahan atau pengunduhan file berukuran besar agar tidak terputus di tengah jalan oleh load balancer.
- **Blok `frontend http_frontend`**: Mengikat seluruh interface jaringan fisik target pada port 80. Baris `http-request redirect scheme https unless { ssl_fc }` menerapkan pengalihan paksa koneksi. Kondisi `{ ssl_fc }` memeriksa apakah request koneksi yang masuk sudah dienkripsi TLS/SSL. Jika tidak, HAProxy membalas request browser dengan kode status HTTP 301/302 Redirect yang memaksa browser memuat ulang alamat URL menggunakan skema aman HTTPS di port 443.
- **Blok `frontend https_frontend`**: Mengikat interface jaringan pada port 443 dengan konfigurasi enkripsi aktif. Parameter `ssl crt /usr/local/etc/haproxy/ssl/haproxy.pem` memuat sertifikat TLS gabungan. HAProxy bertindak sebagai pintu dekripsi TLS (*SSL Termination*). Seluruh kalkulasi matematika enkripsi/dekripsi kunci RSA diselesaikan di lapisan load balancer, sehingga HAProxy menyalurkan request HTTP biasa tanpa beban enkripsi ke kontainer backend Nextcloud, menghemat konsumsi CPU server aplikasi backend.
- **Blok `backend nextcloud_backend`**: Parameter `balance roundrobin` menetapkan algoritma pembagian beban bergantian secara adil. Opsi `cookie SERVERID insert indirect nocache` menginstruksikan HAProxy untuk menyisipkan cookie session HTTP bernama `SERVERID` ke dalam respons HTTP browser. Browser akan menyimpan cookie ini. Untuk request selanjutnya, HAProxy akan membaca cookie `SERVERID` tersebut dan mengarahkan klien secara langsung ke server aplikasi yang sesuai (`check cookie app1` atau `check cookie app2`), memelihara integritas login user.
- **Blok `listen stats`**: Mengaktifkan halaman status visual internal HAProxy pada port `1936` dengan pengamanan `stats auth admin:adminstats`. Baris `http-request use-service prometheus-exporter if { path /metrics }` memproses konversi metrik kinerja HAProxy ke dalam format standard data exporter Prometheus yang dapat ditarik (*scrape*) melalui path URL `/metrics`.

### 5.3 Berkas Konfigurasi Nginx Alternatif (`config/nginx/nginx.conf`)
Sebagai materi pembanding akademis rekayasa web server, Nginx dapat di-deploy sebagai load balancer alternatif pengganti HAProxy:
```nginx
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;

    upstream nextcloud_servers {
        server nextcloud-app-1:80 max_fails=3 fail_timeout=10s;
        server nextcloud-app-2:80 max_fails=3 fail_timeout=10s;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name localhost;
        return 301 https://$host$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;

        location / {
            proxy_pass http://nextcloud_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### Analisis Rekayasa Komparatif Nginx vs HAProxy
Penjelasan komparatif antara Nginx dan HAProxy sebagai load balancer adalah sebagai berikut:
- **Konfigurasi `upstream nextcloud_servers`**: Nginx mendefinisikan klaster backend menggunakan blok `upstream`. Parameter `max_fails=3` dan `fail_timeout=10s` setara dengan parameter `check` pada HAProxy, di mana Nginx akan menangguhkan pengiriman request ke backend selama 10 detik jika terdeteksi kegagalan koneksi sebanyak 3 kali berturut-turut.
- **Pelewatan Header HTTP**: Blok `proxy_set_header` pada Nginx (seperti `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for`) sangat penting karena bertindak sebagai perantara yang meneruskan alamat IP asli browser klien (`X-Real-IP`) dan skema protokol awal (`X-Forwarded-Proto`) ke kontainer Nextcloud. Tanpa header ini, Nextcloud di backend akan salah mendeteksi seluruh request berasal dari IP internal gateway load balancer (`172.20.0.7`), memicu masalah keamanan dan pemblokiran rate-limiting IP.
- **Perbandingan Kinerja**: HAProxy memiliki keunggulan performa murni pada operasi load balancing yang sangat berat karena fokus fungsionalitasnya yang terspesialisasi sebagai proxy layer 4/7 dengan konsumsi resource memori statis minimal. Di sisi lain, Nginx menawarkan kelebihan berupa fleksibilitas pengolahan konten statis, caching internal proxy web (*Nginx proxy cache*), serta konfigurasi pemetaan URL (*URL rewriting*) yang lebih variatif, menjadikannya pilihan ideal jika load balancer juga bertindak sebagai web server aset lokal.

### 5.4 Berkas Konfigurasi Prometheus (`config/prometheus/prometheus.yml`)
(Isi file YAML dan analisis teknis Prometheus tercantum pada sub-bab sebelumnya).

### 5.5 Berkas Konfigurasi Grafana Provisioning (`config/grafana/provisioning/datasources/datasource.yml`)
(Isi file YAML dan analisis teknis Grafana provisioning tercantum pada sub-bab sebelumnya).

### 5.6 Kueri Analisis PromQL Monitoring Stack
Untuk memonitor stabilitas platform Private Cloud Storage secara real-time pada dashboard Grafana, administrator merancang 5 kueri analisis berbasis PromQL (*Prometheus Query Language*) sebagai berikut:
1. **Uptime Server Monitoring**:
   ```promql
   prometheus_tsdb_wal_uploads_total
   ```
   Kueri ini digunakan untuk memantau frekuensi unggahan data log WAL (*Write-Ahead Logging*) Prometheus ke disk. Nilai grafik yang meningkat secara konstan membuktikan database TSDB aktif mencatat perubahan kinerja hardware secara stabil.
2. **Deteksi Kegagalan Scraping Target**:
   ```promql
   up{job="haproxy"} == 0
   ```
   Kueri ini mendeteksi status keaktifan target scraping. Jika nilai keluaran bernilai `0`, server Prometheus akan memicu peringatan (*alert warning*) bahwa target load balancer HAProxy tidak responsif atau mengalami pemutusan port statistik `/metrics`.
3. **Sampel Masuk Per Detik (Scrape Appended Samples Rate)**:
   ```promql
   rate(prometheus_tsdb_head_samples_appended_total[5m])
   ```
   Kueri ini menghitung rata-rata kecepatan data sampel metrik baru yang ditulis ke dalam memory database Prometheus dalam rentang waktu 5 menit terakhir, memantau tingkat kesibukan scraping.
4. **Waktu Durasi Scraping Target**:
   ```promql
   prometheus_target_interval_length_seconds{quantile="0.5"}
   ```
   Kueri ini mengukur latensi respons penarikan data metrik (dalam satuan detik) pada tingkat median (persentil ke-50) untuk memastikan durasi transfer metrik jaringan internal Docker berjalan cepat (stabil di bawah `0.01` detik).
5. **Frekuensi Pembersihan Garbage Collection (GC Rate)**:
   ```promql
   go_gc_duration_seconds{quantile="0.5"}
   ```
   Kueri ini digunakan untuk memantau rata-rata durasi waktu jeda penundaan runtime Go saat melakukan pembersihan memori otomatis (*Garbage Collection*) pada kontainer database Prometheus, mengantisipasi gejala memory leaks.
