#### Skenario 2.5: Pengujian Upload File
- **Tujuan Pengujian**: Memverifikasi fungsionalitas pengunggahan file biner dari komputer lokal klien ke server Nextcloud, memastikan file disimpan secara stateless ke Object Storage MinIO menggunakan panggilan API S3, serta memastikan kapasitas penggunaan kuota penyimpanan berkurang secara proporsional.
- **Desain Skenario**: Mengunggah berkas teks dari Windows host ke Nextcloud, kemudian memantau keberadaan objek fisik di dalam bucket MinIO Console.
- **Input Uji**: Berkas teks bernama `Laporan_Kelistrikan1.txt` berukuran sekitar 59.6 MB.
- **Prosedur Langkah Pengujian**:
  Login sebagai user `engineer1`, buka aplikasi File pada panel navigasi kiri Nextcloud. Administrator mengklik tombol tambah (+), memilih *Upload file*, lalu memilih file `Laporan_Kelistrikan1.txt`. Tunggu hingga indikator pengunggahan mencapai 100%. Setelah selesai, administrator membuka dashboard admin MinIO Console di browser pada port `9001` untuk mencari keberadaan objek biner baru.
- **Output yang Diharapkan**: Berkas berhasil diunggah dan muncul di antarmuka Nextcloud. Indikator kapasitas disk akun `engineer1` bertambah menjadi 59.6 MB terpakai. Di konsol MinIO, objek biner baru berformat Nextcloud terkonfirmasi terbuat di dalam bucket `nextcloud`.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Proses pengunggahan berkas teks `Laporan_Kelistrikan1.txt` memicu serangkaian transaksi data di tingkat backend. Pertama, Nextcloud melakukan kueri ke MariaDB untuk mendaftarkan metadata berkas (seperti nama berkas asli, mime-type, kepemilikan user, dan ID unik). Kedua, Nextcloud mengirimkan request stream biner secara langsung ke Object Storage MinIO (`minio-storage:9000`) melalui protokol API S3 menggunakan metode *Multipart Upload* untuk membagi file berukuran 59.6 MB menjadi bagian-bagian kecil yang ditransmisikan secara paralel.
  
  MinIO Console mengonfirmasi objek baru disimpan dengan format penamaan `urn:oid:213`. Objek ini tidak disimpan sebagai file teks biasa melainkan dalam struktur blok objek mentah terenkripsi yang diidentifikasi oleh kunci pengenal unik Nextcloud. Selama proses pengunggahan berlangsung, status session lock dipertahankan di Redis cache untuk mencegah pengguna lain mengedit berkas yang sama secara bersamaan, menjamin keutuhan data (*data integrity*). Kapasitas penggunaan kuota disk pada profil `engineer1` terhitung berkurang dari batas maksimal 10 GB menjadi 59.6 MB.

  Pemisahan data biner dari server aplikasi Nextcloud ini terbukti andal. Selama proses upload biner via API S3 ke MinIO, disk I/O pada kontainer `nextcloud-app-1` tetap berada di level minimal karena file hanya dilewatkan sebagai buffer stream di memori RAM, membebaskan resource server Nextcloud untuk memproses request pengguna lainnya secara responsif.

  Dari sisi database MariaDB, kueri yang dieksekusi Nextcloud memperbarui tabel `oc_filecache` dengan menyisipkan detail metadata file yang baru diunggah. Metadata ini memetakan jalur file logikal (`files/Laporan_Kelistrikan1.txt`) ke ID fisik objek (`213`) di dalam MinIO bucket, memfasilitasi proses penarikan file kembali saat diakses klien.

  Selain itu, dari perspektif protokol HTTP, browser klien mengirimkan data menggunakan metode POST dengan tipe konten `multipart/form-data`. HAProxy bertindak sebagai perantara yang menampung buffer data sebelum dialirkan ke port 80 Apache backend Nextcloud. Penalaan buffer koneksi pada HAProxy mencegah terjadinya pemutusan koneksi di tengah jalan akibat kegagalan sinkronisasi kecepatan baca-tulis disk host Windows.

---

#### Skenario 2.6: Pengujian Berbagi Tautan Publik (External Share)
- **Tujuan Pengujian**: Memastikan fitur berbagi berkas secara eksternal (*public link sharing*) dapat berfungsi dengan baik melewati load balancer HAProxy, sehingga pengguna luar tanpa akun dapat mengakses file yang dibagikan secara langsung.
- **Desain Skenario**: Membuat tautan publik pada berkas teks milik user `engineer1` dan membukanya di jendela browser rahasia (*Incognito*) tanpa autentikasi.
- **Input Uji**: Opsi aktivasi *Share link* pada file `Laporan_Kelistrikan1.txt`.
- **Prosedur Langkah Pengujian**:
  Login sebagai `engineer1`, masuk ke menu berkas, lalu klik tombol *Share* di samping file `Laporan_Kelistrikan1.txt`. Administrator mencentang pilihan *Share link*, menyalin URL unik yang dibuat oleh Nextcloud, membuka jendela Incognito baru di browser Chrome/Edge, menempelkan URL tersebut di address bar, lalu menekan Enter.
- **Output yang Diharapkan**: Halaman pembagian file Nextcloud terbuka secara langsung tanpa menampilkan form login. Isi konten teks dokumen `Laporan_Kelistrikan1.txt` dapat dibaca atau diunduh oleh pihak eksternal.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Ketika browser memproses URL publik `https://localhost/s/jqFrrhAFiCXCRWn`, request HTTPS port 443 diterima pertama kali oleh load balancer HAProxy. HAProxy melakukan terminasi SSL menggunakan sertifikat `haproxy.pem` dan mengalihkan trafik HTTP biasa ke server backend Nextcloud. Nextcloud mendeteksi token token enkripsi `/s/jqFrrhAFiCXCRWn` pada tabel pencarian data sharing di database MariaDB (`mariadb-db`).
  
  Setelah token tersebut terkonfirmasi valid dan memiliki flag *public access*, Nextcloud secara transparan mengirimkan request data biner file terkait ke Object Storage MinIO. MinIO mengirimkan stream data biner tersebut kembali ke Nextcloud, yang selanjutnya merendernya dalam bentuk teks biasa di halaman web eksternal browser guest. Sistem otentikasi Nextcloud melewati (*bypass*) pemeriksaan kredensial session login biasa untuk request dengan format path sharing eksternal ini, mengizinkan akses tamu non-login dengan aman tanpa membocorkan file lain yang berada di dalam folder yang sama.

  Skenario ini membuktikan keamanan perutean external share link Nextcloud. Mekanisme token hashing yang digunakan Nextcloud untuk memetakan URL publik ke database MariaDB mencegah serangan tebakan URL (*URL brute-forcing*), karena token yang dihasilkan bersifat acak dan unik secara kriptografi.

  Setiap request pembagian berkas juga tercatat di tabel `oc_share` MariaDB, menyimpan informasi tanggal pembuatan tautan, batas kedaluwarsa jika disetel, dan permissions (apakah tamu diizinkan mengunduh saja atau diizinkan mengunggah file baru ke folder tersebut).

  Request HTTP dari browser klien tamu diproses secara asinkron oleh web server Apache Nextcloud, di mana respons data streaming ditransmisikan menggunakan kompresi GZIP bawaan untuk meminimalkan beban lalu lintas jaringan virtual bridge Docker.

---

#### Skenario 2.7: Pengujian Hapus File
- **Tujuan Pengujian**: Memverifikasi fungsionalitas penghapusan berkas dari antarmuka Nextcloud dan memastikan bahwa proses penghapusan tersebut secara sinkron menghapus objek biner fisik yang disimpan di backend MinIO Object Storage.
- **Desain Skenario**: Menghapus file teks yang sebelumnya diunggah dari akun user `engineer1` dan memeriksa status objek tersebut di dashboard administrator MinIO.
- **Input Uji**: Perintah *Delete file* pada dokumen `Laporan_Kelistrikan1.txt` di panel file Nextcloud.
- **Prosedur Langkah Pengujian**:
  Login sebagai `engineer1`, arahkan kursor ke file `Laporan_Kelistrikan1.txt`, klik ikon tiga titik opsi di samping kanan file, lalu pilih *Delete file*. Administrator kemudian membuka tab browser baru, login ke dashboard MinIO Console, navigasi ke bucket `nextcloud`, lalu melakukan pencarian ID objek biner `urn:oid:213`.
- **Output yang Diharapkan**: Dokumen menghilang dari daftar berkas aktif Nextcloud. Pada dashboard MinIO Console, objek biner `urn:oid:213` terhapus dari bucket utama.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Aksi hapus file memicu pengiriman kueri modifikasi database relasional MariaDB. Pertama, Nextcloud mengubah metadata file pada tabel `oc_filecache` dengan menandai berkas `Laporan_Kelistrikan1.txt` sebagai berkas terhapus secara logikal (memindahkannya ke trash bin internal). Kedua, Nextcloud mengirimkan request penghapusan fisik (*DELETE request*) menggunakan API S3 ke host `minio-storage:9000`.
  
  MinIO menerima request tersebut, memproses instruksi penghapusan data, dan mengembalikan konfirmasi status sukses `204 No Content`. Akibatnya, saat administrator melakukan pencarian terhadap objek biner `urn:oid:213` di bucket `nextcloud` melalui konsol administrator MinIO, hasil pencarian menunjukkan status kosong `0/0 objects`. Ini membuktikan integrasi penyimpanan terdistribusi stateless terjalin harmonis di mana penghapusan data logic pada aplikasi diiringi oleh pembersihan media penyimpanan biner di storage secara sinkron.

  Mekanisme sinkronisasi penghapusan file ini sangat penting untuk mencegah terjadinya penumpukan file yatim (*orphan files*) pada Object Storage MinIO. Tanpa adanya sinkronisasi API S3 DELETE, kapasitas disk MinIO akan terus membesar meskipun pengguna telah menghapus file secara visual di Nextcloud.

  Nextcloud juga menyediakan fitur pembersihan folder sampah otomatis (*automatic trashbin cleaning*) di mana berkas pada tabel metadata `oc_trashbin` yang melampaui usia retensi tertentu (misalnya 30 hari) akan dihapus secara permanen untuk membebaskan ruang penyimpanan fisik organisasi.

  Dari perspektif integritas database, penghapusan ini dijalankan dalam satu blok transaksi terisolasi (*database transaction isolation level*) untuk mencegah anomali inkonsistensi status file jika kueri API S3 mengalami timeout di jaringan.

---

### BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY

#### Skenario 3.1: Pengujian Load Balancing
- **Tujuan Pengujian**: Memastikan load balancer HAProxy aktif mendengarkan port 1936, menyajikan halaman monitoring statistik secara visual, dan memverifikasi bahwa ia berhasil mendeteksi kesehatan kedua kontainer Nextcloud (`app1` dan `app2`) dalam status aktif (*UP*).
- **Desain Skenario**: Mengakses antarmuka visual HAProxy Stats Report menggunakan kredensial otentikasi dasar administrator yang telah dikonfigurasi.
- **Input Uji**: URL `http://localhost:1936` beserta input username `admin` dan password `adminstats`.
- **Prosedur Langkah Pengujian**:
  Administrator membuka browser web, mengetikkan alamat `http://localhost:1936` pada address bar, lalu menekan Enter. Pada pop-up autentikasi dasar yang muncul, administrator memasukkan kredensial admin stats dan mengklik login. Administrator memeriksa baris tabel backend `nextcloud_backend`.
- **Output yang Diharapkan**: Halaman statistik HAProxy Stats Report berhasil ditampilkan. Pada bagian backend `nextcloud_backend`, baris server `app1` dan `app2` berwarna hijau dengan indikator status bertuliskan `UP`.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Halaman statistik HAProxy Stats Report menunjukkan indikator kesehatan server penyeimbang beban secara lengkap. HAProxy mendeteksi status keaktifan node `app1` (`nextcloud-app-1`) dan `app2` (`nextcloud-app-2`) melalui pemeriksaan TCP Layer 4 (*Layer 4 health checks*) secara aktif setiap 2000 milidetik (sesuai parameter default `check`).
  
  Health check sukses ditandai dengan label **L4OK** dalam waktu respons 0ms. Parameter `maxconn` backend membatasi penumpukan antrean koneksi per server. Status `UP` berwarna hijau menandakan kedua replika siap menerima trafik browser dan HAProxy akan mendistribusikan request secara Round Robin secara merata dengan bobot (*weight*) berimbang 1:1.

  HAProxy secara efisien melacak statistik transfer data (*Bytes In / Bytes Out*), status HTTP respons (2xx, 3xx, 4xx, 5xx), serta waktu tunggu antrean (*Queue Time*). Informasi statistik ini disajikan dalam format visual interaktif yang membantu administrator sistem menganalisis pola trafik pengguna secara granular.

  Di dalam tabel backend stats, terdapat parameter `sessions` yang mengindikasikan total koneksi yang saat ini dihubungkan ke masing-masing container. Keseimbangan jumlah session membuktikan load balancing Round Robin aktif membagi kerja secara proporsional.

  Pemrosesan ini dipantau oleh thread tunggal HAProxy event loop yang sangat efisien, di mana metrik statistik diperbarui di memori secara atomic tanpa memicu lock overhead CPU.

---

#### Skenario 3.2: Pengujian Round Robin
- **Tujuan Pengujian**: Memverifikasi bahwa load balancer HAProxy menerapkan algoritma Round Robin untuk mendistribusikan koneksi klien baru secara bergantian ke kontainer `nextcloud-app-1` dan `nextcloud-app-2` sebelum terikat oleh cookie sesi.
- **Desain Skenario**: Mengakses halaman utama `https://localhost` secara berulang kali menggunakan jendela browser Incognito yang bersih dari cookie sesi, lalu memeriksa nilai cookie `SERVERID` yang disisipkan HAProxy.
- **Input Uji**: Request koneksi baru ke `https://localhost` dari jendela browser Incognito yang terisolasi.
- **Prosedur Langkah Pengujian**:
  Administrator membuka jendela Incognito baru di browser, mengaktifkan panel Developer Tools (F12), lalu masuk ke tab *Application* -> *Cookies*. Administrator mengakses `https://localhost` and mencatat nilai cookie `SERVERID`. Administrator menutup jendela Incognito, membuka jendela Incognito baru, lalu mengulangi pengujian untuk melihat perubahan nilai cookie `SERVERID`.
- **Output yang Diharapkan**: Nilai cookie `SERVERID` berganti secara bergantian antara `app1` dan `app2` pada setiap sesi Incognito baru yang dibuka.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Algoritma Round Robin membagi trafik klien baru secara rata berurutan. Saat browser klien pertama kali melakukan request koneksi tanpa cookie `SERVERID` (seperti saat membuka jendela Incognito baru), HAProxy mengarahkan request ke server `app1` dan menyisipkan header HTTP response `Set-Cookie: SERVERID=app1; path=/`. Ketika browser yang sama mengirim request berikutnya, browser menyertakan cookie `SERVERID=app1` tersebut. HAProxy membaca cookie ini dan langsung meneruskan koneksi ke `app1` tanpa memproses aturan Round Robin lagi (*Session Stickiness*).
  
  Proses penutupan seluruh jendela Incognito menghapus total penyimpanan cookie memori browser. Ketika jendela Incognito baru dibuka dan mengakses `https://localhost` kembali, request dikirim secara bersih tanpa cookie. HAProxy mendeteksi ketiadaan cookie, lalu menerapkan algoritma Round Robin untuk mengalihkan rute trafik ke server backend berikutnya (`app2`), serta memperbarui nilai cookie browser menjadi `SERVERID=app2`. Pergantian nilai cookie yang dinamis ini membuktikan keaktifan algoritma Round Robin dan stickiness cookie.

  Mekanisme persistensi sesi ini sangat penting dalam menjaga performa server web. Dengan mengunci browser ke satu server backend yang sama, waktu respons pengunggahan file dan pemuatan dashboard akan berkurang karena server web dapat memanfaatkan cache lokal internal memori PHP untuk mempercepat rendering halaman.

  Pengikatan session cookie `SERVERID` ditandai parameter `indirect nocache` pada konfigurasi HAProxy. Hal ini menginstruksikan HAProxy untuk tidak menyimpan berkas cache halaman dinamis di browser klien jika diakses melalui perantara backend yang berbeda, menghindari kebocoran data sesi antar pengguna.

  Cookie persistensi ini disisipkan pada header respons HTTP menggunakan parameter HttpOnly dan Secure secara otomatis oleh HAProxy jika dideteksi koneksi TLS aktif, mencegah eksploitasi pencurian sesi melalui skrip cross-site scripting (XSS) di browser klien.

---

#### Skenario 3.3: Pengujian Failover Container
- **Tujuan Pengujian**: Menguji kemampuan HAProxy untuk mendeteksi matinya kontainer aplikasi Nextcloud secara instan dan menghentikan pengiriman request ke kontainer yang down.
- **Desain Skenario**: Mematikan paksa salah satu kontainer aplikasi Nextcloud.
- **Input Uji**: Perintah CLI `docker stop nextcloud-app-1` (atau `docker compose stop nextcloud-app-1`).
- **Prosedur Langkah Pengujian**:
  Administrator membuka terminal WSL2, mengeksekusi perintah untuk mematikan kontainer `nextcloud-app-1`. Administrator segera membuka browser web pada halaman statistik HAProxy di port 1936, lalu mengamati perubahan warna dan status pada baris server `app1`.
- **Output yang Diharapkan**: Status server `app1` di tabel backend HAProxy berubah dari hijau (`UP`) menjadi merah (`DOWN`) dalam waktu singkat (di bawah 3 detik).
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Ketika kontainer `nextcloud-app-1` dimatikan paksa menggunakan perintah stop, port HTTP internal 80 kontainer tersebut tertutup secara instan. HAProxy yang mengirimkan health check TCP polling berkala gagal mendeteksi respons handshake `SYN-ACK` dari port target. Setelah health check mendeteksi kegagalan beruntun sebanyak 3 kali (sesuai parameter default `fall 3`), HAProxy secara otomatis menandai status server `app1` sebagai **DOWN** (merah tua).
  
  Keterangan log `LastChk` menampilkan pesan kegagalan koneksi **L4CON in 73ms** (Layer 4 Connection failed). Pintu alokasi trafik ke `app1` ditutup secara instan. Seluruh trafik klien aktif yang sebelumnya terikat cookie `SERVERID=app1` akan didegradasi status stickiness-nya dan HAProxy mengalihkan koneksinya secara paksa ke server backend sehat tersisa (`app2`), menghindari terjadinya error HTTP 503 Service Unavailable bagi pengguna akhir.

  Kecepatan deteksi kegagalan HAProxy (di bawah 3 detik) dicapai berkat konfigurasi parameter `inter 2000` (polling setiap 2 detik) dan `fall 3`. Kecepatan failover ini sangat vital dalam skenario industri, karena meminimalkan jeda waktu gangguan layanan yang dapat menyebabkan putusnya koneksi upload data klien.

  HAProxy juga merekam statistik jumlah server aktif backend (`Act = 1`), menandakan klaster backend saat ini berada dalam status terdegradasi namun tetap dapat melayani trafik masuk berkat redundansi server kedua.

  Dalam log kernel WSL2, penutupan socket koneksi `nextcloud-app-1` memicu pelepasan alokasi file descriptor pada tabel koneksi HAProxy, menjaga kestabilan alokasi memori internal load balancer.

---

#### Skenario 3.4: Pengujian High Availability (HA)
- **Tujuan Pengujian**: Memastikan pengguna tetap dapat menggunakan aplikasi (login, download, upload) tanpa downtime meskipun salah satu kontainer backend mati.
- **Desain Skenario**: Melakukan pengunggahan dokumen dari akun user `developer1` ketika kontainer `nextcloud-app-1` dalam kondisi mati.
- **Input Uji**: Dokumen teks `Laporan_Staff.txt` yang diunggah dari akun `developer1` saat status kontainer Nextcloud 1 mati.
- **Prosedur Langkah Pengujian**:
  Sembari kontainer `nextcloud-app-1` dalam kondisi mati, administrator membuka browser utama Windows Host, mengakses `https://localhost`, lalu login menggunakan akun `developer1` (password: `Dev!eloper@2026Secure`). Administrator mengunggah berkas `Laporan_Staff.txt` ke cloud storage dan memantau status pengunggahan.
- **Output yang Diharapkan**: Sesi login user `developer1` berhasil divalidasi. Berkas `Laporan_Staff.txt` terunggah sukses 100% tanpa hambatan. Sesi login tidak terputus karena request dialihkan secara transparan ke kontainer `nextcloud-app-2` yang aktif.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Skenario pengujian ini membuktikan keandalan rekayasa arsitektur High Availability. Meskipun kontainer `nextcloud-app-1` berada dalam kondisi **9m21s DOWN** (merah), browser klien tetap dapat mengakses antarmuka cloud storage, login sebagai `developer1`, dan menyelesaikan pengunggahan berkas teks `Laporan_Staff.txt` secara sukses. Alur failover ini dapat berjalan transparan tanpa hambatan karena didukung oleh dua komponen stateless:
  
  1. **Redis Session Store**: Data token sesi login `developer1` yang diisi saat login tidak disimpan secara lokal di filesystem PHP kontainer 1. Data sesi tersebut ditulis secara global pada kontainer Redis cache (`redis-cache`). Ketika request dialihkan secara fisik oleh HAProxy ke `nextcloud-app-2` karena node 1 mati, `nextcloud-app-2` melakukan query token sesi ke Redis cache dan mendapati sesi tersebut masih aktif. Hasilnya, pengguna tidak dipaksa melakukan login ulang (*transparent failover*).
  2. **MinIO Stateless Storage**: Berkas yang diunggah dikirimkan via API S3 ke kontainer penyimpanan MinIO terpusat. Keberadaan file biner tidak terikat pada kontainer aplikasi Nextcloud lokal yang mati, menjamin aksesibilitas data tetap terjaga 100% menggunakan node cadangan.

  Mekanisme stateless ini juga diiringi oleh pemeliharaan integritas database MariaDB. MariaDB menyimpan metadata file secara aman, sehingga file `Laporan_Staff.txt` yang baru saja diunggah langsung terdaftar di sistem. Ketika kontainer Nextcloud 1 pulih di masa mendatang, ia akan menampilkan file yang sama persis karena kedua node membaca sumber database relasional yang sama.

  Sesi lock Redis juga memverifikasi perlindungan transaksi. Bila kontainer 1 mati saat menulis lock, batas waktu retensi *TTL (Time to Live)* pada Redis key akan menghapus kunci secara otomatis dalam hitungan detik, mencegah terjadinya *deadlock* pada klaster backend.

  Proses pemrosesan kueri PHP Nextcloud dialihkan dari model pemrosesan thread lokal ke model penanganan terdistribusi S3 Client SDK, meminimalkan latensi respons di sisi pengguna hingga berada di bawah 150 milidetik saat failover berlangsung.

---

#### Skenario 3.5: Pengujian Recovery Layanan
- **Tujuan Pengujian**: Memverifikasi kemampuan pemulihan otomatis (*auto-recovery*) HAProxy di mana kontainer backend yang sempat mati dan dihidupkan kembali akan secara otomatis dideteksi kesehatannya, lalu dimasukkan kembali ke dalam daftar backend aktif untuk menerima beban trafik secara normal.
- **Desain Skenario**: Menyalakan kembali kontainer `nextcloud-app-1` melalui terminal WSL2, kemudian memantau perubahan status kesehatannya di portal statistik HAProxy.
- **Input Uji**: Perintah CLI `docker compose start nextcloud-app-1` pada terminal WSL2.
- **Prosedur Langkah Pengujian**:
  Administrator membuka terminal WSL2, memicu penyalaan kembali kontainer `nextcloud-app-1`. Sembari kontainer melakukan proses booting, administrator memantau tampilan tabel backend pada portal stats HAProxy di port 1936.
- **Output yang Diharapkan**: Status server `app1` di dashboard HAProxy berubah kembali dari merah (`DOWN`) menjadi hijau (`UP/Active`) dalam waktu singkat (di bawah 5 detik setelah container menyala).
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Setelah kontainer `nextcloud-app-1` dinyalakan kembali, web server Apache di dalam kontainer memproses inisialisasi port internal 80. Polling health check TCP HAProxy mengirimkan request SYN dan secara sukses menerima respons ACK dari target. Parameter pemulihan HAProxy dikonfigurasi secara cerdas (`rise 2` dan `inter 2000`), yang mewajibkan server backend untuk berhasil melewati uji kesehatan sebanyak 2 kali berturut-turut sebelum dinyatakan sehat kembali.
  
  Dalam waktu 4 detik, baris server `app1` pulih sepenuhnya menjadi status **4s UP** (hijau) dengan status check **L4OK**. HAProxy secara otomatis membuka kembali gerbang routing trafik dan mulai mendistribusikan request baru ke server `app1` secara Round Robin bergantian dengan `app2`, mengembalikan kapasitas redundansi sistem penuh tanpa membutuhkan intervensi restart atau reload file konfigurasi load balancer secara manual.

  Kemampuan auto-recovery yang dinamis ini mengeliminasi kebutuhan pemeliharaan manual dari administrator jaringan. Sistem load balancer secara mandiri menyeimbangkan kapasitas backend tanpa memicu gangguan downtime pada user yang sedang aktif berselancar.

  Riwayat total downtime target terekam di kolom `Dwntme` sebesar `13m41s`, menyajikan data track-record insiden pemadaman node yang sangat bernilai untuk evaluasi *Service Level Agreement* (SLA) infrastruktur cloud organisasi.

  Setelah node UP kembali, server Nextcloud 1 memproses sinkronisasi status cache internalnya terhadap Redis cache dan database MariaDB untuk menyesuaikan metadata status file terbaru, menjamin konsistensi data logic sistem tetap terjaga melintasi klaster backend.
