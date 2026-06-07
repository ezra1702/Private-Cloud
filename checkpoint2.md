# checkpoint2.md - Laporan Implementasi & Konfigurasi Sistem
**Mata Kuliah**: Administrasi Sistem Server  
**Judul Proyek**: Rancang Bangun Platform Enterprise Private Cloud Storage Berbasis Nextcloud dengan Integrasi Object Storage MinIO, Caching Redis, Keamanan SSL/TLS, dan High Availability Terotomatisasi Menggunakan Ansible Playbook Berbasis Docker Container pada WSL2  
**Lingkungan Simulasi**: Windows Subsystem for Linux 2 (WSL2) - Ubuntu 22.04 LTS

---

## D. IMPLEMENTASI SISTEM

Bagian ini menjelaskan seluruh perintah Linux (Ubuntu 22.04 LTS pada WSL2) yang digunakan untuk melakukan instalasi prasyarat, konfigurasi otomatisasi, hingga pemeliharaan sistem, lengkap dengan penjelasannya.

### 1. Instalasi Docker Engine
Sebelum menjalankan kontainer, Docker Engine harus terpasang di WSL2. Proses instalasi dilakukan menggunakan paket manajer `apt`:
```bash
# 1. Update list package
sudo apt-get update

# 2. Install dependensi awal untuk HTTPS transport
sudo apt-get install -y ca-certificates curl gnupg

# 3. Tambahkan GPG key resmi dari Docker
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 4. Daftarkan repositori Docker ke Apt Sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Update index package & install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Pastikan Docker service berjalan
sudo service docker start
```

### 2. Instalasi Docker Compose
Pada Docker modern (v20.10+), Docker Compose telah terintegrasi sebagai plugin (`docker-compose-plugin`). Pengujian keberhasilan instalasi Docker Compose dilakukan dengan perintah:
```bash
docker compose version
```
*Penjelasan*: Perintah ini menampilkan versi Docker Compose yang aktif di sistem, memastikan modul command `docker compose` (bukan skrip Python `docker-compose` lama) siap digunakan.

### 3. Instalasi Ansible
Ansible Core dipasang di WSL2 untuk bertindak sebagai *Controller Node*:
```bash
# 1. Daftarkan PPA resmi Ansible
sudo apt-add-repository --yes --update ppa:ansible/ansible

# 2. Install Ansible
sudo apt-get install -y ansible
```
*Penjelasan*: Menambahkan repositori PPA resmi Ansible menjamin kita mendapatkan versi Ansible Core terbaru yang memiliki modul Docker kustom yang stabil.

### 4. Konfigurasi Inventory Ansible
Berkas inventori digunakan untuk mendefinisikan target host. Berkas ini ditaruh di `ansible/inventory.ini`:
```ini
[cloud_servers]
localhost ansible_connection=local
```
*Penjelasan*: `ansible_connection=local` mengarahkan Ansible untuk tidak menggunakan SSH melainkan langsung mengeksekusi modul-modul sistem ke filesystem WSL2 lokal kita sendiri.

### 5. Konfigurasi Playbook Ansible
Playbook utama ditulis di `ansible/site.yml` yang berisi deklarasi variabel dan daftar import tasks modular yang dipisahkan ke dalam berkas-berkas YAML di direktori `ansible/roles/`.

### 6. Deployment MariaDB
Database MariaDB dideploy sebagai container backend terpusat. Untuk mengujinya dan mematikan container secara mandiri jika diperlukan:
```bash
# Menjalankan kontainer database secara detached
docker run -d --name mariadb-db \
  --network cloud-network \
  -e MYSQL_ROOT_PASSWORD=adminrootpassword \
  -e MYSQL_DATABASE=nextcloud_db \
  -e MYSQL_USER=nextcloud_user \
  -e MYSQL_PASSWORD=nextcloudpassword \
  -v /opt/private-cloud/mariadb:/var/lib/mysql \
  mariadb:10.11
```

### 7. Deployment Nextcloud
Nextcloud dideploy sebanyak 2 replika server aplikasi (`nextcloud-app-1` dan `nextcloud-app-2`). Keduanya terhubung ke database terpusat, Redis, dan MinIO S3 API.

### 8. Deployment Load Balancer (HAProxy)
HAProxy dideploy untuk mengekspos port 80 dan 443. Kontainer memetakan konfigurasi sertifikat SSL `haproxy.pem` dan file konfigurasi `haproxy.cfg` ke dalam kontainer secara read-only (`ro`).

### 9. Konfigurasi Round Robin Load Balancing
Load balancing diatur pada konfigurasi backend di HAProxy (`haproxy.cfg`):
```haproxy
backend nextcloud_backend
    balance roundrobin
    cookie SERVERID insert indirect nocache
    server app1 nextcloud-app-1:80 check cookie app1
    server app2 nextcloud-app-2:80 check cookie app2
```
*Penjelasan*: `balance roundrobin` membagi request secara seimbang 1:1. `cookie SERVERID insert` menyisipkan cookie sesi agar user tidak terlempar log out saat trafik berganti backend kontainer.

### 10. Konfigurasi User Management
Otentikasi, hak akses grup (`Admin`, `Engineer`, `Finance`, `HRD Manager`, `Developer`, `Manager`), serta pembatasan kuota penyimpanan diatur langsung melalui panel administrasi Nextcloud di browser (`https://localhost/settings/users`). Nextcloud mengamankan password menggunakan enkripsi hash bcrypt/argon2 pada tabel `oc_users` di MariaDB.

### 11. Konfigurasi Persistent Storage Docker Volume
Untuk menjamin data tidak hilang saat kontainer mati, kita memetakan direktori host WSL2 ke direktori data kontainer:
- MariaDB: `/opt/private-cloud/mariadb` -> `/var/lib/mysql`
- Redis: `/opt/private-cloud/redis` -> `/data`
- MinIO: `/opt/private-cloud/minio` -> `/data`

### 12. Deployment Otomatis Menggunakan Ansible
Eksekusi playbook Ansible dijalankan dari folder `ansible/`:
```bash
ansible-playbook -i inventory.ini site.yml
```
*Penjelasan*: Perintah ini memicu seluruh jalannya instalasi Docker, SSL certificates generator, pembuatan folder proyek, pemindahan konfigurasi, dan kompilasi docker compose stack secara berurutan.

---

## E. FILE KONFIGURASI UTAMA

Berikut adalah berkas-berkas konfigurasi lengkap yang telah berhasil kita buat di dalam workspace proyek:

### 1. `ansible/ansible.cfg`
```ini
[defaults]
inventory = inventory.ini
host_key_checking = False
deprecation_warnings = False
stdout_callback = yaml
bin_ansible_callbacks = True
```

### 2. `ansible/inventory.ini`
```ini
[cloud_servers]
localhost ansible_connection=local
```

### 3. `ansible/site.yml`
```yaml
---
- name: Deploy Enterprise Private Cloud Storage Stack on WSL2
  hosts: cloud_servers
  become: yes
  vars:
    # Direktori kerja proyek di host WSL2
    project_root: /opt/private-cloud
    ssl_cert_dir: /opt/private-cloud/config/ssl
    
    # Kredensial Database
    db_root_password: adminrootpassword
    db_name: nextcloud_db
    db_user: nextcloud_user
    db_password: nextcloudpassword
    
    # MinIO S3 Credentials
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

### 4. `ansible/roles/common.yml`
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

### 5. `ansible/roles/docker.yml`
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

### 6. `ansible/roles/certificates.yml`
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

### 7. `ansible/roles/loadbalancer.yml`
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

### 8. `ansible/roles/nextcloud.yml`
```yaml
---
- name: 1. Salin berkas docker-compose.yml dari workspace ke host target
  copy:
    src: "{{ playbook_dir }}/../docker/docker-compose.yml"
    dest: "{{ project_root }}/docker/docker-compose.yml"
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

### 9. `docker/docker-compose.yml`
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

### 10. `config/haproxy/haproxy.cfg`
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

### 11. `config/nginx/nginx.conf`
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

    server {
        listen 80;
        server_name localhost;
        return 301 https://$host$request_uri;
    }

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

### 12. `config/prometheus/prometheus.yml`
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'haproxy'
    metrics_path: '/metrics'
    basic_auth:
      username: 'admin'
      password: 'adminstats'
    static_configs:
      - targets: ['haproxy-lb:1936']
```

---

## F. INPUT - PROCESS - OUTPUT (IPO DETAILED)

Berikut adalah skema interaksi input, pemrosesan logis sistem di tingkat container, dan output data yang dihasilkan dari platform storage ini.

### 1. Klien/Browser Access (HTTPS Handshake)
* **Input**: Request HTTP pengguna pada port 80 atau HTTPS pada port 443 via alamat URL `https://localhost`.
* **Process**:
  1. HAProxy menerima trafik pada port 80 dan mengalihkan request dengan header `redirect scheme https`.
  2. Browser melakukan TLS handshake dengan sertifikat self-signed `/usr/local/etc/haproxy/ssl/haproxy.pem` pada port 443.
  3. HAProxy melakukan SSL termination (dekripsi data) dan mendistribusikan trafik HTTP mentah secara Round Robin ke `nextcloud-app-1` atau `nextcloud-app-2`.
* **Output**: Halaman login Nextcloud yang aman ter-render pada browser klien.

### 2. Login User (Autentikasi Sesi)
* **Input**: Formulir login yang berisi `username` dan `password` dikirim oleh klien.
* **Process**:
  1. Replika kontainer Nextcloud menerima kredensial, melakukan hashing password, dan menembak database MariaDB terpusat (`mariadb-db:3306`) untuk validasi akun.
  2. Data sesi yang berhasil diverifikasi disimpan pada kontainer **Redis** (`redis-cache`) agar status login tetap sinkron.
  3. HAProxy menyisipkan cookie header `SERVERID` pada browser klien untuk memastikan persistensi sesi.
* **Output**: Dashboard Nextcloud terbuka dan pengguna berhasil masuk tanpa ter-logout tiba-tiba saat reload halaman.

### 3. Upload File (Unggah Dokumen)
* **Input**: Klien memilih berkas lokal (misal: dokumen PDF ukuran 5MB) dan menekan tombol *Upload* pada browser.
* **Process**:
  1. Nextcloud App server menerima aliran biner file (`binary stream`).
  2. Nextcloud melakukan transaksi penguncian file (`transactional file lock`) di **Redis** untuk mengamankan file selama proses penulisan.
  3. Nextcloud menulis informasi indeks berkas (metadata, tipe file, pemilik, kapasitas) ke database MariaDB.
  4. Nextcloud mengunggah data biner sesungguhnya menggunakan **API S3** ke bucket target di kontainer **MinIO** (`minio-storage:9000`).
  5. Redis melepaskan kunci transaksi file (`file lock release`).
* **Output**: Dokumen PDF muncul di list file browser klien dan tersimpan aman di disk volume host WSL2.

### 4. Download File (Unduh Dokumen)
* **Input**: Klien menekan tombol *Download* pada salah satu dokumen.
* **Process**:
  1. Request diterima oleh HAProxy dan diarahkan ke replika Nextcloud yang aktif.
  2. Nextcloud membaca metadata letak objek berkas dari database MariaDB.
  3. Nextcloud menarik objek berkas biner dari kontainer MinIO menggunakan API S3 secara real-time.
  4. Aliran biner file dikirim kembali melalui HTTP response ke HAProxy, yang kemudian mengenkripsi data tersebut via TLS dan meneruskannya ke browser klien.
* **Output**: Berkas terunduh secara utuh dan berhasil disimpan kembali pada komputer lokal host Windows.
