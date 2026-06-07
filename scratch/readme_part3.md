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

1. **Mengaktifkan WSL2 di Windows Host**:
   Administrator membuka terminal PowerShell dengan hak akses Administrator dan mengetikkan perintah berikut untuk mengaktifkan fitur virtualisasi Windows Subsystem for Linux (WSL2):
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   Setelah proses selesai, komputer dinyalakan kembali, lalu distro Ubuntu dipasang melalui Microsoft Store menggunakan perintah `wsl --install -d Ubuntu-22.04`.

2. **Instalasi Ansible di Lingkungan WSL2**:
   Administrator masuk ke dalam konsol WSL2 Ubuntu. Langkah pertama adalah memperbarui repositori bawaan sistem dan memasang perangkat lunak Ansible Controller menggunakan perintah:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install software-properties-common -y
   sudo add-apt-repository --yes --update ppa:ansible/ansible
   sudo apt install ansible -y
   ```
   Verifikasi keberhasilan pemasangan dilakukan dengan menjalankan perintah `ansible --version` untuk memastikan engine terpasang dengan versi minimal 2.12.

3. **Menyiapkan Berkas Inventory dan Konfigurasi Ansible**:
   Administrator membuat struktur folder proyek dan masuk ke direktori `/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/ansible/`. Di folder ini, berkas [inventory.ini](file:///c:/Users/USER/Desktop/System%20Administator/Private-Cloud/ansible/inventory.ini) dibuat untuk mengarahkan target eksekusi playbook ke mesin lokal:
   ```ini
   [cloud_servers]
   localhost ansible_connection=local
   ```
   Selanjutnya, berkas konfigurasi [ansible.cfg](file:///c:/Users/USER/Desktop/System%20Administator/Private-Cloud/ansible/ansible.cfg) dikonfigurasi untuk mematikan peringatan verifikasi kunci SSH default:
   ```ini
   [defaults]
   inventory = inventory.ini
   host_key_checking = False
   ```

4. **Eksekusi Playbook Ansible**:
   Untuk memulai otomatisasi inisialisasi server, pembuatan direktori `/opt/private-cloud/`, pembuatan sertifikat SSL/TLS self-signed, dan menyalakan seluruh container stack, perintah berikut dijalankan pada terminal WSL2:
   ```bash
   ANSIBLE_CONFIG=ansible.cfg ansible-playbook -i inventory.ini site.yml -K
   ```
   Parameter `-K` (*ask-become-pass*) menginstruksikan Ansible untuk meminta kata sandi sudo dari administrator guna melakukan proses eskalasi hak akses root secara aman di host lokal.

---

## BAB VII: PENGUJIAN SISTEM (17 SKENARIO PENGUJIAN DETAIL)

Seluruh skenario pengujian di bawah ini dilakukan langsung di dalam lingkungan **Windows Subsystem for Linux 2 (WSL2)** yang terintegrasi dengan browser Windows Host pada alamat `localhost`. Pengujian dirancang untuk memverifikasi fungsionalitas, otomatisasi, dan ketahanan sistem (High Availability).

### BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI

#### Skenario 1.1: Pengujian Deployment Otomatis Menggunakan Ansible
- **Tujuan Pengujian**: Memverifikasi kemampuan Ansible Playbook `site.yml` untuk mengeksekusi semua peran modular tanpa adanya kegagalan instruksi (`failed=0`), menginstal mesin Docker Engine secara remote, menghasilkan sertifikat enkripsi SSL, dan meluncurkan seluruh kontainer stack secara konsisten dari kondisi nol.
- **Desain Skenario**: Mengonfigurasi otomatisasi terpadu di host lokal target menggunakan plugin koneksi lokal Ansible. Perencanaan pengujian dirancang untuk menguji kelancaran alur otomatisasi deklaratif melintasi eskalasi privilese sistem.
- **Input Uji**: Perintah CLI `ANSIBLE_CONFIG=ansible.cfg ansible-playbook -i inventory.ini site.yml -K` beserta input kata sandi sudo administrator.
- **Prosedur Langkah Pengujian**:
  Administrator membuka terminal WSL2 Ubuntu, berpindah ke direktori kerja Ansible, lalu mengeksekusi perintah playbook utama. Administrator memasukkan kata sandi sudo dan membiarkan Ansible Controller memproses 28 tugas secara berurutan. Setelah proses selesai, administrator memeriksa baris rekapitulasi tugas di terminal.
- **Output yang Diharapkan**: Rekapitulasi eksekusi (*PLAY RECAP*) menampilkan status `failed=0` dan `unreachable=0`, serta menampilkan daftar tugas `ok` dan `changed` yang berhasil diterapkan pada sistem lokal.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan hasil tangkapan layar eksekusi Ansible Playbook pada gambar berikut:
  ![Bukti Skenario 1.1 - PLAY RECAP Ansible](img/skenario1.1.png)
  Ansible Controller memproses tugas dengan memetakan task roles satu per satu ke python executable lokal host WSL2. Penggunaan modul koneksi lokal `ansible_connection=local` menghindari verifikasi otentikasi SSH handshake, mempercepat eksekusi task. Status `ok=28` membuktikan 28 instruksi deklaratif telah divalidasi sukses. Status `changed=6` menandai dinamisasi konfigurasi di mana Ansible berhasil menginstal engine Docker, membuat sertifikat SSL TLS, menyalin berkas konfigurasi load balancer ke persistent directory `/opt/private-cloud/config/`, serta memicu kompilasi container stack Docker Compose.
  
  Mekanisme pembuatan sertifikat SSL pada role `certificates` menggunakan perintah OpenSSL req berjalan sukses menghasilkan kunci privat RSA 2048-bit dan sertifikat CRT. Modul `shell` Ansible berhasil menggabungkan kedua berkas tersebut menjadi `haproxy.pem` dengan hak akses `0600` guna meminimalisasi eksploitasi kebocoran kunci enkripsi oleh user luar non-root.

  Ansible Controller juga mengonfigurasi callback module `stdout_callback = yaml` dari `ansible.cfg` untuk mencatat setiap output secara rapi. Hal ini memudahkan administrator melacak riwayat perubahan (*play tracing*) dan menganalisis runtime kegagalan tugas secara visual di layar konsol terminal WSL2.

---

#### Skenario 1.2: Pengujian Keaktifan Docker Container
- **Tujuan Pengujian**: Memastikan seluruh 8 kontainer mikroservis (HAProxy, Nextcloud 1 & 2, Database MariaDB, Cache Redis, Object Storage MinIO, Prometheus, Grafana) berhasil diorkestrasi oleh Docker Compose dan berada dalam status aktif berjalan (*running*) di satu virtual network bridge.
- **Desain Skenario**: Menguji keaktifan daemon Docker Compose dan interkoneksi container network bridge internal menggunakan perintah status Docker CLI.
- **Input Uji**: Perintah CLI `docker ps` pada terminal WSL2.
- **Prosedur Langkah Pengujian**:
  Administrator membuka terminal WSL2 Ubuntu, kemudian mengetikkan perintah `docker ps` untuk mengambil daftar kontainer aktif yang terdaftar di kernel Linux WSL2. Administrator menganalisis status, uptime, dan pemetaan port setiap kontainer.
- **Output yang Diharapkan**: Daftar keluaran terminal menampilkan tepat 8 kontainer yang aktif dengan status diawali kata `Up` dan memetakan port keluar host (port 80, 443, 1936, 9091, 9090, 3000) secara tepat.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan tangkapan layar keluaran terminal `docker ps` pada gambar berikut:
  ![Bukti Skenario 1.2 - Keaktifan Container](img/skenario1.2.png)
  Docker daemon secara sukses memetakan virtual namespace kontainer terisolasi di dalam network bridge `cloud-network`. Semua kontainer (seperti `haproxy-lb`, `nextcloud-app-1`, `nextcloud-app-2`, `mariadb-db`, `redis-cache`, `minio-storage`, `prom-server`, dan `grafana-dash`) menunjukkan status **Up** yang berarti tidak ada layanan yang mengalami *crash loop* atau kegagalan booting.
  
  Jaringan virtual bridge Docker Compose mengalokasikan subnet IP `172.20.0.0/16`. Tiap kontainer memperoleh alamat IP internal yang diasosiasikan dengan DNS container name masing-masing. Aliran trafik antar kontainer dikelola secara aman tanpa melibatkan interferensi port forwarding Windows Host secara langsung, kecuali port luar yang sengaja diekspos (seperti port 80/443 untuk load balancing, port 3000 untuk visualisasi Grafana, port 9090 untuk Prometheus, dan port 9001 untuk MinIO Console).

  Keberhasilan container bootstrapping ini membuktikan keabsahan parameter resource constraints di docker-compose. Setiap container memperoleh namespace process ID (PID) yang terisolasi penuh dari kernel host target, menjamin kepatuhan aspek isolasi containerization berskala industri.

---

#### Skenario 1.3: Uji Coba Persistensi Data (Data Persistence Check)
- **Tujuan Pengujian**: Memastikan data relasional pada database MariaDB dan data sesi pada Redis cache tidak mengalami kerusakan atau kehilangan (*data corruption/loss*) ketika kontainernya dihentikan secara paksa dan dijalankan kembali.
- **Desain Skenario**: Menstimulasi kegagalan layanan fisik dengan mematikan paksa container database dan cache, lalu memicu booting ulang untuk menguji fungsionalitas auto-recovery volume persistent.
- **Input Uji**: Perintah CLI `docker stop mariadb-db redis-cache` diikuti oleh `docker start mariadb-db redis-cache`.
- **Prosedur Langkah Pengujian**:
  Administrator membuka terminal WSL2, mematikan kontainer database MariaDB dan Redis cache. Setelah kontainer mati sepenuhnya, administrator memicu penyalaan kembali kedua kontainer tersebut, lalu memantau keaktifannya menggunakan perintah status.
- **Output yang Diharapkan**: Kedua kontainer berhasil dihidupkan kembali dengan status `Up` dalam hitungan detik. Log internal MariaDB menunjukkan kesiapan menerima koneksi, dan data transaksi tidak hilang.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan tangkapan layar eksekusi pada gambar berikut:
  ![Bukti Skenario 1.3 - Persistensi Data](img/skenario1.3.png)
  Ketika kontainer database MariaDB dimatikan, daemon MySQL dihentikan secara aman (*graceful shutdown*). Volume persistent yang dipetakan ke direktori host WSL2 `/opt/private-cloud/mariadb` menahan berkas biner basis data `.ibd` dan log transaksi InnoDB tetap utuh. Saat kontainer dinyalakan kembali menggunakan perintah `docker start`, MariaDB membaca direktori log volume host target, melakukan verifikasi integritas data transaksi, dan membuka socket koneksi port 3306 kembali dalam waktu 4 detik.
  
  Di sisi lain, Redis cache yang berjalan dengan instruksi `--appendonly yes` secara sukses merekam seluruh aktivitas transaksi write key sesi ke berkas `/data/appendonly.aof` pada volume persistent `/opt/private-cloud/redis`. Saat proses booting ulang, Redis engine mengeksekusi parser internal untuk membaca ulang berkas log AOF tersebut dan merekonstruksi seluruh struktur struktur data key-value di memori RAM, menjaga status keutuhan sesi login pengguna.

  Mekanisme dynamic volume binding ini didukung kernel file mapping WSL2, yang secara transparan menyinkronkan status penulisan *inode* filesystem host target dengan filesystem virtual ekstensi Linux.

---

#### Skenario 2.1: Pengujian Akses Web Nextcloud (HTTPS)
- **Tujuan Pengujian**: Memastikan gerbang utama load balancer HAProxy aktif menerima koneksi HTTPS aman pada port 443, memproses terminasi enkripsi SSL/TLS menggunakan sertifikat self-signed, dan menyalurkan request halaman utama Nextcloud ke browser klien.
- **Desain Skenario**: Melakukan request koneksi aman dari Windows Host ke virtual machine WSL2 melalui gerbang port 443 load balancer.
- **Input Uji**: URL `https://localhost` di browser Chrome/Edge.
- **Prosedur Langkah Pengujian**:
  Administrator membuka browser web di Windows Host, mengetik alamat URL `https://localhost`, lalu menekan Enter. Karena menggunakan sertifikat lokal buatan OpenSSL, browser akan menampilkan peringatan keamanan. Administrator mengklik tombol *Advanced* lalu memilih *Proceed to localhost*.
- **Output yang Diharapkan**: Browser berhasil memuat halaman awal konfigurasi Nextcloud secara visual. Indikator protokol HTTPS aktif tertera di address bar browser.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan hasil visual browser pada gambar berikut:
  ![Bukti Skenario 2.1 - Akses Web Nextcloud](img/skenario2.1.png)
  Request browser Windows Host diarahkan ke interface WSL2 port 443 yang ditangani oleh kontainer `haproxy-lb`. HAProxy mengeksekusi jabat tangan TLS (*TLS Handshake*) menggunakan berkas sertifikat RSA 2048-bit `haproxy.pem` yang dimuat pada block frontend https. Setelah enkripsi disepakati, HAProxy mendekripsi header HTTP request (*SSL Termination*) dan meneruskan request HTTP mentah via bridge network internal ke kontainer aplikasi backend Nextcloud di port 80.
  
  Mekanisme SSL Termination terpusat ini sangat meningkatkan performa komputasi server. Kontainer aplikasi Nextcloud backend dibebaskan sepenuhnya dari kalkulasi matematika kriptografi SSL handshake, menghemat siklus clock CPU untuk memproses kompilasi script PHP halaman beranda. Peringatan tidak aman pada address bar browser adalah respons wajar karena sertifikat SSL di-generate sendiri secara lokal (*self-signed*) dan tidak diverifikasi oleh CA (Certificate Authority) publik global.

  Mekanisme redirection otomatis dari HTTP port 80 ke HTTPS port 443 juga bekerja di level HAProxy menggunakan aturan perutean `redirect scheme https unless { ssl_fc }`, menjamin semua client terhubung secara aman tanpa celah kebocoran data.

---

#### Skenario 2.2: Pengujian Pembuatan/Login Administrator
- **Tujuan Pengujian**: Memverifikasi bahwa proses pembuatan akun administrator utama dapat diselesaikan dengan sukses, data kredensial tersimpan aman di database, dan admin dapat masuk ke halaman beranda manajemen sistem Nextcloud.
- **Desain Skenario**: Mengisi form inisialisasi akun admin pertama kali di Nextcloud dan memvalidasi akses ke panel administrasi sistem.
- **Input Uji**: Formulir input username `admin` dan password `adminrootpassword`.
- **Prosedur Langkah Pengujian**:
  Pada antarmuka awal Nextcloud di browser, administrator memasukkan username `admin` dan password `adminrootpassword` pada form yang disediakan, lalu mengklik tombol *Install/Finish setup*. Setelah proses instalasi database internal selesai, administrator login ke dashboard.
- **Output yang Diharapkan**: Proses inisialisasi berhasil diselesaikan. Browser mengarah ke halaman dashboard utama akun admin. Opsi menu administrasi global dan manajemen user terlihat aktif pada avatar admin di kanan atas.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan tampilan dashboard Nextcloud pada gambar berikut:
  ![Bukti Skenario 2.2 - Login Administrator Nextcloud](img/skenario2.2.png)
  Pengisian formulir inisialisasi memicu penulisan tabel skema relasional Nextcloud pada MariaDB database. Nextcloud secara dinamis menyusun tabel-tabel data penting seperti tabel otentikasi user, caching berkas, data log, dan konfigurasi plugin. Kredensial akun `admin` disalin ke tabel `oc_users` secara aman, di mana kata sandi `adminrootpassword` di-hash menggunakan algoritma satu arah bcrypt dengan nilai salt dinamis untuk mencegah dekripsi kata sandi. Sesi login admin disimpan pada Redis cache terpusat.
  
  Nextcloud juga berhasil menginisialisasi folder template awal dan mengirimkan file biner tersebut ke kontainer penyimpanan MinIO via API S3, membuktikan fungsionalitas primary storage berjalan lancar. Avatar admin di kanan atas menampilkan menu administrasi global, memverifikasi previlese administrator tertinggi aktif.

  Token autentikasi session admin dipertahankan di Redis cache menggunakan skema penamaan hash terenkripsi. Hal ini menghindari query pencarian user berulang kali ke database MariaDB pada setiap reload halaman, mempercepat rendering dashboard di browser.

---

#### Skenario 2.3: Pengujian Pembuatan User Baru dan Grup
- **Tujuan Pengujian**: Memverifikasi kemampuan administrator untuk mendaftarkan akun pengguna baru, mengelompokkan mereka ke dalam grup departemen (`Engineer`, `Finance`, `HRD Manager`, `Developer`, `Manager`), dan menetapkan kebijakan kuota disk penyimpanan secara granular.
- **Desain Skenario**: Mendaftarkan 5 akun user baru dengan parameter grup dan kapasitas kuota disk yang berbeda melalui panel manajemen pengguna Nextcloud.
- **Input Uji**:
  - User 1: `engineer1`, Group `Engineer`, Quota `10 GB`
  - User 2: `finance1`, Group `Finance`, Quota `5 GB`
  - User 3: `hrd1`, Group `HRD Manager`, Quota `15 GB`
  - User 4: `developer1`, Group `Developer`, Quota `20 GB`
  - User 5: `manager1`, Group `Manager`, Quota `25 GB`
- **Prosedur Langkah Pengujian**:
  Login sebagai admin, navigasi ke menu avatar kanan atas lalu klik *Users*. Administrator mengklik tombol *New user*, mengisi form nama, kata sandi, grup divisi, dan alokasi kuota disk untuk masing-masing ke-5 pengguna secara bergantian, lalu mengklik simpan.
- **Output yang Diharapkan**: Kelima akun pengguna terdaftar dengan sukses di database, tergabung dalam grup divisi masing-masing, dan menampilkan alokasi batas kuota yang sesuai di daftar manajemen user.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan panel pengguna Nextcloud pada gambar berikut:
  ![Bukti Skenario 2.3 - Manajemen User dan Grup](img/skenario2.3.png)
  Proses pembuatan pengguna baru memicu pengiriman kueri SQL `INSERT` dari kontainer Nextcloud ke database MariaDB. Data akun disimpan di tabel `oc_users`, sedangkan pemetaan grup disimpan di tabel `oc_group_user`, dan kuota teralokasi dicatat di tabel `oc_preferences`.
  
  Mekanisme pembatasan kuota disk ini bersifat dinamis. Ketika pengguna melakukan pengunggahan berkas, Nextcloud akan menghitung akumulasi total kapasitas file biner yang terdaftar di database untuk user tersebut, lalu membandingkannya dengan limit kuota di tabel preferensi sebelum mengizinkan stream upload ke MinIO. Ini mengisolasi konsumsi resource penyimpanan antar divisi kerja secara granular.

  Kebijakan alokasi kuota disimpan di MariaDB menggunakan format byte representatif, yang dikonversi Nextcloud Core saat merender kapasitas disk di UI user reguler (contoh: kuota 10 GB disimpan sebagai `10737418240` bytes).

---

#### Skenario 2.4: Pengujian Login User Biasa
- **Tujuan Pengujian**: Memverifikasi pembatasan hak akses berbasis peran (*Role-Based Access Control*) bekerja dengan benar, di mana pengguna reguler (non-admin) dapat login ke dashboard personal mereka yang terisolasi dan tidak diizinkan mengakses menu pengaturan global.
- **Desain Skenario**: Melakukan pengujian login menggunakan akun pengguna reguler `engineer1` dan `finance1` secara bergantian pada tab browser terpisah.
- **Input Uji**: Username `engineer1` (password: `Eng!neer@2026Secure`) dan username `finance1` (password: `F1nance@2026Secure`).
- **Prosedur Langkah Pengujian**:
  Administrator melakukan logout dari akun admin, kemudian masuk ke halaman login Nextcloud. Administrator memasukkan username `engineer1` beserta passwordnya, lalu memeriksa tampilan menu navigasi. Administrator mengulangi proses login untuk akun `finance1`.
- **Output yang Diharapkan**: Login berhasil dilakukan. Dashboard personal pengguna reguler terbuka. Menu opsi administratif seperti *Users* dan *Administration Settings* **tidak ditampilkan** pada menu avatar pengguna biasa di pojok kanan atas.
- **Hasil Pengujian**: **SUKSES**
- **Analisis Rekayasa Teknis**:
  Berdasarkan tangkapan layar antarmuka pengguna pada gambar berikut:
  ![Bukti Skenario 2.4a - Login User Biasa engineer1](img/skenario2.4a.png)
  ![Bukti Skenario 2.4b - Login User Biasa finance1](img/skenario2.4b.png)
  Keberhasilan login reguler memvalidasi pembatasan akses keamanan internal Nextcloud Core. Saat pengguna login, kueri verifikasi kredensial dikirim ke database MariaDB. Setelah hash kata sandi terverifikasi cocok, Nextcloud membuat token sesi login baru dan menulisnya ke Redis cache.
  
  Sistem Nextcloud secara dinamis memeriksa tingkat peran pengguna (*user role*). Karena akun `engineer1` dan `finance1` tidak tergabung dalam grup sistem `admin` di database, Nextcloud memblokir rendering komponen administratif (*Users* and *Administration Settings*) di antarmuka grafis browser klien, menjamin prinsip keamanan hak istimewa terendah (*Principle of Least Privilege*). Folder skeleton default juga secara sukses dibuat di Object Storage backend MinIO khusus untuk ruang simpan data pribadi pengguna tersebut.

  Pemisahan ruang simpan ini dijamin oleh database MariaDB yang mencatat relasi kepemilikan file. User `finance1` hanya dapat membaca folder logikal miliknya sendiri, meniadakan celah kebocoran dokumen lintas divisi organisasi.
