# RANCANG BANGUN PLATFORM ENTERPRISE PRIVATE CLOUD STORAGE BERBASIS NEXTCLOUD DENGAN INTEGRASI OBJECT STORAGE MINIO, CACHING REDIS, KEAMANAN SSL/TLS, DAN HIGH AVAILABILITY TEROTOMATISASI MENGGUNAKAN ANSIBLE ROLES BERBASIS DOCKER CONTAINER PADA WSL2


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

### 5.5 Berkas Konfigurasi Ansible Target (`ansible/ansible.cfg`)
Berkas konfigurasi global untuk mengontrol perilaku eksekusi engine Ansible Controller.
```ini
[defaults]
inventory = inventory.ini
host_key_checking = False
deprecation_warnings = False
stdout_callback = yaml
bin_ansible_callbacks = True
```

#### Analisis Teknik Rekayasa Berkas `ansible.cfg`
Penjelasan mendalam mengenai parameter konfigurasi Ansible Controller adalah sebagai berikut:
- **`inventory = inventory.ini`**: Whitelist file inventory default. Parameter ini mengarahkan Ansible untuk secara otomatis memuat host target dari berkas `inventory.ini` di folder lokal tanpa mengharuskan administrator menulis opsi `-i` secara manual pada command line eksekusi.
- **`host_key_checking = False`**: Menonaktifkan verifikasi kunci SSH host target (*SSH Host Key Checking*). Konfigurasi ini sangat penting di lingkungan otomatisasi multi-server guna mencegah terhentinya playbook akibat konfirmasi interaktif sidik jari host target (`Are you sure you want to continue connecting (yes/no)?`) yang sering menggagalkan jalannya script otomatisasi background.
- **`stdout_callback = yaml`**: Mengatur format keluaran terminal. Dengan mengubah callback bawaan menjadi `yaml`, Ansible menampilkan log aktivitas tugas secara rapi menggunakan indentasi terstruktur yang lebih mudah dibaca dan dianalisis daripada format output standar yang berantakan.

### 5.6 Berkas Inventory Ansible (`ansible/inventory.ini`)
Berkas definisi pengelompokan host target yang dikelola oleh Ansible.
```ini
[cloud_servers]
localhost ansible_connection=local
```

#### Analisis Teknik Rekayasa Berkas `inventory.ini`
Penjelasan mendalam mengenai parameter berkas inventory adalah sebagai berikut:
- **`[cloud_servers]`**: Tag pengelompokan host target (*host group*). Mendefinisikan nama grup server agar playbook dapat memanggil konfigurasi secara spesifik hanya pada mesin target yang termasuk dalam divisi infrastruktur awan pribadi.
- **`localhost ansible_connection=local`**: Mendefinisikan target lokal. Opsi `ansible_connection=local` menginstruksikan Ansible Controller untuk tidak menggunakan protokol SSH biasa untuk terhubung, melainkan menggunakan API internal system calls Linux lokal. Hal ini mengeliminasi overhead otentikasi SSH, mempermudah deployment container stack di WSL2 tanpa membutuhkan server SSH daemon eksternal.

### 5.7 Berkas Ansible Playbook Utama (`ansible/site.yml`)
Berkas playbook utama yang mengimpor seluruh peran modular untuk dieksekusi secara berurutan.
```yaml
---
- name: Deploy Enterprise Private Cloud Storage Stack on WSL2
  hosts: cloud_servers
  become: yes
  vars:
    project_root: /opt/private-cloud
    ssl_cert_dir: /opt/private-cloud/config/ssl
    db_root_password: adminrootpassword
    db_name: nextcloud_db
    db_user: nextcloud_user
    db_password: nextcloudpassword
    minio_root_user: minioadmin
    minio_root_password: minioadminpassword
    minio_bucket: nextcloud

  tasks:
    - name: Mengimpor tugas sistem dasar (common)
      import_tasks: roles/common.yml

    - name: Mengimpor tugas instalasi Docker
      import_tasks: roles/docker.yml

    - name: Mengimpor tugas pembuatan sertifikat SSL
      import_tasks: roles/certificates.yml

    - name: Mengimpor tugas setup database MariaDB
      import_tasks: roles/database.yml

    - name: Mengimpor tugas setup Redis
      import_tasks: roles/redis.yml

    - name: Mengimpor tugas setup MinIO Object Storage
      import_tasks: roles/minio.yml

    - name: Mengimpor tugas setup Load Balancer
      import_tasks: roles/loadbalancer.yml

    - name: Mengimpor tugas setup Nextcloud & Run Stack
      import_tasks: roles/nextcloud.yml
```

#### Analisis Teknik Rekayasa Berkas `site.yml`
Penjelasan mendalam mengenai parameter eksekusi playbook utama adalah sebagai berikut:
- **Parameter `hosts: cloud_servers`**: Mengarahkan Ansible Controller untuk mencari daftar host target di dalam grup host `cloud_servers` yang telah didefinisikan dalam berkas inventory `inventory.ini`. Konfigurasi ini memungkinkan skalabilitas tinggi di mana administrator dapat dengan mudah menambah host server baru ke dalam grup tersebut untuk mengulang deployment otomatis secara massal.
- **Parameter `become: yes`**: Mengaktifkan sistem eskalasi hak istimewa (*privilege escalation*). Secara default, Ansible akan menjalankan perintah menggunakan utilitas `sudo` pada host target agar setiap tugas dapat dieksekusi dengan hak akses akun administrator `root`. Hal ini sangat penting untuk melakukan operasi tingkat rendah seperti memodifikasi sistem file kernel, mengubah konfigurasi firewall, membuat folder sistem `/opt/`, dan memasang paket perangkat lunak biner.
- **Blok `vars`**: Deklarasi variabel terpusat untuk mempermudah pemeliharaan kode. Nilai kredensial database, nama direktori, dan username disuplai ke seluruh modul task roles di bawahnya secara dinamis, mengeliminasi duplikasi penulisan parameter keras (*hardcoded parameters*) pada sub-file tugas.
- **Blok `tasks`**: Menggunakan modul `import_tasks` untuk membagi struktur tugas menjadi peran modular terpisah. Ini memisahkan tugas inisialisasi lingkungan dasar (`common.yml`), instalasi docker engine (`docker.yml`), pembuatan sertifikat TLS (`certificates.yml`), database persistent volumes (`database.yml`), cache volumes (`redis.yml`), object storage volumes (`minio.yml`), load balancer configs (`loadbalancer.yml`), dan kompilasi container stack (`nextcloud.yml`), mempermudah proses pemeliharaan script di masa depan.

### 5.8 Berkas Peran Ansible modular (`ansible/roles/`)

#### **`roles/common.yml`**
Tugas ini memastikan sistem dasar terupdate dan memiliki direktori kerja proyek `/opt/private-cloud`.
```yaml
---
- name: 1. Update cache APT
  apt:
    update_cache: yes
  when: ansible_os_family == "Debian"

- name: 2. Install dependensi sistem dasar
  apt:
    name:
      - curl
      - gnupg
      - ca-certificates
      - openssl
    state: present
  when: ansible_os_family == "Debian"

- name: 3. Buat direktori utama proyek di host target
  file:
    path: "{{ item }}"
    state: directory
    owner: root
    group: root
    mode: '0755'
  loop:
    - "{{ project_root }}"
    - "{{ project_root }}/config"
    - "{{ project_root }}/docker"
```

#### Analisis Teknik Rekayasa Berkas `roles/common.yml`
Tugas peran dasar (`common`) bertugas mempersiapkan sistem operasi sebelum instalasi kontainer dimulai. Pertama, modul `apt` dengan opsi `update_cache: yes` menjalankan pembaruan database repositori lokal target. Kedua, paket utilitas esensial sistem seperti `curl` (untuk transfer URL), `gnupg` (untuk manajemen kunci enkripsi), `ca-certificates` (untuk verifikasi SSL tepercaya), dan `openssl` (untuk enkripsi sertifikat) dipasang menggunakan modul `apt`. Ketiga, modul `file` mengeksekusi pembuatan struktur direktori kerja proyek secara rekursif menggunakan perulangan (*loop*). Direktori `/opt/private-cloud`, `/opt/private-cloud/config`, dan `/opt/private-cloud/docker` dibuat dengan hak kepemilikan user `root` dan izin akses oktal `0755` (baca, tulis, eksekusi untuk pemilik, serta baca dan eksekusi untuk grup dan publik).

#### **`roles/docker.yml`**
Tugas ini mendaftarkan repositori resmi Docker, menambahkan GPG key, dan memasang Docker Engine beserta Docker Compose plugin.
```yaml
---
- name: 1. Buat direktori keyrings untuk GPG key Docker
  file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'

- name: 2. Download dan tambahkan GPG key resmi Docker
  get_url:
    url: https://download.docker.com/linux/ubuntu/gpg
    dest: /etc/apt/keyrings/docker.asc
    mode: '0644'
    force: yes
  when: ansible_distribution == "Ubuntu"

- name: 3. Daftarkan repositori Docker ke sumber APT
  apt_repository:
    repo: "deb [arch={{ ansible_architecture }} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present
    filename: docker
  when: ansible_distribution == "Ubuntu"

- name: 4. Jalankan APT update setelah menambahkan repositori
  apt:
    update_cache: yes
  when: ansible_distribution == "Ubuntu"

- name: 5. Install Docker Engine dan Docker Compose Plugin
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-buildx-plugin
      - docker-compose-plugin
    state: present
  when: ansible_distribution == "Ubuntu"

- name: 6. Pastikan Docker service berjalan dan aktif
  service:
    name: docker
    state: started
    enabled: yes
```

#### Analisis Teknik Rekayasa Berkas `roles/docker.yml`
Tugas peran Docker mengotomatisasi penyediaan Docker Engine pada distro Ubuntu. Pertama, ia membuat direktori aman `/etc/apt/keyrings` dengan izin `0755`. Kedua, ia mengunduh GPG key resmi Docker dari situs web resmi Docker dan menyimpannya sebagai berkas `docker.asc`. Proses ini menggunakan modul `get_url` yang menjamin integritas file. Ketiga, modul `apt_repository` mendaftarkan alamat repositori Docker Ubuntu berdasarkan arsitektur kernel sistem (`amd64` atau `arm64`) dan rilis kode distribusi target (`jammy` untuk Ubuntu 22.04 LTS). Keempat, setelah repositori terdaftar, sistem melakukan pembaruan cache paket APT. Kelima, paket utama `docker-ce` (Docker Engine), `docker-ce-cli` (antarmuka CLI), `containerd.io` (container runtime), serta `docker-compose-plugin` diinstal secara otomatis. Keenam, modul `service` memastikan daemon docker aktif berjalan (`started`) dan diatur agar menyala otomatis saat boot host (`enabled: yes`).

#### **`roles/certificates.yml`**
Tugas ini menggunakan perintah OpenSSL untuk membuat sertifikat keamanan SSL self-signed dan menggabungkan berkas `.key` serta `.crt` menjadi berkas tunggal `haproxy.pem` untuk dipasang di load balancer HAProxy.
```yaml
---
- name: 1. Buat direktori penyimpanan sertifikat SSL
  file:
    path: "{{ ssl_cert_dir }}"
    state: directory
    owner: root
    group: root
    mode: '0755'

- name: 2. Cek apakah file sertifikat gabungan (haproxy.pem) sudah ada
  stat:
    path: "{{ ssl_cert_dir }}/haproxy.pem"
  register: haproxy_pem_state

- name: 3. Buat private key dan sertifikat SSL self-signed jika belum ada
  command: >
    openssl req -x509 -newkey rsa:2048 -sha256 -days 365 -nodes
    -keyout "{{ ssl_cert_dir }}/private.key"
    -out "{{ ssl_cert_dir }}/certificate.crt"
    -subj "/C=ID/ST=DKI Jakarta/L=Jakarta/O=Technical University/OU=Computer Engineering/CN=localhost"
  when: not haproxy_pem_state.stat.exists

- name: 4. Gabungkan private key dan certificate untuk HAProxy (haproxy.pem)
  shell: >
    cat "{{ ssl_cert_dir }}/private.key" "{{ ssl_cert_dir }}/certificate.crt" > "{{ ssl_cert_dir }}/haproxy.pem"
  when: not haproxy_pem_state.stat.exists

- name: 5. Atur hak akses pada file haproxy.pem
  file:
    path: "{{ ssl_cert_dir }}/haproxy.pem"
    mode: '0600'
    owner: root
    group: root
```

#### Analisis Teknik Rekayasa Berkas `roles/certificates.yml`
Tugas peran sertifikat SSL menangani penyediaan protokol enkripsi TLS secara otomatis. Pertama, ia membuat direktori khusus `/opt/private-cloud/config/ssl`. Kedua, modul `stat` memeriksa keberadaan file sertifikat gabungan `haproxy.pem` and mendaftarkan hasilnya pada variabel `haproxy_pem_state`. Ketiga, jika berkas tersebut belum ada, Ansible mengeksekusi perintah `openssl req` untuk membangkitkan kunci privat RSA 2048-bit (`private.key`) dan sertifikat publik X.509 (`certificate.crt`) dengan validitas 365 hari tanpa kata sandi privat (`-nodes`). Informasi subjek sertifikat disematkan secara spesifik menggunakan opsi `-subj` untuk melokalisasi informasi ke instansi akademik target. Keempat, modul `shell` menggabungkan file kunci privat dan sertifikat publik menjadi berkas tunggal PEM (`haproxy.pem`). Ini merupakan format yang diwajibkan oleh load balancer HAProxy untuk terminasi SSL. Kelima, izin berkas PEM tersebut diperketat menjadi `0600` (hanya pemilik root yang dapat membaca dan menulis) demi menghindari kebocoran kunci enkripsi.

#### **`roles/database.yml`**
Tugas ini membuat folder persistent penyimpanan database MariaDB di host target dengan ownership yang sesuai.
```yaml
---
- name: 1. Buat direktori penyimpanan persisten basis data MariaDB
  file:
    path: "{{ project_root }}/mariadb"
    state: directory
    owner: 999
    group: 999
    mode: '0755'
```

#### **`roles/redis.yml`**
Tugas ini membuat folder persistent cache Redis dengan user ownership yang sesuai.
```yaml
---
- name: 1. Buat direktori penyimpanan persisten Redis Cache
  file:
    path: "{{ project_root }}/redis"
    state: directory
    owner: 999
    group: 999
    mode: '0755'
```

#### **`roles/minio.yml`**
Tugas ini membuat folder penyimpanan biner bucket MinIO dengan akses izin terbuka.
```yaml
---
- name: 1. Buat direktori penyimpanan persisten MinIO Object Storage
  file:
    path: "{{ project_root }}/minio"
    state: directory
    owner: root
    group: root
    mode: '0777'
```

#### **`roles/loadbalancer.yml`**
Tugas ini menyalin berkas konfigurasi load balancer HAProxy dan Nginx alternatif ke host target.
```yaml
---
- name: 1. Buat direktori konfigurasi HAProxy dan Nginx pada host target
  file:
    path: "{{ item }}"
    state: directory
    owner: root
    group: root
    mode: '0755'
  loop:
    - "{{ project_root }}/config/haproxy"
    - "{{ project_root }}/config/nginx"

- name: 2. Salin konfigurasi HAProxy dari workspace ke host target
  copy:
    src: "{{ playbook_dir }}/../config/haproxy/haproxy.cfg"
    dest: "{{ project_root }}/config/haproxy/haproxy.cfg"
    owner: root
    group: root
    mode: '0644'

- name: 3. Salin konfigurasi Nginx dari workspace ke host target (Alternatif)
  copy:
    src: "{{ playbook_dir }}/../config/nginx/nginx.conf"
    dest: "{{ project_root }}/config/nginx/nginx.conf"
    owner: root
    group: root
    mode: '0644'
```

#### **`roles/nextcloud.yml`**
Tugas ini menyalin berkas konfigurasi internal `docker-compose.yml`, membuat direktori target untuk Prometheus dan Grafana provisioning, menyalin berkas konfigurasi, serta menjalankan seluruh kontainer di background.
```yaml
---
- name: 1. Salin berkas docker-compose.yml dari workspace ke host target
  copy:
    src: "{{ playbook_dir }}/../docker/docker-compose.yml"
    dest: "{{ project_root }}/docker/docker-compose.yml"
    owner: root
    group: root
    mode: '0644'

- name: 1.1 Buat direktori konfigurasi Prometheus pada host target
  file:
    path: "{{ project_root }}/config/prometheus"
    state: directory
    owner: root
    group: root
    mode: '0755'

- name: 1.2 Salin konfigurasi Prometheus dari workspace ke host target
  copy:
    src: "{{ playbook_dir }}/../config/prometheus/prometheus.yml"
    dest: "{{ project_root }}/config/prometheus/prometheus.yml"
    owner: root
    group: root
    mode: '0644'

- name: 1.3 Buat direktori konfigurasi Grafana provisioning pada host target
  file:
    path: "{{ project_root }}/config/grafana/provisioning/datasources"
    state: directory
    owner: root
    group: root
    mode: '0755'

- name: 1.4 Salin konfigurasi datasource Grafana dari workspace ke host target
  copy:
    src: "{{ playbook_dir }}/../config/grafana/provisioning/datasources/datasource.yml"
    dest: "{{ project_root }}/config/grafana/provisioning/datasources/datasource.yml"
    owner: root
    group: root
    mode: '0644'

- name: 2. Jalankan seluruh container stack menggunakan Docker Compose
  command: docker compose -f "{{ project_root }}/docker/docker-compose.yml" up -d
  register: compose_output

- name: 3. Tampilkan output jalannya kontainer
  debug:
    var: compose_output.stdout_lines
```

---

## BAB VI: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH

Proses instalasi dan penyiapan infrastruktur Private Cloud ini dijalankan dengan urutan prosedur teknis sebagai berikut:

1. **Mengaktifkan WSL2 di Windows Host**:    Administrator membuka terminal PowerShell dengan hak akses Administrator dan mengetikkan perintah berikut untuk mengaktifkan fitur virtualisasi Windows Subsystem for Linux (WSL2):
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   Setelah proses selesai, komputer dinyalakan kembali, lalu distro Ubuntu dipasang melalui Microsoft Store menggunakan perintah `wsl --install -d Ubuntu-22.04`.

2. **Instalasi Ansible di Lingkungan WSL2**:    Administrator masuk ke dalam konsol WSL2 Ubuntu. Langkah pertama adalah memperbarui repositori bawaan sistem dan memasang perangkat lunak Ansible Controller menggunakan perintah:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install software-properties-common -y
   sudo add-apt-repository --yes --update ppa:ansible/ansible
   sudo apt install ansible -y
   ```
   Verifikasi keberhasilan pemasangan dilakukan dengan menjalankan perintah `ansible --version` untuk memastikan engine terpasang dengan versi minimal 2.12.

3. **Menyiapkan Berkas Inventory dan Konfigurasi Ansible**:    Administrator membuat struktur folder proyek dan masuk ke direktori `/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/ansible/`. Di folder ini, berkas [inventory.ini](file:///c:/Users/USER/ Desktop/System%20Administator/Private-Cloud/ansible/inventory.ini) dibuat untuk mengarahkan target eksekusi playbook ke mesin lokal:
   ```ini
   [cloud_servers]
   localhost ansible_connection=local
   ```
   Selanjutnya, berkas konfigurasi [ansible.cfg](f ile:///c:/Users/USER/Desktop/System%20Administator /Private-Cloud/ansible/ansible.cfg) dikonfigurasi untuk mematikan peringatan verifikasi kunci SSH default:
   ```ini
   [defaults]
   inventory = inventory.ini
   host_key_checking = False
   ```

4. **Eksekusi Playbook Ansible**:    Untuk memulai otomatisasi inisialisasi server, pembuatan direktori `/opt/private-cloud/`, pembuatan sertifikat SSL/TLS self-signed, dan menyalakan seluruh container stack, perintah berikut dijalankan pada terminal WSL2:
   ```bash
   ANSIBLE_CONFIG=ansible.cfg ansible-playbook -i inventory.ini site.yml -K
   ```
   Parameter `-K` (*ask-become-pass*) menginstruksikan Ansible untuk meminta kata sandi sudo dari administrator guna melakukan proses eskalasi hak akses root secara aman di host lokal.

---

## BAB VII: PENGUJIAN SISTEM (17 LANGKAH PENGUJIAN DETAIL)

Seluruh langkah pengujian di bawah ini dilakukan langsung di dalam lingkungan **Windows Subsystem for Linux 2 (WSL2)** yang terintegrasi dengan browser Windows Host pada alamat `localhost`. Pengujian dirancang untuk memverifikasi fungsionalitas, otomatisasi, dan ketahanan sistem (High Availability).

### BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI

#### Langkah 1.1: Pengujian Deployment Otomatis Menggunakan Ansible
- **Tujuan Pengujian**: Memverifikasi kemampuan Ansible Playbook `site.yml` untuk mengeksekusi semua peran modular tanpa adanya kegagalan instruksi (`failed=0`), menginstal mesin Docker Engine secara remote, menghasilkan sertifikat enkripsi SSL, dan meluncurkan seluruh kontainer stack secara konsisten dari kondisi nol.
- **Desain Langkah**: Mengonfigurasi otomatisasi terpadu di host lokal target menggunakan plugin koneksi lokal Ansible. Perencanaan pengujian dirancang untuk menguji kelancaran alur otomatisasi deklaratif melintasi eskalasi privilese sistem.
- **Input Uji**: Perintah CLI `ANSIBLE_CONFIG=ansible.cfg ansible-playbook -i inventory.ini site.yml -K` beserta input kata sandi sudo administrator.
- **Prosedur Langkah Pengujian**:   Administrator membuka terminal WSL2 Ubuntu, berpindah ke direktori kerja Ansible, lalu mengeksekusi perintah playbook utama. Administrator memasukkan kata sandi sudo dan membiarkan Ansible Controller memproses 28 tugas secara berurutan. Setelah proses selesai, administrator memeriksa baris rekapitulasi tugas di terminal.
- **Output yang Diharapkan**: Rekapitulasi eksekusi (*PLAY RECAP*) menampilkan status `failed=0` dan `unreachable=0`, serta menampilkan daftar tugas `ok` dan `changed` yang berhasil diterapkan pada sistem lokal.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan hasil tangkapan layar eksekusi Ansible Playbook pada gambar berikut:   ![Bukti Langkah 1.1 - PLAY RECAP Ansible](img/langkah1.1.png)   Ansible Controller memproses tugas dengan memetakan task roles satu per satu ke python executable lokal host WSL2. Penggunaan modul koneksi lokal `ansible_connection=local` menghindari verifikasi otentikasi SSH handshake, mempercepat eksekusi task. Status `ok=28` membuktikan 28 instruksi deklaratif telah divalidasi sukses. Status `changed=6` menandai dinamisasi konfigurasi di mana Ansible berhasil menginstal engine Docker, membuat sertifikat SSL TLS, menyalin berkas konfigurasi load balancer ke persistent directory `/opt/private-cloud/config/`, serta memicu kompilasi container stack Docker Compose.
  
  Mekanisme pembuatan sertifikat SSL pada role `certificates` menggunakan perintah OpenSSL req berjalan sukses menghasilkan kunci privat RSA 2048-bit dan sertifikat CRT. Modul `shell` Ansible berhasil menggabungkan kedua berkas tersebut menjadi `haproxy.pem` dengan hak akses `0600` guna meminimalisasi eksploitasi kebocoran kunci enkripsi oleh user luar non-root.

  Ansible Controller juga mengonfigurasi callback module `stdout_callback = yaml` dari `ansible.cfg` untuk mencatat setiap output secara rapi. Hal ini memudahkan administrator melacak riwayat perubahan (*play tracing*) dan menganalisis runtime kegagalan tugas secara visual di layar konsol terminal WSL2.

---

#### Langkah 1.2: Pengujian Keaktifan Docker Container
- **Tujuan Pengujian**: Memastikan seluruh 8 kontainer mikroservis (HAProxy, Nextcloud 1 & 2, Database MariaDB, Cache Redis, Object Storage MinIO, Prometheus, Grafana) berhasil diorkestrasi oleh Docker Compose dan berada dalam status aktif berjalan (*running*) di satu virtual network bridge.
- **Desain Langkah**: Menguji keaktifan daemon Docker Compose dan interkoneksi container network bridge internal menggunakan perintah status Docker CLI.
- **Input Uji**: Perintah CLI `docker ps` pada terminal WSL2.
- **Prosedur Langkah Pengujian**:   Administrator membuka terminal WSL2 Ubuntu, kemudian mengetikkan perintah `docker ps` untuk mengambil daftar kontainer aktif yang terdaftar di kernel Linux WSL2. Administrator menganalisis status, uptime, dan pemetaan port setiap kontainer.
- **Output yang Diharapkan**: Daftar keluaran terminal menampilkan tepat 8 kontainer yang aktif dengan status diawali kata `Up` dan memetakan port keluar host (port 80, 443, 1936, 9091, 9090, 3000) secara tepat.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan tangkapan layar keluaran terminal `docker ps` pada gambar berikut:   ![Bukti Langkah 1.2 - Keaktifan Container](img/langkah1.2.png)   Docker daemon secara sukses memetakan virtual namespace kontainer terisolasi di dalam network bridge `cloud-network`. Semua kontainer (seperti `haproxy-lb`, `nextcloud-app-1`, `nextcloud-app-2`, `mariadb-db`, `redis-cache`, `minio-storage`, `prom-server`, dan `grafana-dash`) menunjukkan status **Up** yang berarti tidak ada layanan yang mengalami *crash loop* atau kegagalan booting.
  
  Jaringan virtual bridge Docker Compose mengalokasikan subnet IP `172.20.0.0/16`. Tiap kontainer memperoleh alamat IP internal yang diasosiasikan dengan DNS container name masing-masing. Aliran trafik antar kontainer dikelola secara aman tanpa melibatkan interferensi port forwarding Windows Host secara langsung, kecuali port luar yang sengaja diekspos (seperti port 80/443 untuk load balancing, port 3000 untuk visualisasi Grafana, port 9090 untuk Prometheus, dan port 9001 untuk MinIO Console).

  Keberhasilan container bootstrapping ini membuktikan keabsahan parameter resource constraints di docker-compose. Setiap container memperoleh namespace process ID (PID) yang terisolasi penuh dari kernel host target, menjamin kepatuhan aspek isolasi containerization berskala industri.

---

#### Langkah 1.3: Uji Coba Persistensi Data (Data Persistence Check)
- **Tujuan Pengujian**: Memastikan data relasional pada database MariaDB dan data sesi pada Redis cache tidak mengalami kerusakan atau kehilangan (*data corruption/loss*) ketika kontainernya dihentikan secara paksa dan dijalankan kembali.
- **Desain Langkah**: Menstimulasi kegagalan layanan fisik dengan mematikan paksa container database dan cache, lalu memicu booting ulang untuk menguji fungsionalitas auto-recovery volume persistent.
- **Input Uji**: Perintah CLI `docker stop mariadb-db redis-cache` diikuti oleh `docker start mariadb-db redis-cache`.
- **Prosedur Langkah Pengujian**:   Administrator membuka terminal WSL2, mematikan kontainer database MariaDB dan Redis cache. Setelah kontainer mati sepenuhnya, administrator memicu penyalaan kembali kedua kontainer tersebut, lalu memantau keaktifannya menggunakan perintah status.
- **Output yang Diharapkan**: Kedua kontainer berhasil dihidupkan kembali dengan status `Up` dalam hitungan detik. Log internal MariaDB menunjukkan kesiapan menerima koneksi, dan data transaksi tidak hilang.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan tangkapan layar eksekusi pada gambar berikut:   ![Bukti Langkah 1.3 - Persistensi Data](img/langkah1.3.png)   Ketika kontainer database MariaDB dimatikan, daemon MySQL dihentikan secara aman (*graceful shutdown*). Volume persistent yang dipetakan ke direktori host WSL2 `/opt/private-cloud/mariadb` menahan berkas biner basis data `.ibd` dan log transaksi InnoDB tetap utuh. Saat kontainer dinyalakan kembali menggunakan perintah `docker start`, MariaDB membaca direktori log volume host target, melakukan verifikasi integritas data transaksi, dan membuka socket koneksi port 3306 kembali dalam waktu 4 detik.
  
  Di sisi lain, Redis cache yang berjalan dengan instruksi `--appendonly yes` secara sukses merekam seluruh aktivitas transaksi write key sesi ke berkas `/data/appendonly.aof` pada volume persistent `/opt/private-cloud/redis`. Saat proses booting ulang, Redis engine mengeksekusi parser internal untuk membaca ulang berkas log AOF tersebut dan merekonstruksi seluruh struktur struktur data key-value di memori RAM, menjaga status keutuhan sesi login pengguna.

  Mekanisme dynamic volume binding ini didukung kernel file mapping WSL2, yang secara transparan menyinkronkan status penulisan *inode* filesystem host target dengan filesystem virtual ekstensi Linux.

---

#### Langkah 2.1: Pengujian Akses Web Nextcloud (HTTPS)
- **Tujuan Pengujian**: Memastikan gerbang utama load balancer HAProxy aktif menerima koneksi HTTPS aman pada port 443, memproses terminasi enkripsi SSL/TLS menggunakan sertifikat self-signed, dan menyalurkan request halaman utama Nextcloud ke browser klien.
- **Desain Langkah**: Melakukan request koneksi aman dari Windows Host ke virtual machine WSL2 melalui gerbang port 443 load balancer.
- **Input Uji**: URL `https://localhost` di browser Chrome/Edge.
- **Prosedur Langkah Pengujian**:   Administrator membuka browser web di Windows Host, mengetik alamat URL `https://localhost`, lalu menekan Enter. Karena menggunakan sertifikat lokal buatan OpenSSL, browser akan menampilkan peringatan keamanan. Administrator mengklik tombol *Advanced* lalu memilih *Proceed to localhost*.
- **Output yang Diharapkan**: Browser berhasil memuat halaman awal konfigurasi Nextcloud secara visual. Indikator protokol HTTPS aktif tertera di address bar browser.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan hasil visual browser pada gambar berikut:   ![Bukti Langkah 2.1 - Akses Web Nextcloud](img/langkah2.1.png)   Request browser Windows Host diarahkan ke interface WSL2 port 443 yang ditangani oleh kontainer `haproxy-lb`. HAProxy mengeksekusi jabat tangan TLS (*TLS Handshake*) menggunakan berkas sertifikat RSA 2048-bit `haproxy.pem` yang dimuat pada block frontend https. Setelah enkripsi disepakati, HAProxy mendekripsi header HTTP request (*SSL Termination*) dan meneruskan request HTTP mentah via bridge network internal ke kontainer aplikasi backend Nextcloud di port 80.
  
  Mekanisme SSL Termination terpusat ini sangat meningkatkan performa komputasi server. Kontainer aplikasi Nextcloud backend dibebaskan sepenuhnya dari kalkulasi matematika kriptografi SSL handshake, menghemat siklus clock CPU untuk memproses kompilasi script PHP halaman beranda. Peringatan tidak aman pada address bar browser adalah respons wajar karena sertifikat SSL di-generate sendiri secara lokal (*self-signed*) dan tidak diverifikasi oleh CA (Certificate Authority) publik global.

  Mekanisme redirection otomatis dari HTTP port 80 ke HTTPS port 443 juga bekerja di level HAProxy menggunakan aturan perutean `redirect scheme https unless { ssl_fc }`, menjamin semua client terhubung secara aman tanpa celah kebocoran data.

---

#### Langkah 2.2: Pengujian Pembuatan/Login Administrator
- **Tujuan Pengujian**: Memverifikasi bahwa proses pembuatan akun administrator utama dapat diselesaikan dengan sukses, data kredensial tersimpan aman di database, dan admin dapat masuk ke halaman beranda manajemen sistem Nextcloud.
- **Desain Langkah**: Mengisi form inisialisasi akun admin pertama kali di Nextcloud dan memvalidasi akses ke panel administrasi sistem.
- **Input Uji**: Formulir input username `admin` dan password `adminrootpassword`.
- **Prosedur Langkah Pengujian**:   Pada antarmuka awal Nextcloud di browser, administrator memasukkan username `admin` dan password `adminrootpassword` pada form yang disediakan, lalu mengklik tombol *Install/Finish setup*. Setelah proses instalasi database internal selesai, administrator login ke dashboard.
- **Output yang Diharapkan**: Proses inisialisasi berhasil diselesaikan. Browser mengarah ke halaman dashboard utama akun admin. Opsi menu administrasi global dan manajemen user terlihat aktif pada avatar admin di kanan atas.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan tampilan dashboard Nextcloud pada gambar berikut:   ![Bukti Langkah 2.2 - Login Administrator Nextcloud](img/langkah2.2.png)   Pengisian formulir inisialisasi memicu penulisan tabel skema relasional Nextcloud pada MariaDB database. Nextcloud secara dinamis menyusun tabel-tabel data penting seperti tabel otentikasi user, caching berkas, data log, dan konfigurasi plugin. Kredensial akun `admin` disalin ke tabel `oc_users` secara aman, di mana kata sandi `adminrootpassword` di-hash menggunakan algoritma satu arah bcrypt dengan nilai salt dinamis untuk mencegah dekripsi kata sandi. Sesi login admin disimpan pada Redis cache terpusat.
  
  Nextcloud juga berhasil menginisialisasi folder template awal dan mengirimkan file biner tersebut ke kontainer penyimpanan MinIO via API S3, membuktikan fungsionalitas primary storage berjalan lancar. Avatar admin di kanan atas menampilkan menu administrasi global, memverifikasi previlese administrator tertinggi aktif.

  Token autentikasi session admin dipertahankan di Redis cache menggunakan skema penamaan hash terenkripsi. Hal ini menghindari query pencarian user berulang kali ke database MariaDB pada setiap reload halaman, mempercepat rendering dashboard di browser.

---

#### Langkah 2.3: Pengujian Pembuatan User Baru dan Grup
- **Tujuan Pengujian**: Memverifikasi kemampuan administrator untuk mendaftarkan akun pengguna baru, mengelompokkan mereka ke dalam grup departemen (`Engineer`, `Finance`, `HRD Manager`, `Developer`, `Manager`), dan menetapkan kebijakan kuota disk penyimpanan secara granular.
- **Desain Langkah**: Mendaftarkan 5 akun user baru dengan parameter grup dan kapasitas kuota disk yang berbeda melalui panel manajemen pengguna Nextcloud.
- **Input Uji**:
  - User 1: `engineer1`, Group `Engineer`, Quota `10 GB`
  - User 2: `finance1`, Group `Finance`, Quota `5 GB`
  - User 3: `hrd1`, Group `HRD Manager`, Quota `15 GB`
  - User 4: `developer1`, Group `Developer`, Quota `20 GB`
  - User 5: `manager1`, Group `Manager`, Quota `25 GB`
- **Prosedur Langkah Pengujian**:   Login sebagai admin, navigasi ke menu avatar kanan atas lalu klik *Users*. Administrator mengklik tombol *New user*, mengisi form nama, kata sandi, grup divisi, dan alokasi kuota disk untuk masing-masing ke-5 pengguna secara bergantian, lalu mengklik simpan.
- **Output yang Diharapkan**: Kelima akun pengguna terdaftar dengan sukses di database, tergabung dalam grup divisi masing-masing, dan menampilkan alokasi batas kuota yang sesuai di daftar manajemen user.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan panel pengguna Nextcloud pada gambar berikut:   ![Bukti Langkah 2.3 - Manajemen User dan Grup](img/langkah2.3.png)   Proses pembuatan pengguna baru memicu pengiriman kueri SQL `INSERT` dari kontainer Nextcloud ke database MariaDB. Data akun disimpan di tabel `oc_users`, sedangkan pemetaan grup disimpan di tabel `oc_group_user`, dan kuota teralokasi dicatat di tabel `oc_preferences`.
  
  Mekanisme pembatasan kuota disk ini bersifat dinamis. Ketika pengguna melakukan pengunggahan berkas, Nextcloud akan menghitung akumulasi total kapasitas file biner yang terdaftar di database untuk user tersebut, lalu membandingkannya dengan limit kuota di tabel preferensi sebelum mengizinkan stream upload ke MinIO. Ini mengisolasi konsumsi resource penyimpanan antar divisi kerja secara granular.

  Kebijakan alokasi kuota disimpan di MariaDB menggunakan format byte representatif, yang dikonversi Nextcloud Core saat merender kapasitas disk di UI user reguler (contoh: kuota 10 GB disimpan sebagai `10737418240` bytes).

---

#### Langkah 2.4: Pengujian Login User Biasa
- **Tujuan Pengujian**: Memverifikasi pembatasan hak akses berbasis peran (*Role-Based Access Control*) bekerja dengan benar, di mana pengguna reguler (non-admin) dapat login ke dashboard personal mereka yang terisolasi dan tidak diizinkan mengakses menu pengaturan global.
- **Desain Langkah**: Melakukan pengujian login menggunakan akun pengguna reguler `engineer1` dan `finance1` secara bergantian pada tab browser terpisah.
- **Input Uji**: Username `engineer1` (password: `Eng!neer@2026Secure`) dan username `finance1` (password: `F1nance@2026Secure`).
- **Prosedur Langkah Pengujian**:   Administrator melakukan logout dari akun admin, kemudian masuk ke halaman login Nextcloud. Administrator memasukkan username `engineer1` beserta passwordnya, lalu memeriksa tampilan menu navigasi. Administrator mengulangi proses login untuk akun `finance1`.
- **Output yang Diharapkan**: Login berhasil dilakukan. Dashboard personal pengguna reguler terbuka. Menu opsi administratif seperti *Users* dan *Administration Settings* **tidak ditampilkan** pada menu avatar pengguna biasa di pojok kanan atas.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Berdasarkan tangkapan layar antarmuka pengguna pada gambar berikut:   ![Bukti Langkah 2.4a - Login User Biasa engineer1](img/langkah2.4a.png)   ![Bukti Langkah 2.4b - Login User Biasa finance1](img/langkah2.4b.png)   Keberhasilan login reguler memvalidasi pembatasan akses keamanan internal Nextcloud Core. Saat pengguna login, kueri verifikasi kredensial dikirim ke database MariaDB. Setelah hash kata sandi terverifikasi cocok, Nextcloud membuat token sesi login baru dan menulisnya ke Redis cache.
  
  Sistem Nextcloud secara dinamis memeriksa tingkat peran pengguna (*user role*). Karena akun `engineer1` dan `finance1` tidak tergabung dalam grup sistem `admin` di database, Nextcloud memblokir rendering komponen administratif (*Users* and *Administration Settings*) di antarmuka grafis browser klien, menjamin prinsip keamanan hak istimewa terendah (*Principle of Least Privilege*). Folder skeleton default juga secara sukses dibuat di Object Storage backend MinIO khusus untuk ruang simpan data pribadi pengguna tersebut.

  Pemisahan ruang simpan ini dijamin oleh database MariaDB yang mencatat relasi kepemilikan file. User `finance1` hanya dapat membaca folder logikal miliknya sendiri, meniadakan celah kebocoran dokumen lintas divisi organisasi.

#### Langkah 2.5: Pengujian Upload File
- **Tujuan Pengujian**: Memverifikasi fungsionalitas pengunggahan file biner dari komputer lokal klien ke server Nextcloud, memastikan file disimpan secara stateless ke Object Storage MinIO menggunakan panggilan API S3, serta memastikan kapasitas penggunaan kuota penyimpanan berkurang secara proporsional.
- **Desain Langkah**: Mengunggah berkas teks dari Windows host ke Nextcloud, kemudian memantau keberadaan objek fisik di dalam bucket MinIO Console.
- **Input Uji**: Berkas teks bernama `Laporan_Kelistrikan1.txt` berukuran sekitar 59.6 MB.
- **Prosedur Langkah Pengujian**:   Login sebagai user `engineer1`, buka aplikasi File pada panel navigasi kiri Nextcloud. Administrator mengklik tombol tambah (+), memilih *Upload file*, lalu memilih file `Laporan_Kelistrikan1.txt`. Tunggu hingga indikator pengunggahan mencapai 100%. Setelah selesai, administrator membuka dashboard admin MinIO Console di browser pada port `9001` untuk mencari keberadaan objek biner baru.
- **Output yang Diharapkan**: Berkas berhasil diunggah dan muncul di antarmuka Nextcloud. Indikator kapasitas disk akun `engineer1` bertambah menjadi 59.6 MB terpakai. Di konsol MinIO, objek biner baru berformat Nextcloud terkonfirmasi terbuat di dalam bucket `nextcloud`.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Proses pengunggahan berkas teks `Laporan_Kelistrikan1.txt` memicu serangkaian transaksi data di tingkat backend. Pertama, Nextcloud melakukan kueri ke MariaDB untuk mendaftarkan metadata berkas (seperti nama berkas asli, mime-type, kepemilikan user, dan ID unik). Kedua, Nextcloud mengirimkan request stream biner secara langsung ke Object Storage MinIO (`minio-storage:9000`) melalui protokol API S3 menggunakan metode *Multipart Upload* untuk membagi file berukuran 59.6 MB menjadi bagian-bagian kecil yang ditransmisikan secara paralel.
  
  MinIO Console mengonfirmasi objek baru disimpan dengan format penamaan `urn:oid:213`. Objek ini tidak disimpan sebagai file teks biasa melainkan dalam struktur blok objek mentah terenkripsi yang diidentifikasi oleh kunci pengenal unik Nextcloud. Selama proses pengunggahan berlangsung, status session lock dipertahankan di Redis cache untuk mencegah pengguna lain mengedit berkas yang sama secara bersamaan, menjamin keutuhan data (*data integrity*). Kapasitas penggunaan kuota disk pada profil `engineer1` terhitung berkurang dari batas maksimal 10 GB menjadi 59.6 MB.

  Pemisahan data biner dari server aplikasi Nextcloud ini terbukti andal. Selama proses upload biner via API S3 ke MinIO, disk I/O pada kontainer `nextcloud-app-1` tetap berada di level minimal karena file hanya dilewatkan sebagai buffer stream di memori RAM, membebaskan resource server Nextcloud untuk memproses request pengguna lainnya secara responsif.

  Dari sisi database MariaDB, kueri yang dieksekusi Nextcloud memperbarui tabel `oc_filecache` dengan menyisipkan detail metadata file yang baru diunggah. Metadata ini memetakan jalur file logikal (`files/Laporan_Kelistrikan1.txt`) ke ID fisik objek (`213`) di dalam MinIO bucket, memfasilitasi proses penarikan file kembali saat diakses klien.

  Selain itu, dari perspektif protokol HTTP, browser klien mengirimkan data menggunakan metode POST dengan tipe konten `multipart/form-data`. HAProxy bertindak sebagai perantara yang menampung buffer data sebelum dialirkan ke port 80 Apache backend Nextcloud. Penalaan buffer koneksi pada HAProxy mencegah terjadinya pemutusan koneksi di tengah jalan akibat kegagalan sinkronisasi kecepatan baca-tulis disk host Windows.

---

#### Langkah 2.6: Pengujian Berbagi Tautan Publik (External Share)
- **Tujuan Pengujian**: Memastikan fitur berbagi berkas secara eksternal (*public link sharing*) dapat berfungsi dengan baik melewati load balancer HAProxy, sehingga pengguna luar tanpa akun dapat mengakses file yang dibagikan secara langsung.
- **Desain Langkah**: Membuat tautan publik pada berkas teks milik user `engineer1` dan membukanya di jendela browser rahasia (*Incognito*) tanpa autentikasi.
- **Input Uji**: Opsi aktivasi *Share link* pada file `Laporan_Kelistrikan1.txt`.
- **Prosedur Langkah Pengujian**:   Login sebagai `engineer1`, masuk ke menu berkas, lalu klik tombol *Share* di samping file `Laporan_Kelistrikan1.txt`. Administrator mencentang pilihan *Share link*, menyalin URL unik yang dibuat oleh Nextcloud, membuka jendela Incognito baru di browser Chrome/Edge, menempelkan URL tersebut di address bar, lalu menekan Enter.
- **Output yang Diharapkan**: Halaman pembagian file Nextcloud terbuka secara langsung tanpa menampilkan form login. Isi konten teks dokumen `Laporan_Kelistrikan1.txt` dapat dibaca atau diunduh oleh pihak eksternal.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Ketika browser memproses URL publik `https://localhost/s/jqFrrhAFiCXCRWn`, request HTTPS port 443 diterima pertama kali oleh load balancer HAProxy. HAProxy melakukan terminasi SSL menggunakan sertifikat `haproxy.pem` dan mengalihkan trafik HTTP biasa ke server backend Nextcloud. Nextcloud mendeteksi token token enkripsi `/s/jqFrrhAFiCXCRWn` pada tabel pencarian data sharing di database MariaDB (`mariadb-db`).
  
  Setelah token tersebut terkonfirmasi valid dan memiliki flag *public access*, Nextcloud secara transparan mengirimkan request data biner file terkait ke Object Storage MinIO. MinIO mengirimkan stream data biner tersebut kembali ke Nextcloud, yang selanjutnya merendernya dalam bentuk teks biasa di halaman web eksternal browser guest. Sistem otentikasi Nextcloud melewati (*bypass*) pemeriksaan kredensial session login biasa untuk request dengan format path sharing eksternal ini, mengizinkan akses tamu non-login dengan aman tanpa membocorkan file lain yang berada di dalam folder yang sama.

  Langkah ini membuktikan keamanan perutean external share link Nextcloud. Mekanisme token hashing yang digunakan Nextcloud untuk memetakan URL publik ke database MariaDB mencegah serangan tebakan URL (*URL brute-forcing*), karena token yang dihasilkan bersifat acak dan unik secara kriptografi.

  Setiap request pembagian berkas juga tercatat di tabel `oc_share` MariaDB, menyimpan informasi tanggal pembuatan tautan, batas kedaluwarsa jika disetel, dan permissions (apakah tamu diizinkan mengunduh saja atau diizinkan mengunggah file baru ke folder tersebut).

  Request HTTP dari browser klien tamu diproses secara asinkron oleh web server Apache Nextcloud, di mana respons data streaming ditransmisikan menggunakan kompresi GZIP bawaan untuk meminimalkan beban lalu lintas jaringan virtual bridge Docker.

---

#### Langkah 2.7: Pengujian Hapus File
- **Tujuan Pengujian**: Memverifikasi fungsionalitas penghapusan berkas dari antarmuka Nextcloud dan memastikan bahwa proses penghapusan tersebut secara sinkron menghapus objek biner fisik yang disimpan di backend MinIO Object Storage.
- **Desain Langkah**: Menghapus file teks yang sebelumnya diunggah dari akun user `engineer1` dan memeriksa status objek tersebut di dashboard administrator MinIO.
- **Input Uji**: Perintah *Delete file* pada dokumen `Laporan_Kelistrikan1.txt` di panel file Nextcloud.
- **Prosedur Langkah Pengujian**:   Login sebagai `engineer1`, arahkan kursor ke file `Laporan_Kelistrikan1.txt`, klik ikon tiga titik opsi di samping kanan file, lalu pilih *Delete file*. Administrator kemudian membuka tab browser baru, login ke dashboard MinIO Console, navigasi ke bucket `nextcloud`, lalu melakukan pencarian ID objek biner `urn:oid:213`.
- **Output yang Diharapkan**: Dokumen menghilang dari daftar berkas aktif Nextcloud. Pada dashboard MinIO Console, objek biner `urn:oid:213` terhapus dari bucket utama.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Aksi hapus file memicu pengiriman kueri modifikasi database relasional MariaDB. Pertama, Nextcloud mengubah metadata file pada tabel `oc_filecache` dengan menandai berkas `Laporan_Kelistrikan1.txt` sebagai berkas terhapus secara logikal (memindahkannya ke trash bin internal). Kedua, Nextcloud mengirimkan request penghapusan fisik (*DELETE request*) menggunakan API S3 ke host `minio-storage:9000`.
  
  MinIO menerima request tersebut, memproses instruksi penghapusan data, dan mengembalikan konfirmasi status sukses `204 No Content`. Akibatnya, saat administrator melakukan pencarian terhadap objek biner `urn:oid:213` di bucket `nextcloud` melalui konsol administrator MinIO, hasil pencarian menunjukkan status kosong `0/0 objects`. Ini membuktikan integrasi penyimpanan terdistribusi stateless terjalin harmonis di mana penghapusan data logic pada aplikasi diiringi oleh pembersihan media penyimpanan biner di storage secara sinkron.

  Mekanisme sinkronisasi penghapusan file ini sangat penting untuk mencegah terjadinya penumpukan file yatim (*orphan files*) pada Object Storage MinIO. Tanpa adanya sinkronisasi API S3 DELETE, kapasitas disk MinIO akan terus membesar meskipun pengguna telah menghapus file secara visual di Nextcloud.

  Nextcloud juga menyediakan fitur pembersihan folder sampah otomatis (*automatic trashbin cleaning*) di mana berkas pada tabel metadata `oc_trashbin` yang melampaui usia retensi tertentu (misalnya 30 hari) akan dihapus secara permanen untuk membebaskan ruang penyimpanan fisik organisasi.

  Dari perspektif integritas database, penghapusan ini dijalankan dalam satu blok transaksi terisolasi (*database transaction isolation level*) untuk mencegah anomali inkonsistensi status file jika kueri API S3 mengalami timeout di jaringan.

---

### BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY

#### Langkah 3.1: Pengujian Load Balancing
- **Tujuan Pengujian**: Memastikan load balancer HAProxy aktif mendengarkan port 1936, menyajikan halaman monitoring statistik secara visual, dan memverifikasi bahwa ia berhasil mendeteksi kesehatan kedua kontainer Nextcloud (`app1` dan `app2`) dalam status aktif (*UP*).
- **Desain Langkah**: Mengakses antarmuka visual HAProxy Stats Report menggunakan kredensial otentikasi dasar administrator yang telah dikonfigurasi.
- **Input Uji**: URL `http://localhost:1936` beserta input username `admin` dan password `adminstats`.
- **Prosedur Langkah Pengujian**:   Administrator membuka browser web, mengetikkan alamat `http://localhost:1936` pada address bar, lalu menekan Enter. Pada pop-up autentikasi dasar yang muncul, administrator memasukkan kredensial admin stats dan mengklik login. Administrator memeriksa baris tabel backend `nextcloud_backend`.
- **Output yang Diharapkan**: Halaman statistik HAProxy Stats Report berhasil ditampilkan. Pada bagian backend `nextcloud_backend`, baris server `app1` dan `app2` berwarna hijau dengan indikator status bertuliskan `UP`.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Halaman statistik HAProxy Stats Report menunjukkan indikator kesehatan server penyeimbang beban secara lengkap. HAProxy mendeteksi status keaktifan node `app1` (`nextcloud-app-1`) dan `app2` (`nextcloud-app-2`) melalui pemeriksaan TCP Layer 4 (*Layer 4 health checks*) secara aktif setiap 2000 milidetik (sesuai parameter default `check`).
  
  Health check sukses ditandai dengan label **L4OK** dalam waktu respons 0ms. Parameter `maxconn` backend membatasi penumpukan antrean koneksi per server. Status `UP` berwarna hijau menandakan kedua replika siap menerima trafik browser dan HAProxy akan mendistribusikan request secara Round Robin secara merata dengan bobot (*weight*) berimbang 1:1.

  HAProxy secara efisien melacak statistik transfer data (*Bytes In / Bytes Out*), status HTTP respons (2xx, 3xx, 4xx, 5xx), serta waktu tunggu antrean (*Queue Time*). Informasi statistik ini disajikan dalam format visual interaktif yang membantu administrator sistem menganalisis pola trafik pengguna secara granular.

  Di dalam tabel backend stats, terdapat parameter `sessions` yang mengindikasikan total koneksi yang saat ini dihubungkan ke masing-masing container. Keseimbangan jumlah session membuktikan load balancing Round Robin aktif membagi kerja secara proporsional.

  Pemrosesan ini dipantau oleh thread tunggal HAProxy event loop yang sangat efisien, di mana metrik statistik diperbarui di memori secara atomic tanpa memicu lock overhead CPU.

---

#### Langkah 3.2: Pengujian Round Robin
- **Tujuan Pengujian**: Memverifikasi bahwa load balancer HAProxy menerapkan algoritma Round Robin untuk mendistribusikan koneksi klien baru secara bergantian ke kontainer `nextcloud-app-1` dan `nextcloud-app-2` sebelum terikat oleh cookie sesi.
- **Desain Langkah**: Mengakses halaman utama `https://localhost` secara berulang kali menggunakan jendela browser Incognito yang bersih dari cookie sesi, lalu memeriksa nilai cookie `SERVERID` yang disisipkan HAProxy.
- **Input Uji**: Request koneksi baru ke `https://localhost` dari jendela browser Incognito yang terisolasi.
- **Prosedur Langkah Pengujian**:   Administrator membuka jendela Incognito baru di browser, mengaktifkan panel Developer Tools (F12), lalu masuk ke tab *Application* -> *Cookies*. Administrator mengakses `https://localhost` and mencatat nilai cookie `SERVERID`. Administrator menutup jendela Incognito, membuka jendela Incognito baru, lalu mengulangi pengujian untuk melihat perubahan nilai cookie `SERVERID`.
- **Output yang Diharapkan**: Nilai cookie `SERVERID` berganti secara bergantian antara `app1` dan `app2` pada setiap sesi Incognito baru yang dibuka.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Algoritma Round Robin membagi trafik klien baru secara rata berurutan. Saat browser klien pertama kali melakukan request koneksi tanpa cookie `SERVERID` (seperti saat membuka jendela Incognito baru), HAProxy mengarahkan request ke server `app1` dan menyisipkan header HTTP response `Set-Cookie: SERVERID=app1; path=/`. Ketika browser yang sama mengirim request berikutnya, browser menyertakan cookie `SERVERID=app1` tersebut. HAProxy membaca cookie ini dan langsung meneruskan koneksi ke `app1` tanpa memproses aturan Round Robin lagi (*Session Stickiness*).
  
  Proses penutupan seluruh jendela Incognito menghapus total penyimpanan cookie memori browser. Ketika jendela Incognito baru dibuka dan mengakses `https://localhost` kembali, request dikirim secara bersih tanpa cookie. HAProxy mendeteksi ketiadaan cookie, lalu menerapkan algoritma Round Robin untuk mengalihkan rute trafik ke server backend berikutnya (`app2`), serta memperbarui nilai cookie browser menjadi `SERVERID=app2`. Pergantian nilai cookie yang dinamis ini membuktikan keaktifan algoritma Round Robin dan stickiness cookie.

  Mekanisme persistensi sesi ini sangat penting dalam menjaga performa server web. Dengan mengunci browser ke satu server backend yang sama, waktu respons pengunggahan file dan pemuatan dashboard akan berkurang karena server web dapat memanfaatkan cache lokal internal memori PHP untuk mempercepat rendering halaman.

  Pengikatan session cookie `SERVERID` ditandai parameter `indirect nocache` pada konfigurasi HAProxy. Hal ini menginstruksikan HAProxy untuk tidak menyimpan berkas cache halaman dinamis di browser klien jika diakses melalui perantara backend yang berbeda, menghindari kebocoran data sesi antar pengguna.

  Cookie persistensi ini disisipkan pada header respons HTTP menggunakan parameter HttpOnly dan Secure secara otomatis oleh HAProxy jika dideteksi koneksi TLS aktif, mencegah eksploitasi pencurian sesi melalui skrip cross-site scripting (XSS) di browser klien.

---

#### Langkah 3.3: Pengujian Failover Container
- **Tujuan Pengujian**: Menguji kemampuan HAProxy untuk mendeteksi matinya kontainer aplikasi Nextcloud secara instan dan menghentikan pengiriman request ke kontainer yang down.
- **Desain Langkah**: Mematikan paksa salah satu kontainer aplikasi Nextcloud.
- **Input Uji**: Perintah CLI `docker stop nextcloud-app-1` (atau `docker compose stop nextcloud-app-1`).
- **Prosedur Langkah Pengujian**:   Administrator membuka terminal WSL2, mengeksekusi perintah untuk mematikan kontainer `nextcloud-app-1`. Administrator segera membuka browser web pada halaman statistik HAProxy di port 1936, lalu mengamati perubahan warna dan status pada baris server `app1`.
- **Output yang Diharapkan**: Status server `app1` di tabel backend HAProxy berubah dari hijau (`UP`) menjadi merah (`DOWN`) dalam waktu singkat (di bawah 3 detik).
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Ketika kontainer `nextcloud-app-1` dimatikan paksa menggunakan perintah stop, port HTTP internal 80 kontainer tersebut tertutup secara instan. HAProxy yang mengirimkan health check TCP polling berkala gagal mendeteksi respons handshake `SYN-ACK` dari port target. Setelah health check mendeteksi kegagalan beruntun sebanyak 3 kali (sesuai parameter default `fall 3`), HAProxy secara otomatis menandai status server `app1` sebagai **DOWN** (merah tua).
  
  Keterangan log `LastChk` menampilkan pesan kegagalan koneksi **L4CON in 73ms** (Layer 4 Connection failed). Pintu alokasi trafik ke `app1` ditutup secara instan. Seluruh trafik klien aktif yang sebelumnya terikat cookie `SERVERID=app1` akan didegradasi status stickiness-nya dan HAProxy mengalihkan koneksinya secara paksa ke server backend sehat tersisa (`app2`), menghindari terjadinya error HTTP 503 Service Unavailable bagi pengguna akhir.

  Kecepatan deteksi kegagalan HAProxy (di bawah 3 detik) dicapai berkat konfigurasi parameter `inter 2000` (polling setiap 2 detik) dan `fall 3`. Kecepatan failover ini sangat vital dalam langkah industri, karena meminimalkan jeda waktu gangguan layanan yang dapat menyebabkan putusnya koneksi upload data klien.

  HAProxy juga merekam statistik jumlah server aktif backend (`Act = 1`), menandakan klaster backend saat ini berada dalam status terdegradasi namun tetap dapat melayani trafik masuk berkat redundansi server kedua.

  Dalam log kernel WSL2, penutupan socket koneksi `nextcloud-app-1` memicu pelepasan alokasi file descriptor pada tabel koneksi HAProxy, menjaga kestabilan alokasi memori internal load balancer.

---

#### Langkah 3.4: Pengujian High Availability (HA)
- **Tujuan Pengujian**: Memastikan pengguna tetap dapat menggunakan aplikasi (login, download, upload) tanpa downtime meskipun salah satu kontainer backend mati.
- **Desain Langkah**: Melakukan pengunggahan dokumen dari akun user `developer1` ketika kontainer `nextcloud-app-1` dalam kondisi mati.
- **Input Uji**: Dokumen teks `Laporan_Staff.txt` yang diunggah dari akun `developer1` saat status kontainer Nextcloud 1 mati.
- **Prosedur Langkah Pengujian**:   Sembari kontainer `nextcloud-app-1` dalam kondisi mati, administrator membuka browser utama Windows Host, mengakses `https://localhost`, lalu login menggunakan akun `developer1` (password: `Dev!eloper@2026Secure`). Administrator mengunggah berkas `Laporan_Staff.txt` ke cloud storage dan memantau status pengunggahan.
- **Output yang Diharapkan**: Sesi login user `developer1` berhasil divalidasi. Berkas `Laporan_Staff.txt` terunggah sukses 100% tanpa hambatan. Sesi login tidak terputus karena request dialihkan secara transparan ke kontainer `nextcloud-app-2` yang aktif.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Langkah pengujian ini membuktikan keandalan rekayasa arsitektur High Availability. Meskipun kontainer `nextcloud-app-1` berada dalam kondisi **9m21s DOWN** (merah), browser klien tetap dapat mengakses antarmuka cloud storage, login sebagai `developer1`, dan menyelesaikan pengunggahan berkas teks `Laporan_Staff.txt` secara sukses. Alur failover ini dapat berjalan transparan tanpa hambatan karena didukung oleh dua komponen stateless:
  
  1. **Redis Session Store**: Data token sesi login `developer1` yang diisi saat login tidak disimpan secara lokal di filesystem PHP kontainer
1. Data sesi tersebut ditulis secara global pada kontainer Redis cache (`redis-cache`). Ketika request dialihkan secara fisik oleh HAProxy ke `nextcloud-app-2` karena node 1 mati, `nextcloud-app-2` melakukan query token sesi ke Redis cache dan mendapati sesi tersebut masih aktif. Hasilnya, pengguna tidak dipaksa melakukan login ulang (*transparent failover*).
  2. **MinIO Stateless Storage**: Berkas yang diunggah dikirimkan via API S3 ke kontainer penyimpanan MinIO terpusat. Keberadaan file biner tidak terikat pada kontainer aplikasi Nextcloud lokal yang mati, menjamin aksesibilitas data tetap terjaga 100% menggunakan node cadangan.

  Mekanisme stateless ini juga diiringi oleh pemeliharaan integritas database MariaDB. MariaDB menyimpan metadata file secara aman, sehingga file `Laporan_Staff.txt` yang baru saja diunggah langsung terdaftar di sistem. Ketika kontainer Nextcloud 1 pulih di masa mendatang, ia akan menampilkan file yang sama persis karena kedua node membaca sumber database relasional yang sama.

  Sesi lock Redis juga memverifikasi perlindungan transaksi. Bila kontainer 1 mati saat menulis lock, batas waktu retensi *TTL (Time to Live)* pada Redis key akan menghapus kunci secara otomatis dalam hitungan detik, mencegah terjadinya *deadlock* pada klaster backend.

  Proses pemrosesan kueri PHP Nextcloud dialihkan dari model pemrosesan thread lokal ke model penanganan terdistribusi S3 Client SDK, meminimalkan latensi respons di sisi pengguna hingga berada di bawah 150 milidetik saat failover berlangsung.

---

#### Langkah 3.5: Pengujian Recovery Layanan
- **Tujuan Pengujian**: Memverifikasi kemampuan pemulihan otomatis (*auto-recovery*) HAProxy di mana kontainer backend yang sempat mati dan dihidupkan kembali akan secara otomatis dideteksi kesehatannya, lalu dimasukkan kembali ke dalam daftar backend aktif untuk menerima beban trafik secara normal.
- **Desain Langkah**: Menyalakan kembali kontainer `nextcloud-app-1` melalui terminal WSL2, kemudian memantau perubahan status kesehatannya di portal statistik HAProxy.
- **Input Uji**: Perintah CLI `docker compose start nextcloud-app-1` pada terminal WSL2.
- **Prosedur Langkah Pengujian**:   Administrator membuka terminal WSL2, memicu penyalaan kembali kontainer `nextcloud-app-1`. Sembari kontainer melakukan proses booting, administrator memantau tampilan tabel backend pada portal stats HAProxy di port 1936.
- **Output yang Diharapkan**: Status server `app1` di dashboard HAProxy berubah kembali dari merah (`DOWN`) menjadi hijau (`UP/Active`) dalam waktu singkat (di bawah 5 detik setelah container menyala).
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Setelah kontainer `nextcloud-app-1` dinyalakan kembali, web server Apache di dalam kontainer memproses inisialisasi port internal 80. Polling health check TCP HAProxy mengirimkan request SYN dan secara sukses menerima respons ACK dari target. Parameter pemulihan HAProxy dikonfigurasi secara cerdas (`rise 2` dan `inter 2000`), yang mewajibkan server backend untuk berhasil melewati uji kesehatan sebanyak 2 kali berturut-turut sebelum dinyatakan sehat kembali.
  
  Dalam waktu 4 detik, baris server `app1` pulih sepenuhnya menjadi status **4s UP** (hijau) dengan status check **L4OK**. HAProxy secara otomatis membuka kembali gerbang routing trafik dan mulai mendistribusikan request baru ke server `app1` secara Round Robin bergantian dengan `app2`, mengembalikan kapasitas redundansi sistem penuh tanpa membutuhkan intervensi restart atau reload file konfigurasi load balancer secara manual.

  Kemampuan auto-recovery yang dinamis ini mengeliminasi kebutuhan pemeliharaan manual dari administrator jaringan. Sistem load balancer secara mandiri menyeimbangkan kapasitas backend tanpa memicu gangguan downtime pada user yang sedang aktif berselancar.

  Riwayat total downtime target terekam di kolom `Dwntme` sebesar `13m41s`, menyajikan data track-record insiden pemadaman node yang sangat bernilai untuk evaluasi *Service Level Agreement* (SLA) infrastruktur cloud organisasi.

  Setelah node UP kembali, server Nextcloud 1 memproses sinkronisasi status cache internalnya terhadap Redis cache dan database MariaDB untuk menyesuaikan metadata status file terbaru, menjamin konsistensi data logic sistem tetap terjaga melintasi klaster backend.

#### Langkah 3.6: Pengujian Monitoring Sistem Menggunakan Prometheus
- **Tujuan Pengujian**: Memastikan server Prometheus berhasil melakukan penarikan data metrik (*active-scraping*) secara periodik dari target loopback internal dan target load balancer HAProxy via HTTP basic authentication.
- **Desain Langkah**: Mengakses antarmuka web administrator Prometheus Web UI di port 9090 dan menganalisis tabel keaktifan targets.
- **Input Uji**: URL `http://localhost:9090` di browser komputer klien.
- **Prosedur Langkah Pengujian**:   Administrator membuka browser web, mengetikkan alamat URL `http://localhost:9090` pada address bar, lalu menekan Enter. Pada panel navigasi atas Prometheus, administrator mengklik menu *Status* -> *Targets*, lalu mengamati status kesehatan target.
- **Output yang Diharapkan**: Dashboard Prometheus termuat. Halaman Targets menampilkan target `prometheus` dan target `haproxy` dalam status berwarna hijau bertuliskan **UP**.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Prometheus bekerja menggunakan model tarikan (*pull model*) yang secara periodik mengirimkan request HTTP GET ke endpoint metrik target. Di dalam file konfigurasi `prometheus.yml`, target `haproxy` didaftarkan menggunakan domain internal Docker `haproxy-lb:1936` pada path `/metrics`. Karena port statistik HAProxy dilindungi oleh proteksi kredensial stats, Prometheus memanfaatkan opsi konfigurasi `basic_auth` untuk mengirimkan header otentikasi HTTP dasar.
  
  Tangkapan layar di atas menunjukkan status target `haproxy` berada dalam kondisi **UP** dengan waktu scraping terakhir `2.861s ago` dan durasi respons scraping `1.042ms`. Hal ini membuktikan bahwa Prometheus berhasil melompati proteksi kata sandi stats HAProxy dan berhasil menerjemahkan metrik mentah yang disajikan oleh modul exporter internal HAProxy ke dalam database deret waktu (*time-series database*) internalnya secara berkala.

  Scraping target ini sangat penting dalam arsitektur monitoring terdistribusi. Dengan mengumpulkan data keaktifan HAProxy, Prometheus dapat memicu alert sistem secara otomatis jika terdeteksi adanya penurunan performa load balancer, kegagalan koneksi backend, atau lonjakan request abnormal.

---

#### Langkah 3.7: Pengujian Monitoring Sistem Menggunakan Grafana
- **Tujuan Pengujian**: Memverifikasi keberhasilan integrasi visualisasi data source Prometheus pada dasbor Grafana, memastikan data deret waktu (*time-series data*) dirender secara visual dalam bentuk grafik real-time yang akurat dan interaktif.
- **Desain Langkah**: Mengakses halaman utama dashboard Grafana di port 3000, login, meng-import template dashboard Prometheus Overview, dan menganalisis grafik indikator performa.
- **Input Uji**: URL `http://localhost:3000` beserta template ID dashboard `3662`.
- **Prosedur Langkah Pengujian**:   Administrator membuka browser, mengakses `http://localhost:3000`, login dengan user default admin, meng-import template dashboard ID `3662`, menghubungkannya ke data source Prometheus, lalu memantau grafik Uptime, total series, append rate, dan aktivitas Garbage Collection.
- **Output yang Diharapkan**: Dasbor visual Grafana termuat dengan sukses. Grafik menampilkan data real-time yang terus berubah secara dinamis, tanpa ada indikasi error data source connection.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:   Provisiasi visual pada Grafana terhubung secara seamless dengan server Prometheus melalui konfigurasi otomatis berkas `datasource.yml`. Pada dashboard *Prometheus 2.0 Overview* (ID: 3662), data metrik dirender menggunakan kueri bahasa PromQL (*Prometheus Query Language*) secara kontinu. Dasbor atas menunjukkan uptime Prometheus mencapai 100% penuh selama 1 jam terakhir dengan jumlah data series aktif terakumulasi sebanyak 1451 series. Status `N/A` pada missed/skipped iterations verifikasi tidak ada query internal yang mengalami keterlambatan eksekusi.
  
  Dasbor tengah menyajikan visualisasi grafik *Appended Samples per Second* yang berfluktuasi secara dinamis di kisaran 60-80 samples/s, menggambarkan kecepatan penyimpanan data metrik baru. Grafik durasi scraping menunjukkan rata-rata waktu respons penarikan metrik berada di bawah 0.008 detik, membuktikan efisiensi komunikasi antar kontainer di dalam Docker bridge network. Dasbor bawah menunjukkan keaktifan siklus pembersihan memori otomatis (*Garbage Collection*) untuk menjaga konsumsi RAM kontainer agar tetap stabil dan terhindar dari anomali kebocoran memori (*memory leak*), memvalidasi kesiapan sistem monitoring untuk kebutuhan diagnosa sistem jangka panjang.

  Keberhasilan visualisasi Grafana ini membuktikan stabilitas integrasi provisioning datasource Grafana. Datasource yang didefinisikan secara deklaratif di `datasource.yml` terbukti langsung dapat dibaca oleh panel-panel visualisasi Grafana, menghemat waktu setup manual bagi administrator sistem saat melakukan deployment dari nol.

---
## VII : PENUTUP (Kesimpulan dan Saran)

### 13.1 Kesimpulan
Berdasarkan seluruh tahapan rekayasa arsitektur, otomatisasi deployment menggunakan Ansible, serta hasil eksekusi dari 17 langkah pengujian terperinci yang telah dilaksanakan pada platform *Enterprise Private Cloud Storage* ini, maka dapat ditarik kesimpulan ilmiah sebagai berikut:
1. Otomatisasi deployment menggunakan Ansible Playbook modular berbasis *Roles* terbukti sukses melakukan inisialisasi direktori, instalasi Docker Engine, generator sertifikat SSL OpenSSL, dan kompilasi container stack secara konsisten dengan status *failed=0*, meniadakan potensi kesalahan penulisan manual oleh administrator.
2. Mekanisme ketersediaan tinggi (*High Availability*) yang dibangun memanfaatkan load balancer HAProxy dengan algoritma Round Robin dan persistensi cookie terbukti sangat andal dalam menangani kegagalan server aplikasi (*failover*) di bawah 3 detik secara transparan tanpa memutus sesi login aktif pengguna atau memaksa login ulang.
3. Penerapan arsitektur aplikasi *stateless* melalui pengalihan data biner ke MinIO Object Storage via API S3 dan penyimpanan sesi login ke Redis cache terbukti sukses menjaga keuntuhan berkas pengguna melintasi siklus hidup kontainer.
4. Sistem pemantauan kinerja terintegrasi Prometheus dan Grafana telah berfungsi optimal mengumpulkan data metrik secara real-time dan menyajikan visualisasi grafis performa server yang akurat untuk mendukung pemeliharaan sistem secara proaktif.

### 13.2 Saran
Untuk meningkatkan ketangguhan, keamanan, dan skalabilitas platform cloud storage ini pada tahap pengembangan berikutnya, disarankan beberapa rekomendasi teknis sebagai berikut:
1. **Menerapkan Replikasi Database Relasional**: Mengembangkan arsitektur database MariaDB menjadi cluster database terdistribusi menggunakan Galera Cluster atau skema master-slave replication untuk mengeliminasi kerentanan kehilangan database metadata.
2. **Mengonfigurasi MinIO Erasure Coding**: Mengimplementasikan MinIO Distributed mode pada minimal 4 drive penyimpanan terpisah untuk mengaktifkan perlindungan kehilangan berkas otomatis (*erasure coding*) di tingkat penyimpanan objek biner backend.
3. **Migrasi ke Orkestrasi Kubernetes**: Mengalihkan manajemen container stack dari Docker Compose ke Kubernetes cluster untuk mendukung kemampuan pemulihan kontainer secara mandiri (*self-healing container*), load balancing ingress yang lebih canggih, serta penskalaan kapasitas horizontal secara otomatis (*autoscaling*).
