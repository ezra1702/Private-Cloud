#### Skenario 3.6: Pengujian Monitoring Sistem Menggunakan Prometheus
- **Tujuan Pengujian**: Memastikan server Prometheus berhasil melakukan penarikan data metrik (*active-scraping*) secara periodik dari target loopback internal dan target load balancer HAProxy via HTTP basic authentication.
- **Desain Skenario**: Mengakses antarmuka web administrator Prometheus Web UI di port 9090 dan menganalisis tabel keaktifan targets.
- **Input Uji**: URL `http://localhost:9090` di browser komputer klien.
- **Prosedur Langkah Pengujian**:
  Administrator membuka browser web, mengetikkan alamat URL `http://localhost:9090` pada address bar, lalu menekan Enter. Pada panel navigasi atas Prometheus, administrator mengklik menu *Status* -> *Targets*, lalu mengamati status kesehatan target.
- **Output yang Diharapkan**: Dashboard Prometheus termuat. Halaman Targets menampilkan target `prometheus` dan target `haproxy` dalam status berwarna hijau bertuliskan **UP**.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Prometheus bekerja menggunakan model tarikan (*pull model*) yang secara periodik mengirimkan request HTTP GET ke endpoint metrik target. Di dalam file konfigurasi `prometheus.yml`, target `haproxy` didaftarkan menggunakan domain internal Docker `haproxy-lb:1936` pada path `/metrics`. Karena port statistik HAProxy dilindungi oleh proteksi kredensial stats, Prometheus memanfaatkan opsi konfigurasi `basic_auth` untuk mengirimkan header otentikasi HTTP dasar.
  
  Tangkapan layar di atas menunjukkan status target `haproxy` berada dalam kondisi **UP** dengan waktu scraping terakhir `2.861s ago` dan durasi respons scraping `1.042ms`. Hal ini membuktikan bahwa Prometheus berhasil melompati proteksi kata sandi stats HAProxy dan berhasil menerjemahkan metrik mentah yang disajikan oleh modul exporter internal HAProxy ke dalam database deret waktu (*time-series database*) internalnya secara berkala.

  Scraping target ini sangat penting dalam arsitektur monitoring terdistribusi. Dengan mengumpulkan data keaktifan HAProxy, Prometheus dapat memicu alert sistem secara otomatis jika terdeteksi adanya penurunan performa load balancer, kegagalan koneksi backend, atau lonjakan request abnormal.

---

#### Skenario 3.7: Pengujian Monitoring Sistem Menggunakan Grafana
- **Tujuan Pengujian**: Memverifikasi keberhasilan integrasi visualisasi data source Prometheus pada dasbor Grafana, memastikan data deret waktu (*time-series data*) dirender secara visual dalam bentuk grafik real-time yang akurat dan interaktif.
- **Desain Skenario**: Mengakses halaman utama dashboard Grafana di port 3000, login, meng-import template dashboard Prometheus Overview, dan menganalisis grafik indikator performa.
- **Input Uji**: URL `http://localhost:3000` beserta template ID dashboard `3662`.
- **Prosedur Langkah Pengujian**:
  Administrator membuka browser, mengakses `http://localhost:3000`, login dengan user default admin, meng-import template dashboard ID `3662`, menghubungkannya ke data source Prometheus, lalu memantau grafik Uptime, total series, append rate, dan aktivitas Garbage Collection.
- **Output yang Diharapkan**: Dasbor visual Grafana termuat dengan sukses. Grafik menampilkan data real-time yang terus berubah secara dinamis, tanpa ada indikasi error data source connection.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Provisiasi visual pada Grafana terhubung secara seamless dengan server Prometheus melalui konfigurasi otomatis berkas `datasource.yml`. Pada dashboard *Prometheus 2.0 Overview* (ID: 3662), data metrik dirender menggunakan kueri bahasa PromQL (*Prometheus Query Language*) secara kontinu. Dasbor atas menunjukkan uptime Prometheus mencapai 100% penuh selama 1 jam terakhir dengan jumlah data series aktif terakumulasi sebanyak 1451 series. Status `N/A` pada missed/skipped iterations verifikasi tidak ada query internal yang mengalami keterlambatan eksekusi.
  
  Dasbor tengah menyajikan visualisasi grafik *Appended Samples per Second* yang berfluktuasi secara dinamis di kisaran 60-80 samples/s, menggambarkan kecepatan penyimpanan data metrik baru. Grafik durasi scraping menunjukkan rata-rata waktu respons penarikan metrik berada di bawah 0.008 detik, membuktikan efisiensi komunikasi antar kontainer di dalam Docker bridge network. Dasbor bawah menunjukkan keaktifan siklus pembersihan memori otomatis (*Garbage Collection*) untuk menjaga konsumsi RAM kontainer agar tetap stabil dan terhindar dari anomali kebocoran memori (*memory leak*), memvalidasi kesiapan sistem monitoring untuk kebutuhan diagnosa sistem jangka panjang.

  Keberhasilan visualisasi Grafana ini membuktikan stabilitas integrasi provisioning datasource Grafana. Datasource yang didefinisikan secara deklaratif di `datasource.yml` terbukti langsung dapat dibaca oleh panel-panel visualisasi Grafana, menghemat waktu setup manual bagi administrator sistem saat melakukan deployment dari nol.

---

## BAB VIII: ANALISIS HASIL DAN PEMBAHASAN

### 8.1 Analisis Keberhasilan Otomatisasi (Ansible Role Modularity)
Penerapan Infrastructure as Code (IaC) menggunakan struktur peran Ansible (*Ansible Roles*) terbukti secara signifikan meminimalkan waktu penyediaan (*provisioning*) infrastruktur server dari yang semula membutuhkan waktu berjam-jam pengerjaan manual menjadi kurang dari dua menit secara otomatis. Pemisahan tugas ke dalam sub-peran modular (`common`, `docker`, `certificates`, `database`, `redis`, `minio`, `loadbalancer`, `nextcloud`) memfasilitasi kemudahan pemeliharaan kode serta mempercepat pelacakan kesalahan konfigurasi. Sifat Ansible yang *idempotent* menjamin bahwa playbook dapat dijalankan berulang kali pada target yang sama tanpa risiko merusak database yang sedang aktif atau membangkitkan ulang sertifikat TLS yang masih valid, melainkan hanya memperbarui komponen konfigurasi yang terdeteksi mengalami modifikasi fisik di workspace.

### 8.2 Analisis Mekanisme High Availability (HA) & Stateless Architecture
Desain ketersediaan tinggi diuji dengan mematikan kontainer server aplikasi Nextcloud 1 secara paksa. HAProxy terbukti mendeteksi matinya kontainer dalam waktu di bawah 3 detik melalui kegagalan jabat tangan TCP (*TCP handshake checks*) pada port 80 secara beruntun. Pemindahan beban trafik (*failover*) ke kontainer cadangan Nextcloud 2 berjalan secara transparan dari sisi pengguna. Ketiadaan penyimpanan data biner lokal pada kontainer Nextcloud (*stateless model*) yang dialihkan langsung ke Object Storage MinIO via API S3, dikombinasikan dengan sinkronisasi data sesi login pengguna secara terpusat pada Redis cache, terbukti menjadi faktor kunci keberhasilan failover. Pengguna tetap dapat login, mengakses folder, dan menyelesaikan proses upload file tanpa terputus sesi aktifnya saat pemindahan backend berlangsung.

### 8.3 Analisis Manajemen Pengguna dan Kebijakan Kuota
Nextcloud sukses menerapkan sistem kontrol akses berbasis peran (*Role-Based Access Control* - RBAC) secara granular. Pengguna biasa dari berbagai grup divisi (`engineer1`, `finance1`, `hrd1`, `developer1`, `manager1`) berhasil diarahkan ke dashboard personal masing-masing yang terisolasi dari wewenang administratif. Administrator sistem berhasil membatasi kapasitas penyimpanan data secara dinamis melalui konfigurasi kuota disk Nextcloud. Setiap file biner yang diunggah dikonversi ukurannya dan divalidasi terhadap batas kapasitas disk yang diizinkan (misal: 10 GB untuk Engineer dan 20 GB untuk Developer) sebelum diizinkan ditulis ke Object Storage backend, mencegah terjadinya pemborosan resource media penyimpanan fisik.

### 8.4 Analisis Infrastruktur Monitoring & Diagnostik
Integrasi monitoring menggunakan Prometheus dan Grafana memberikan transparansi visual bagi administrator untuk memantau kesehatan server secara proaktif. Pengalihan endpoint statistik HAProxy port 1936 ke format exporter Prometheus `/metrics` dengan proteksi kata sandi dasar terbukti berhasil di-scrape tanpa kendala otentikasi. Visualisasi grafik interaktif Grafana memfasilitasi identifikasi dini terhadap gejala penumpukan antrean koneksi (*connection queueing*), lonjakan latensi respons HTTP backend, serta pemakaian RAM/CPU kontainer, menyajikan platform diagnostik terpadu berskala industri.

### 8.5 Analisis Penggunaan Docker
Penggunaan teknologi kontainerisasi Docker memberikan keuntungan isolasi pustaka dependensi bagi setiap mikroservis. Setiap komponen berjalan pada container runtime tersendiri tanpa memicu konflik dependensi sistem operasi host. Docker Compose mempermudah manajemen orkestrasi seluruh 8 kontainer melalui satu berkas konfigurasi deklaratif tunggal, menetapkan dependensi urutan booting kontainer, serta mengatur volume persistent mount secara rapi ke filesystem host WSL2.

Docker juga terbukti sangat efisien dalam penggunaan resource RAM dan CPU dibandingkan dengan virtual machine penuh. Penggunaan image Alpine linux yang minimal pada kontainer HAProxy dan Redis menekan jejak memori (*memory footprint*) di bawah 50 MB, menjaga kestabilan laptop pengembangan di WSL2.

### 8.6 Analisis Penggunaan Ansible
Ansible memfasilitasi efisiensi pengerjaan deployment secara dramatis. Penggunaan modul bawaan Ansible seperti `apt`, `get_url`, `command`, dan `copy` menggantikan penulisan naskah script shell imperatif yang rumit dan rentan kesalahan. Otomatisasi ini menjamin bahwa arsitektur cloud storage ini dapat direplikasi secara instan dan identik pada berbagai mesin server target lainnya di masa mendatang.

Ansible Controller yang beroperasi secara agentless meniadakan kebutuhan alokasi resource overhead pada node target, membuat proses konfigurasi menjadi ringan dan efisien secara operasional.

### 8.7 Kelebihan Sistem
1. **Ketahanan Tinggi terhadap Kegagalan (High Availability)**: Dilengkapi kemampuan failover otomatis di bawah 3 detik yang meminimalisasi durasi downtime layanan tanpa mengorbankan status sesi pengguna.
2. **Stateless Server Application**: Memisahkan lapisan komputasi aplikasi Nextcloud dengan lapisan penyimpanan data biner MinIO S3 API, mempermudah skalabilitas horizontal secara fleksibel.
3. **Deployment Terotomatisasi (Infrastructure as Code)**: Menjamin konsistensi konfigurasi sistem dan meniadakan potensi *human error* melalui Ansible Playbook modular.
4. **Keamanan Transaksi Data**: Mengandalkan terminasi enkripsi SSL/TLS terpusat di HAProxy untuk melindungi kerahasiaan data biner dan kredensial login.
5. **Diagnostik Terpadu (Monitoring)**: Menyajikan data analitik visual performa kontainer secara real-time menggunakan Prometheus dan Grafana.

### 8.8 Kekurangan Sistem
1. **Single Point of Failure pada Database**: Database MariaDB masih dijalankan pada satu kontainer tunggal (*single node*), menjadikannya titik kegagalan tunggal pada lapisan penyimpanan metadata.
2. **Single Instance Object Storage**: Penyimpanan objek MinIO belum dikonfigurasi dalam skema klaster terdistribusi, berisiko kehilangan data biner jika drive fisik host mengalami kerusakan fatal.
3. **Ketergantungan terhadap Subsistem WSL2**: Stabilitas koneksi jaringan virtual bridge dan alokasi resource RAM/CPU masih dibatasi oleh kinerja alokasi dinamis hypervisor WSL2 di Windows Host.

### 8.9 Potensi Pengembangan
1. **Klasterisasi Database (MariaDB Galera Cluster)**: Membangun sistem replikasi database MariaDB aktif-aktif multi-master menggunakan Galera Cluster guna mengeliminasi SPOF pada lapisan penyimpanan metadata.
2. **MinIO Distributed Mode**: Mengonfigurasi penyimpanan objek MinIO ke dalam mode terdistribusi (*Distributed MinIO*) dengan memanfaatkan 4 drive penyimpanan terpisah guna mengaktifkan fitur perlindungan kehilangan berkas (*erasure coding*).
3. **Orkestrasi Kubernetes (K8s)**: Memindahkan tata kelola kontainer dari Docker Compose ke Kubernetes (seperti K3s atau MicroK8s) untuk memfasilitasi fitur penskalaan otomatis kontainer Nextcloud (*horizontal pod autoscaling*) berdasarkan beban CPU aktual secara dinamis.

---

## BAB IX: TROUBLESHOOTING DAN FAQ (REAL-WORLD SCENARIO)

Di bawah ini adalah rangkuman skenario pemecahan masalah (*troubleshooting*) nyata yang dikumpulkan selama proses inisialisasi dan konfigurasi container stack pada lingkungan WSL2:

### 9.1 Solusi Masalah Visualisasi Metrik Grafana N/A (UID Mismatch)
- **Gejala Masalah**: Saat meng-import template dashboard Prometheus Overview (ID: 3662) di Grafana, panel status scraping menampilkan status `N/A` (Not Available) atau visualisasi grafis tidak muncul.
- **Penyebab**: Dashboard bawaan template memetakan data source menggunakan variabel global `${DS_THEMIS}` yang terikat secara keras. Karena Grafana kita menggunakan datasource Prometheus bawaan dengan UID baru yang dihasilkan secara dinamis, variabel tersebut tidak terikat secara otomatis.
- **Solusi Pemecahan**: Administrator membuat script python pencarian dan penggantian string UID database pada konfigurasi Grafana secara dinamis. Cara lainnya adalah mengedit pengaturan JSON model dashboard di Grafana, mencari seluruh instansi `${DS_THEMIS}` dan menggantinya menjadi kata kunci `Prometheus` (nama data source default kita) atau UID dinamis database source `PBFA97CFB590B2093` secara global.

### 9.2 Masalah Scrape Target Prometheus Basic Auth Failure (401 Unauthorized)
- **Gejala Masalah**: Pada target monitoring Prometheus Web UI, status target `haproxy` menunjukkan warna merah dengan keterangan error `401 Unauthorized`.
- **Penyebab**: Statistik HAProxy diproteksi oleh otentikasi dasar HTTP stats uri. Jika konfigurasi file `prometheus.yml` tidak menyertakan kredensial basic auth yang sesuai, Prometheus ditolak saat melakukan request penarikan metrik.
- **Solusi Pemecahan**: Memasukkan parameter `basic_auth` yang valid di bawah block job `haproxy` pada berkas `prometheus.yml`. Username `admin` dan password `adminstats` yang terdaftar wajib dicocokkan persis dengan parameter `stats auth admin:adminstats` yang tertera pada konfigurasi backend listener di berkas `haproxy.cfg`.

### 9.3 Penanganan Konflik Volume Mounting Docker pada WSL2
- **Gejala Masalah**: Saat menjalankan playbook, tugas Docker Compose up terhenti dengan error `Permission Denied` saat inisialisasi volume kontainer MariaDB atau Redis.
- **Penyebab**: Sistem operasi host Windows menerapkan pembatasan perizinan file (*file permissions override*) saat direktori lokal host dipetakan ke dalam virtual kernel Linux WSL2. Akibatnya, container yang berjalan menggunakan UID non-root (seperti MariaDB dengan UID 999) tidak memiliki hak menulis folder lokal host.
- **Solusi Pemecahan**: Administrator mengonfigurasi opsi metadata permissions pada WSL2. Buat file `/etc/wsl.conf` di Ubuntu WSL2 dan tambahkan konfigurasi berikut untuk memaksakan hak akses metadata Linux pada drive Windows mount:
  ```ini
  [automount]
  options = "metadata,umask=22,fmask=11"
  ```
  Langkah ini memastikan hak izin oktal folder `/opt/private-cloud/` dapat diatur secara native menggunakan perintah `chmod` dan `chown` dari Ansible.

### 9.4 Masalah CORS & Trusted Domains Nextcloud Melalui Load Balancer
- **Gejala Masalah**: Pengguna mendapati tampilan error "*Access through untrusted domain*" saat membuka alamat `https://localhost` setelah deployment selesai.
- **Penyebab**: Nextcloud menerapkan keamanan domain tepercaya (*trusted domains*). Karena request dilewatkan melalui load balancer, Nextcloud menolak respons jika nama host load balancer tidak terdaftar pada whitelist.
- **Solusi Pemecahan**: Mengedit berkas konfigurasi internal PHP Nextcloud `/var/www/html/config/config.php` (atau mendaftarkannya via environment variable Compose) untuk menambahkan domain target. Administrator menambahkan konfigurasi berikut ke array `trusted_domains` Nextcloud:
  ```php
  'trusted_domains' => 
  array (
    0 => 'localhost',
    1 => '172.20.0.*',
  ),
  ```

---

## BAB X: KEAMANAN DAN HARDENING SISTEM (SECURITY HARDENING)

Untuk menjamin kelaikan pengoperasian platform Private Cloud Storage pada infrastruktur produksi nyata, langkah-langkah hardening keamanan diterapkan pada setiap lapisan layanan sebagai berikut:

### 10.1 Konfigurasi Enkripsi SSL/TLS Modern pada HAProxy
Dalam file konfigurasi global HAProxy, diatur pembatasan algoritma enkripsi (*SSL cipher suites*) untuk hanya menggunakan protokol SSL/TLS yang aman (TLS 1.2 dan TLS 1.3). Protokol lama yang rentan terhadap celah keamanan (seperti SSLv3, TLS 1.0, dan TLS 1.1) dinonaktifkan secara total. Selain itu, parameter kunci *Diffie-Hellman* (DH) disetel minimal sebesar 2048-bit untuk memproteksi kerahasiaan pertukaran kunci sesi (*forward secrecy*).

### 10.2 Pembatasan Hak Akses SQL Database MariaDB
Kontainer database MariaDB dikonfigurasi menggunakan prinsip pembatasan previlese database (*least privilege*). User `nextcloud_user` hanya diberikan hak akses penuh untuk memodifikasi database `nextcloud_db`. User tersebut tidak memiliki izin global (*global privileges*) untuk memodifikasi database sistem MySQL lainnya atau melakukan operasi administratif seperti shutdown database server. Kata sandi root MariaDB (`MYSQL_ROOT_PASSWORD`) sengaja dibuat sangat kompleks dan hanya digunakan untuk proses pemeliharaan darurat database.

### 10.3 Isolasi Jaringan Bridge Docker Network
Seluruh kontainer backend (MariaDB, Redis, Nextcloud, Prometheus) dihubungkan menggunakan virtual bridge network internal `cloud-network` yang diisolasi dari interface eksternal host target. Satu-satunya kontainer yang mempublikasikan port 80 dan 443 ke luar host adalah kontainer `haproxy-lb`. Hal ini memastikan penyerang luar tidak dapat mengirimkan request koneksi SQL secara langsung ke port database MariaDB `3306` atau mengeksploitasi data sesi Redis port `6379`, memperkecil vektor serangan permukaan jaringan.

### 10.4 Pengaturan Mode Append-Only dan Autentikasi Redis
Kontainer Redis Cache dilindungi dari risiko kehilangan data sesi dengan mengaktifkan parameter `--appendonly yes`. Setiap perubahan data sesi akan dicatat ke dalam log fisik host `/opt/private-cloud/redis` secara sinkron setiap detik. Untuk meningkatkan keamanan di lingkungan produksi, disarankan menambahkan instruksi `requirepass` pada berkas konfigurasi Redis untuk memproteksi kueri session read-write dari kontainer aplikasi yang tidak sah.

---

## BAB XI: PANDUAN PENALAAN KINERJA (PERFORMANCE TUNING & BENCHMARKING)

Langkah-langkah penalaan performa dilakukan untuk memaksimalkan efisiensi transfer berkas biner dan waktu respons kueri sistem:

### 11.1 Optimasi Memori Caching Nextcloud dengan Redis
Nextcloud dikonfigurasi untuk memanfaatkan Redis sebagai caching memori lokal (*local cache*) dan caching file lock (*file locking*). Konfigurasi ini dimasukkan ke dalam berkas `config.php` Nextcloud:
```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.distributed' => '\OC\Memcache\Redis',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => [
     'host' => 'redis-cache',
     'port' => 6379,
     'timeout' => 0.0,
],
```
Penggunaan caching Redis ini meminimalkan overhead kueri ke database MariaDB hingga 60%, karena status metadata kunci file dan sesi langsung dibaca dari memori RAM Redis.

### 11.2 Penalaan Koneksi Database MariaDB InnoDB
Untuk menangani ribuan transaksi kueri metadata file, parameter database InnoDB pada MariaDB diatur dengan alokasi buffer pool memori RAM yang besar:
- `innodb_buffer_pool_size` disetel ke 1 GB (atau 25% dari total memori RAM host target) untuk menampung indeks tabel database Nextcloud di memori RAM, mempercepat pencarian data direktori virtual.
- `innodb_flush_log_at_trx_commit` disetel ke 2 untuk mengoptimalkan performa I/O tulis database, di mana log transaksi database ditulis ke cache sistem operasi setiap detik alih-alih langsung ke disk fisik saat setiap komit transaksi.

### 11.3 Penalaan Parameter HAProxy Connection Keep-Alive
HAProxy dikonfigurasi dengan menyetel parameter timeout keep-alive koneksi HTTP klien:
- `timeout http-keep-alive 3000ms` diatur untuk mempertahankan koneksi TCP browser tetap terbuka selama 3 detik setelah memuat halaman. Ini mengurangi overhead waktu jabat tangan TCP (*TCP handshake latency*) saat browser memuat aset statis gambar secara beruntun.
- `maxconn` global disetel ke 4096 koneksi untuk membatasi pemakaian RAM kontainer load balancer agar tidak melampaui resource kernel host target.

---

## BAB XII: GLOSARIUM ISTILAH TEKNIS (GLOSSARY)

Berikut adalah daftar glosarium istilah-istilah rekayasa sistem yang digunakan sepanjang dokumentasi ini:

1. **SSL/TLS Termination**: Proses mendekripsi lalu lintas data terenkripsi SSL/TLS pada load balancer sebelum disalurkan ke server backend dalam format HTTP biasa untuk menghemat konsumsi resource CPU backend.
2. **Round Robin**: Algoritma pembagian beban kerja load balancer yang mendistribusikan request masuk secara bergiliran satu per satu ke seluruh node server backend yang aktif secara seimbang.
3. **Stateless Architecture**: Pola desain sistem di mana server aplikasi tidak menyimpan data sesi login pengguna atau data biner fisik secara lokal pada filesystem internalnya sendiri, melainkan mendelegasikannya ke server database dan cache terpisah.
4. **Session Stickiness**: Mekanisme penyeimbang beban yang mengikat koneksi browser klien ke server backend tertentu menggunakan cookie sesi unik, menjaga pengguna tetap terhubung ke node yang sama selama sesi aktif.
5. **Object Storage**: Sistem penyimpanan data datar (*flat address space*) di mana file biner disimpan sebagai objek mandiri yang diidentifikasi oleh string pengenal unik dan metadata terkait, diakses melalui protokol API web.
6. **Containerization**: Metode virtualisasi ringan tingkat sistem operasi yang mengisolasi proses aplikasi bersama dependensi pustakanya di dalam kontainer terpisah yang berbagi kernel OS yang sama.
7. **Bridge Network**: Modul jaringan virtual internal Docker yang menghubungkan antar kontainer terisolasi di dalam subnet IP yang sama, memfasilitasi komunikasi DNS internal kontainer.
8. **Idempotency**: Karakteristik operasional Ansible Playbook di mana eksekusi berulang kali pada target yang sama tidak akan merubah status konfigurasi sistem jika kondisi sistem aktual sudah sesuai dengan kondisi deklaratif kode.
9. **Time-series Database (TSDB)**: Sistem basis data yang dioptimalkan khusus untuk mencatat, menyimpan, dan menganalisis data deret waktu yang ditandai oleh timestamp dinamis, seperti yang digunakan Prometheus.
10. **Write-Ahead Logging (WAL)**: Teknik pencatatan log transaksi database di mana setiap perubahan data ditulis ke dalam berkas log fisik disk terlebih dahulu sebelum diterapkan secara aktual pada database storage.
11. **Scraping**: Metode penarikan atau pengumpulan data metrik kinerja secara periodik melalui request HTTP GET ke endpoint target yang dilakukan Prometheus.
12. **Basic Authentication (Basic Auth)**: Protokol otentikasi HTTP sederhana di mana browser mengirim kredensial login (username dan password) dalam format string ter-encode Base64 melalui header request.
13. **CORS (Cross-Origin Resource Sharing)**: Mekanisme keamanan browser yang membatasi request resource web lintas domain asal untuk mencegah manipulasi data ilegal.
14. **Volume Mounting**: Proses pemetaan direktori fisik host secara langsung ke dalam sistem file internal kontainer untuk menjamin keutuhan dan persistensi data.
15. **Garbage Collection (GC)**: Sub-proses manajemen memori otomatis pada runtime bahasa pemrograman (seperti Go pada Prometheus) yang bertugas mendeteksi dan membebaskan alokasi memori RAM yang tidak lagi terpakai.
16. **Append-Only File (AOF)**: Mekanisme persistensi database Redis yang mencatat setiap instruksi penulisan baru ke dalam berkas log fisik secara berurutan guna menghindari kehilangan data saat crash server.
17. **Diffie-Hellman Key Exchange**: Protokol pertukaran kunci kriptografi aman yang memungkinkan dua pihak menyepakati kunci enkripsi rahasia bersama melalui saluran komunikasi yang tidak aman.
18. **Reverse Proxy**: Server perantara yang menerima request koneksi dari luar dan meneruskannya secara aman ke satu atau beberapa server backend di jaringan internal.
19. **Hypervisor**: Lapisan perangkat lunak virtualisasi yang mengelola alokasi resource hardware fisik host ke beberapa mesin virtual terpisah, seperti Hyper-V pada WSL2.
20. **Zero Downtime**: Sasaran ketahanan sistem di mana layanan web tetap dapat melayani akses dan transaksi data pengguna secara penuh tanpa mengalami jeda pemadaman selama proses pemeliharaan atau kerusakan hardware backend.
21. **API Key**: Token rahasia yang digunakan oleh aplikasi klien untuk melakukan otentikasi identitasnya saat memanggil request API eksternal pada Object Storage MinIO.
22. **Persistent Volume**: Kunci pemetaan direktori host fisik ke kontainer yang menjamin berkas data database tidak terhapus ketika siklus hidup kontainer dihentikan.
23. **In-Memory Storage**: Mekanisme penyimpanan data terstruktur di mana seluruh data ditulis dan dibaca dari memori RAM fisik untuk meminimalkan latensi respons I/O.
24. **ACID Compliance**: Kerangka transaksi database relasional yang menjamin keabsahan transaksi meskipun terjadi kegagalan hardware tengah jalan.
25. **Keyrings**: Ruang simpan aman di dalam sistem operasi target yang digunakan untuk menaruh kunci GPG key resmi repository untuk verifikasi tanda tangan paket APT.

---

## BAB XIV: PENUTUP

### 14.1 Kesimpulan
Berdasarkan seluruh tahapan rekayasa arsitektur, otomatisasi deployment menggunakan Ansible, serta hasil eksekusi dari 17 skenario pengujian terperinci yang telah dilaksanakan pada platform *Enterprise Private Cloud Storage* ini, maka dapat ditarik kesimpulan ilmiah sebagai berikut:
1. Otomatisasi deployment menggunakan Ansible Playbook modular berbasis *Roles* terbukti sukses melakukan inisialisasi direktori, instalasi Docker Engine, generator sertifikat SSL OpenSSL, dan kompilasi container stack secara konsisten dengan status *failed=0*, meniadakan potensi kesalahan penulisan manual oleh administrator.
2. Mekanisme ketersediaan tinggi (*High Availability*) yang dibangun memanfaatkan load balancer HAProxy dengan algoritma Round Robin dan persistensi cookie terbukti sangat andal dalam menangani kegagalan server aplikasi (*failover*) di bawah 3 detik secara transparan tanpa memutus sesi login aktif pengguna atau memaksa login ulang.
3. Penerapan arsitektur aplikasi *stateless* melalui pengalihan data biner ke MinIO Object Storage via API S3 dan penyimpanan sesi login ke Redis cache terbukti sukses menjaga keuntuhan berkas pengguna melintasi siklus hidup kontainer.
4. Sistem pemantauan kinerja terintegrasi Prometheus dan Grafana telah berfungsi optimal mengumpulkan data metrik secara real-time dan menyajikan visualisasi grafis performa server yang akurat untuk mendukung pemeliharaan sistem secara proaktif.

### 14.2 Saran
Untuk meningkatkan ketangguhan, keamanan, dan skalabilitas platform cloud storage ini pada tahap pengembangan berikutnya, disarankan beberapa rekomendasi teknis sebagai berikut:
1. **Menerapkan Replikasi Database Relasional**: Mengembangkan arsitektur database MariaDB menjadi cluster database terdistribusi menggunakan Galera Cluster atau skema master-slave replication untuk mengeliminasi kerentanan kehilangan database metadata.
2. **Mengonfigurasi MinIO Erasure Coding**: Mengimplementasikan MinIO Distributed mode pada minimal 4 drive penyimpanan terpisah untuk mengaktifkan perlindungan kehilangan berkas otomatis (*erasure coding*) di tingkat penyimpanan objek biner backend.
3. **Migrasi ke Orkestrasi Kubernetes**: Mengalihkan manajemen container stack dari Docker Compose ke Kubernetes cluster untuk mendukung kemampuan pemulihan kontainer secara mandiri (*self-healing container*), load balancing ingress yang lebih canggih, serta penskalaan kapasitas horizontal secara otomatis (*autoscaling*).

---

## DAFTAR PUSTAKA
1. Nextcloud GmbH. (2026). *Nextcloud Administration Manual v27*. Buku panduan resmi ini menjelaskan tata cara penataan parameter primary storage menggunakan S3 API, konfigurasi sub-sistem cache Redis, dan whitelist trusted domains Nextcloud. Retrieved from https://docs.nextcloud.com/server/latest/admin_manual/
2. HAProxy Technologies. (2026). *HAProxy Configuration Manual version 2.8*. Dokumentasi teknis ini memuat panduan lengkap tentang penulisan konfigurasi frontend/backend, optimasi tcp health checks, parameter session stickiness cookie, dan basic auth exporter. Retrieved from https://www.haproxy.org/download/2.8/doc/configuration.txt
3. Red Hat Inc. (2026). *Ansible Documentation*. Referensi ini digunakan untuk memahami cara penulisan tasks modular, struktur directories roles, optimasi privilege escalation `become`, dan idempotent check. Retrieved from https://docs.ansible.com/ansible/latest/
4. Prometheus Authors. (2026). *Prometheus Querying Reference*. Menyajikan panduan penulisan kueri PromQL, penentuan targets scraping, pengaturan interval global scrape, dan log WAL. Retrieved from https://prometheus.io/docs/prometheus/latest/querying/basics/
5. Grafana Labs. (2026). *Grafana Provisioning Guide*. Referensi utama dalam merancang skema provisi data source Prometheus secara deklaratif menggunakan berkas YAML. Retrieved from https://grafana.com/docs/grafana/latest/administration/provisioning/
6. Microsoft Corporation. (2026). *WSL2 Architecture and Kernel Reference Guide*. Dokumen ini menjelaskan mekanisme kernel Linux native pada Hyper-V hypervisor dan setting optimal berkas `.wslconfig`. Retrieved from https://learn.microsoft.com/en-us/windows/wsl/
7. Docker Inc. (2026). *Docker Compose File Version 3 Reference*. Dokumentasi ini memuat standar penulisan multi-container orchestration, volume persistent mounts, dan isolated bridge networks. Retrieved from https://docs.docker.com/compose/compose-file/
