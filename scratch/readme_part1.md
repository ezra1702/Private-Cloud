# LAPORAN TUGAS AKHIR
## Mata Kuliah: Administrasi Sistem Server

---

# RANCANG BANGUN PLATFORM ENTERPRISE PRIVATE CLOUD STORAGE BERBASIS NEXTCLOUD DENGAN INTEGRASI OBJECT STORAGE MINIO, CACHING REDIS, KEAMANAN SSL/TLS, DAN HIGH AVAILABILITY TEROTOMATISASI MENGGUNAKAN ANSIBLE ROLES BERBASIS DOCKER CONTAINER PADA WSL2

```text
                                  _     _             _ 
  /\/\  _   _| |_  __ _  ___ ___ | |   (_)_ __  _   _| | __
 /    \| | | | __|/ _` |/ __/ __|| |   | | '_ \| | | | |/ /
/ /\/\ \ |_| | |_| (_| | (_| \__ \| |___| | | | | |_| |   < 
\/    \/\__,_|\__|\__,_|\___|___/|_____|_|_| |_|\__,_|_|\_\
                                                            
         [ ENTERPRISE PRIVATE CLOUD ARCHITECTURE ]
```

### **Kelompok & Kontributor:**
* **Nama Anggota 1** - [NIM Kelompok 1]
* **Nama Anggota 2** - [NIM Kelompok 2]
* **Nama Anggota 3** - [NIM Kelompok 3]

**Dosen Pengampu:** [Nama Dosen Pengampu]  
**Program Studi:** Teknik Komputer  
**Universitas:** [Nama Universitas / Institusi]  
**Tahun:** 2026

---

## ABSTRAK
Perancangan platform penyimpanan awan pribadi (*private cloud storage*) berskala enterprise pada era modern menuntut jaminan integritas data, ketersediaan tinggi (*High Availability*), keamanan enkripsi lalu lintas data, serta efisiensi manajemen operasional server. Penelitian tugas akhir ini mengkaji secara komprehensif rancang bangun arsitektur penyimpanan awan stateless berbasis Nextcloud yang diintegrasikan dengan Object Storage MinIO via protokol API S3, database terpusat MariaDB, dan in-memory cache Redis sebagai pengelola sesi login pengguna serta transaction locking. Untuk meniadakan kegagalan sistem terpusat pada satu titik (*Single Point of Failure*), dirancang skema load balancing redundan menggunakan dua replika kontainer Nextcloud di balik load balancer HAProxy yang menerapkan algoritma *Round Robin* dan persistensi cookie. Seluruh rangkaian deployment sistem diotomatisasi secara deklaratif menggunakan Ansible Roles guna meminimalkan intervensi manual dan kesalahan konfigurasi operasional pada hypervisor WSL2 (Ubuntu 22.04 LTS). Pemantauan kesehatan serta diagnostik performa kontainer disajikan secara real-time melalui integrasi Prometheus metrics scraper dan dasbor visualisasi Grafana. Hasil pengujian terhadap 17 skenario menunjukkan bahwa otomatisasi Ansible berhasil melakukan instalasi dengan status *failed=0*, load balancer HAProxy mampu melakukan pemindahan beban trafik (*failover*) di bawah 3 detik tanpa memutus sesi login aktif pengguna, dan arsitektur stateless berhasil mempertahankan integritas data biner di Object Storage MinIO.

Kata Kunci: *Private Cloud*, *High Availability*, *Stateless Architecture*, *Ansible Roles*, *Load Balancing*, *Docker Containers*.

---

## KATA PENGANTAR
Puji syukur kami panjatkan ke hadirat Tuhan Yang Maha Esa karena atas rahmat dan karunia-Nya kami dapat menyelesaikan laporan Tugas Akhir untuk mata kuliah Administrasi Sistem Server ini dengan tepat waktu. Proyek rancang bangun sistem yang kami beri judul "Rancang Bangun Platform Enterprise Private Cloud Storage Berbasis Nextcloud dengan Integrasi Object Storage MinIO, Caching Redis, Keamanan SSL/TLS, dan High Availability Terotomatisasi Menggunakan Ansible Roles Berbasis Docker Container pada WSL2" ini merupakan hasil kerja keras, kolaborasi, dan dedikasi seluruh anggota kelompok selama satu semester perkuliahan. Laporan ini disusun secara komprehensif dan mendalam untuk menyajikan cetak biru (*blueprint*) rekayasa infrastruktur server berskala industri yang tangguh, otomatis, aman, dan terpantau secara berkala.

Kami menyadari bahwa penyusunan laporan dan keberhasilan proyek ini tidak lepas dari bimbingan, arahan, dan dukungan dari berbagai pihak. Oleh karena itu, kami ingin mengucapkan terima kasih sebesar-besarnya kepada Bapak Dosen Pengampu mata kuliah Administrasi Sistem Server yang telah memberikan ilmu, saran teknis, serta motivasi yang tiada henti sepanjang semester ini. Terima kasih juga kami sampaikan kepada rekan-rekan mahasiswa Program Studi Teknik Komputer atas diskusi, kritik, dan masukan konstruktif yang membantu kami menyempurnakan arsitektur sistem ini. Kami berharap laporan ini tidak hanya berfungsi sebagai pemenuhan syarat penilaian akademis akademik, melainkan dapat menjadi sumber referensi praktis yang berguna bagi mahasiswa lain maupun praktisi IT dalam memahami integrasi teknologi administrasi server modern. Kami menyadari masih terdapat keterbatasan dalam sistem ini, oleh karena itu kritik dan saran yang membangun sangat kami harapkan untuk pengembangan sistem lebih lanjut di masa depan.

---

## BAB I: PENDAHULUAN

### 1.1 Latar Belakang
Perkembangan teknologi informasi dan komunikasi yang sangat pesat pada era digitalisasi saat ini telah membawa dampak perubahan yang signifikan bagi tata kelola penyimpanan data di berbagai organisasi. Data digital tidak lagi hanya sekadar berkas dokumen pasif, melainkan telah menjadi aset strategis utama yang menunjang kelangsungan operasional korporasi skala enterprise, instansi pemerintah, institusi akademis, hingga pelaku industri kecil. Kebutuhan akan ruang penyimpanan berkas yang berkapasitas besar, fleksibel, terenkripsi aman, serta dapat diakses secara instan lintas perangkat (*cross-platform access*) dari mana saja dan kapan saja telah mendorong pergeseran masif paradigma penyimpanan lokal (*on-premise local hard drive*) ke arah teknologi komputasi awan atau *cloud computing*.

Dalam lanskap komputasi awan komersial saat ini, layanan penyimpanan awan publik (*public cloud storage*) seperti Google Drive, Microsoft OneDrive, Dropbox, dan Box mendominasi pasar global. Layanan ini menawarkan kemudahan aksesibilitas instan tanpa mengharuskan organisasi berinvestasi pada penyediaan perangkat keras fisik, konfigurasi jaringan, maupun pemeliharaan server secara berkala. Browser web dan aplikasi klien mobile yang matang membuat kolaborasi dokumen real-time menjadi sangat praktis. Namun, bagi organisasi berskala besar yang menangani informasi berkategori rahasia, sangat sensitif, atau terikat oleh kepatuhan hukum, ketergantungan penuh pada platform *public cloud* melahirkan berbagai tantangan krusial yang menyangkut keamanan, kepatuhan hukum, biaya jangka panjang, serta hilangnya kontrol fisik terhadap data organisasi.

Tantangan paling utama yang dihadapi oleh administrator sistem adalah masalah kedaulatan data (*data sovereignty*). Di bawah kerangka regulasi privasi internasional seperti *General Data Protection Regulation* (GDPR) di Uni Eropa, serta regulasi domestik seperti Undang-Undang Perlindungan Data Pribadi (UU PDP) di Indonesia, setiap instansi yang mengumpulkan dan memproses data pribadi warga negara wajib memiliki kendali mutlak atas lokasi geografis server fisik tempat data tersebut disimpan. Pada arsitektur *public cloud*, data biner pengguna sering kali direplikasi dan didistribusikan lintas pusat data (*data centers*) di berbagai negara tanpa persetujuan eksplisit pemilik data. Kondisi ini menempatkan organisasi pada risiko pelanggaran hukum privasi data lokal jika server fisik penyedia jasa awan publik berada di yurisdiksi hukum negara asing.

Tantangan kedua berkaitan dengan aspek ekonomi dan biaya operasional jangka panjang. Model bisnis *public cloud* menerapkan skema langganan bulanan (*subscription-based pay-as-you-go*) yang terlihat murah pada tahap awal deployment skala kecil. Namun, ketika volume penyimpanan membengkak hingga mencapai puluhan terabyte dengan pengguna aktif ribuan orang, biaya sewa bulanan dan biaya lalu lintas pengunduhan data keluar (*egress fees*) akan terakumulasi menjadi pengeluaran modal operasional (*OpEx*) yang sangat besar dan bersifat permanen. Bagi institusi akademis atau instansi pemerintah dengan anggaran tahunan terbatas, pembengkakan biaya langganan awan publik ini menjadi tidak efisien dan tidak berkelanjutan. Ditambah lagi, risiko kebocoran data (*data breach*) akibat kerentanan celah keamanan pada infrastruktur *multitenant* milik penyedia public cloud dapat berdampak fatal bagi reputasi instansi.

Sebagai langkah mitigasi yang efektif terhadap risiko-risiko di atas, perancangan dan implementasi platform *Private Cloud Storage* mandiri (*on-premise*) muncul sebagai jalan keluar terbaik. Dengan membangun platform penyimpanan awan pribadi di dalam infrastruktur internal sendiri, organisasi memiliki kedaulatan mutlak atas enkripsi data, penentuan hak akses pengguna, pemetaan log audit, serta penentuan lokasi fisik tempat data biner disimpan. Untuk mewujudkan platform kolaboratif yang tangguh dan kaya akan fitur, perangkat lunak Nextcloud dipilih sebagai perangkat lunak open-source utama. Nextcloud menyediakan antarmuka penyimpanan dokumen yang modern, aman, serta memiliki ekosistem aplikasi tambahan yang sangat luas untuk menunjang produktivitas. Namun, deployment standar Nextcloud pada satu server tunggal (*single node*) sangat rentan terhadap gangguan operasional. Apabila server tunggal tersebut mengalami crash hardware, kehabisan resource memori, serangan keamanan, atau kegagalan sistem operasi, seluruh layanan penyimpanan awan akan mengalami kelumpuhan total (*downtime*).

Untuk meniadakan kerentanan sistem terpusat pada satu titik (*single point of failure*), diperlukan perancangan arsitektur berkapasitas industri yang memiliki ketahanan tinggi (*High Availability*) dan skalabilitas yang andal. Arsitektur ini dirancang dengan memisahkan server aplikasi Nextcloud menjadi beberapa replika kontainer di balik Load Balancer HAProxy. Seluruh data biner yang diunggah dipindahkan ke lapisan penyimpanan *stateless* menggunakan Object Storage eksternal yang kompatibel dengan protokol API S3 (MinIO). Transaksi metadata disinkronkan ke server database terpusat MariaDB, sedangkan data sesi pengguna (*user session*) dan mekanisme penguncian file (*file transaction locking*) ditangani oleh Redis cache. Melalui pemisahan lapisan aplikasi, database, cache, dan penyimpanan biner ini, kegagalan pada salah satu node aplikasi Nextcloud tidak akan memutus sesi aktif pengguna atau menyebabkan terjadinya kehilangan data.

Pembangunan arsitektur terdistribusi multi-kontainer ini memiliki tingkat kompleksitas instalasi dan konfigurasi yang sangat tinggi. Kesalahan manusia (*human error*) dalam penulisan parameter, konflik dependensi sistem operasi, serta inkonsistensi deployment antar lingkungan server menjadi tantangan utama bagi administrator sistem. Oleh karena itu, konsep *Infrastructure as Code* (IaC) diterapkan dengan memanfaatkan Ansible Playbook modular berbasis *Roles*. Ansible secara otomatis menangani instalasi mesin Docker, pembuatan sertifikat keamanan SSL/TLS *self-signed*, inisialisasi volume penyimpanan persisten, penyalinan file konfigurasi, hingga kompilasi dan orkestrasi seluruh kontainer. Seluruh sistem ini disimulasikan di dalam lingkungan Windows Subsystem for Linux 2 (WSL2) yang mengintegrasikan virtualisasi kernel Linux secara efisien dengan sistem operasi host Windows, menciptakan lingkungan simulasi enterprise yang tangguh, mudah dikembangkan, dan siap untuk dipindahkan ke lingkungan server produksi sesungguhnya.

### 1.2 Rumusan Masalah
Berdasarkan latar belakang masalah yang telah dipaparkan secara komprehensif, maka rumusan masalah yang menjadi fokus utama dalam perancangan dan pengujian sistem ini adalah sebagai berikut:
1. Bagaimana mengonfigurasi otomatisasi penyediaan (*provisioning*) lingkungan virtualisasi WSL2, instalasi Docker Engine, dan penyalinan konfigurasi server menggunakan skrip deklaratif Ansible Roles secara konsisten dan terbebas dari *human error*?
2. Bagaimana merancang skema load balancing berbasis HAProxy yang menerapkan enkripsi SSL/TLS Termination serta algoritma Round Robin dan stickiness cookie untuk mendistribusikan trafik browser ke dua replika server Nextcloud?
3. Bagaimana mengintegrasikan aplikasi Nextcloud dengan database MariaDB terpusat, Redis cache, dan Object Storage MinIO agar server aplikasi Nextcloud dapat beroperasi secara stateless tanpa menulis data sesi atau berkas fisik secara lokal?
4. Bagaimana menguji ketahanan failover klaster server aplikasi ketika salah satu kontainer Nextcloud dimatikan paksa, serta mengukur durasi pemulihan otomatis (*auto-recovery*) yang dilakukan oleh load balancer HAProxy?
5. Bagaimana mengonfigurasi scraping metrik kinerja menggunakan Prometheus server pada port stats HAProxy dan memprovisikan datanya ke Grafana Dashboard secara real-time untuk keperluan diagnostik stabilitas sistem?

### 1.3 Tujuan Proyek
Tujuan ilmiah dan praktis yang ingin dicapai melalui pelaksanaan proyek Tugas Akhir ini adalah sebagai berikut:
1. Membangun dan mengonfigurasi lingkungan virtualisasi server multi-kontainer Docker yang stabil di dalam kernel Windows Subsystem for Linux 2 (WSL2) dengan distro Ubuntu 22.04 LTS.
2. Menyusun naskah otomatisasi deklaratif Ansible Playbook berbasis struktur Roles modular (`common`, `docker`, `certificates`, `loadbalancer`, `nextcloud`) untuk memfasilitasi penyiapan sistem secara idempotent dari kondisi kosong.
3. Mengonfigurasi HAProxy sebagai gerbang reverse proxy terdepan terenkripsi SSL/TLS Termination 2048-bit, serta menerapkan pemindahan beban dinamis (*failover*) ke server backend cadangan secara transparan.
4. Mengintegrasikan server database relasional MariaDB terpusat, session store Redis cache dengan mode AOF (Append-Only File), serta platform S3-compatible API Object Storage MinIO guna mendukung arsitektur Nextcloud stateless.
5. Menyusun dashboard pemantauan visual Grafana yang terhubung ke server database Prometheus untuk menyajikan grafik visualisasi kinerja CPU, RAM, latensi scrape, status keaktifan kontainer, dan manajemen memori.

### 1.4 Manfaat Proyek
Adapun manfaat rekayasa dan nilai guna yang dapat diperoleh dari keberhasilan perancangan proyek sistem ini meliputi beberapa aspek berikut:
1. **Bagi Instansi/Perusahaan**: Menyediakan cetak biru (*blueprint*) rancang bangun penyimpanan awan internal mandiri yang aman, tangguh, memiliki ketersediaan tinggi, patuh terhadap regulasi privasi data lokal (seperti UU PDP), serta memangkas alokasi biaya pengeluaran rutin sewa public cloud dalam jangka panjang.
2. **Bagi Administrator Jaringan/Server**: Memberikan framework pemeliharaan infrastruktur server berbasis teknologi Infrastructure as Code (IaC) yang terstandarisasi, meminimalkan waktu perbaikan server jika terjadi crash fatal, serta menyajikan sistem monitoring performa proaktif yang mudah dikelola.
3. **Bagi Pengembangan Ilmu Pengetahuan**: Memberikan dokumentasi ilmiah yang mendalam dan teruji secara empiris mengenai integrasi praktis antara konsep-konsep inti administrasi sistem server modern (Virtualisasi, Kontainerisasi, High Availability, Load Balancing, Object Storage, Automasi, dan Diagnostik Pemantauan) untuk memperkaya literatur rekayasa sistem di Teknik Komputer.

---

## BAB II: LANDASAN TEORI

### 2.1 Nextcloud Application Server Architecture
Nextcloud merupakan platform perangkat lunak kolaboratif open-source terkemuka yang dirancang untuk menyediakan layanan penyimpanan awan pribadi terkelola secara mandiri (*self-hosted cloud storage hub*). Secara arsitektur, Nextcloud dibangun menggunakan bahasa pemrograman PHP untuk penanganan logika backend dan HTML5/Javascript untuk interaksi antarmuka pengguna pada browser. Nextcloud berjalan di atas web server HTTP Apache atau Nginx, dan mengandalkan database relasional (seperti MariaDB, MySQL, atau PostgreSQL) untuk penyimpanan data konfigurasi relasional dan metadata.

Nextcloud memiliki rancangan arsitektur penyimpanan yang sangat fleksibel. Secara default, Nextcloud menyimpan berkas data biner yang diunggah pengguna pada filesystem lokal server target di folder `/var/www/html/data`. Namun, untuk deployment berskala industri dengan beban trafik tinggi dan tuntutan ketersediaan tinggi, konfigurasi penyimpanan primer Nextcloud dapat dialihkan ke Object Storage eksternal yang kompatibel dengan protokol API S3 (seperti AWS S3 atau MinIO). Ketika menggunakan Object Storage sebagai media penyimpanan primer, kontainer Nextcloud beroperasi dalam mode *stateless*.

Dalam mode stateless ini, Nextcloud tidak lagi melakukan penulisan file fisik pada penyimpanan lokal kontainer. Setiap file biner yang diunggah oleh pengguna akan langsung diteruskan oleh Nextcloud melalui request S3 API ke server Object Storage MinIO. Database MariaDB mencatat metadata file tersebut (seperti nama berkas asli, mime-type, ukuran, hak kepemilikan, dan pengenal unik objek), sedangkan Redis menyimpan data token sesi login pengguna dan penguncian transaksi file. Pemisahan data biner dari server aplikasi Nextcloud ini memungkinkan beberapa kontainer Nextcloud berjalan secara paralel di balik load balancer untuk melayani pengguna yang sama tanpa mengalami masalah inkonsistensi data filesystem lokal.

### 2.2 MariaDB Database Management System
MariaDB merupakan sistem manajemen database relasional (*Relational Database Management System* - RDBMS) berskala enterprise yang dikembangkan sebagai percabangan (*fork*) dari MySQL. MariaDB diciptakan oleh para pengembang asli MySQL setelah MySQL diakuisisi oleh Oracle Corporation. Tujuan utama dari pengembangan MariaDB adalah untuk menjamin ketersediaan sistem database relasional yang sepenuhnya open-source, berkinerja tinggi, kompatibel dengan pustaka MySQL, serta kaya akan fitur mesin penyimpanan (*storage engines*) modern seperti Aria, MyRocks, dan ColumnStore.

Dalam sistem private cloud storage Nextcloud, MariaDB bertindak sebagai repositori metadata terpusat. MariaDB menyimpan seluruh informasi relasional krusial sistem, termasuk tabel konfigurasi sistem global, kredensial otentikasi login pengguna yang disimpan dalam format hash bcrypt aman, tabel pengelompokan grup divisi kerja, riwayat log audit keamanan, izin akses dokumen yang dibagikan (*sharing permissions*), serta data penanda waktu pembuatan berkas. Untuk menjamin konsistensi data relasional melintasi kegagalan server, MariaDB menerapkan prinsip transaksi ACID (*Atomicity, Consistency, Isolation, Durability*).

MariaDB ditempatkan di dalam kontainer terisolasi `mariadb-db` yang terhubung secara persisten ke direktori host WSL2 `/opt/private-cloud/mariadb`. Pemisahan database ke kontainer terdedikasi ini menjamin bahwa seluruh data metadata relasional organisasi terlindungi dari gangguan kegagalan operasional di lapisan server aplikasi Nextcloud. MariaDB dikonfigurasi dengan alokasi memori buffer pool InnoDB yang dioptimalkan agar mampu merespons ribuan kueri kueri baca-tulis dari dua replika Nextcloud secara efisien.

### 2.3 Redis Cache and Transaction Session Locking
Redis (*Remote Dictionary Server*) adalah sistem penyimpanan struktur data dalam memori (*in-memory data structure store*) open-source yang sangat cepat. Redis beroperasi dengan latensi di bawah milidetik karena seluruh operasi baca-tulis data diproses secara langsung di memori RAM server, bukan pada media penyimpanan disk mekanis. Redis mendukung berbagai macam struktur data canggih seperti hash, string, list, set, sorted set, dan hyperloglog, menjadikannya pilihan utama untuk kebutuhan caching performa tinggi dan pengelolaan sesi pengguna terdistribusi.

Dalam arsitektur ketersediaan tinggi Nextcloud, Redis menjalankan dua fungsi rekayasa yang sangat vital bagi stabilitas sistem:
1. **Penyimpanan Sesi Terdistribusi (Distributed Session Store)**: Menyimpan status login dan token sesi aktif pengguna secara terpusat. Ketika pengguna sedang mengakses cloud storage dan load balancer HAProxy mengalihkan koneksinya dari `nextcloud-app-1` ke `nextcloud-app-2` akibat peristiwa failover, sesi login pengguna tidak akan terputus. Server `nextcloud-app-2` akan membaca token sesi yang sama dari Redis cache, sehingga pengguna tidak perlu melakukan login ulang.
2. **Penguncian Transaksi Berkas (File Transaction Locking)**: Berperan krusial dalam mencegah terjadinya kerusakan data akibat konflik penulisan file simultan (*race condition*). Ketika seorang pengguna sedang melakukan proses modifikasi atau pengunggahan file, Nextcloud menginstruksikan Redis untuk mengunci id file tersebut. Jika pengguna lain mencoba memodifikasi file yang sama pada waktu bersamaan via replika Nextcloud kedua, Redis akan menolak request tersebut hingga proses penulisan pertama selesai dan kunci dibebaskan.

Redis dikonfigurasi dengan mengaktifkan fitur *Append-Only File* (AOF) via perintah `redis-server --appendonly yes`. Setiap modifikasi kunci sesi akan dicatat ke dalam log fisik disk host `/opt/private-cloud/redis` secara asinkron setiap detik, menjamin data cache dapat dipulihkan secara utuh setelah terjadi insiden crash server.

### 2.4 MinIO Object Storage and S3 API Compatibility
MinIO adalah platform penyimpanan objek (*object storage*) sumber terbuka berkinerja tinggi yang dirancang khusus untuk memenuhi standar arsitektur cloud native berskala besar. MinIO dikembangkan menggunakan bahasa pemrograman Go, memiliki footprint memori yang kecil, serta sepenuhnya kompatibel dengan protokol API S3 milik Amazon Web Services (AWS S3). Berbeda dengan sistem file tradisional (*POSIX file system*) yang menyimpan berkas dalam struktur hierarki folder bercabang, MinIO menyimpan data sebagai objek dalam ruang alamat datar (*flat namespace*) di dalam bucket.

Setiap objek di dalam MinIO diidentifikasi oleh kunci string unik dan terdiri dari dua komponen utama: data biner mentah (*payload*) dan data metadata (seperti tipe konten, penanda waktu, enkripsi, dan ukuran). MinIO sangat ideal digunakan sebagai lapisan backend penyimpanan biner untuk arsitektur stateless. Dengan memindahkan tanggung jawab penyimpanan berkas biner ke kontainer `minio-storage`, server Nextcloud tidak perlu memelihara partisi storage lokal, menyederhanakan konfigurasi skalabilitas.

MinIO juga menyediakan antarmuka grafis modern (MinIO Console) pada port `9001` yang mempermudah administrator mengelola bucket penyimpanan, mengontrol izin akses API key, serta memantau statistik lalu lintas data keluar-masuk secara visual. Konfigurasi primary storage Nextcloud dialihkan ke MinIO via port data `9000` menggunakan kredensial API key aman yang dikonfigurasi melalui variabel lingkungan otomatis di Docker Compose.
