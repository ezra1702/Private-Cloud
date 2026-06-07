# Dokumentasi Otomatisasi Deployment (ansible.md)
**Mata Kuliah**: Administrasi Sistem Server  
**Dokumen**: Panduan Konfigurasi, Struktur, dan Eksekusi Ansible Playbook

---

## 1. Pendahuluan
Ansible digunakan sebagai alat otomatisasi utama (*Infrastructure as Code* / IaC) untuk mempercepat deployment platform Enterprise Private Cloud Storage di lingkungan WSL2 (Ubuntu 22.04 LTS). Ansible bekerja secara *agentless* (tanpa memerlukan agen di server target) dan bersifat *idempotent* (tugas yang sama dapat dijalankan berkali-kali tanpa mengubah hasil akhir jika kondisi sistem sudah sesuai).

Dalam proyek ini, Ansible dikonfigurasi untuk berjalan secara lokal pada WSL2 (`localhost` via `ansible_connection=local`). Hal ini meminimalkan overhead administrasi dan membebaskan mahasiswa dari konfigurasi SSH key yang rumit di lokal.

---

## 2. Struktur Berkas Ansible
Berikut adalah struktur folder dan berkas otomatisasi yang telah kita bangun pada direktori `ansible/`:

```text
ansible/
├── ansible.cfg               # Berkas konfigurasi global Ansible
├── inventory.ini             # Daftar host target (localhost WSL2)
├── site.yml                  # Playbook utama (entry point)
└── roles/                    # Berkas tugas modular (hybrid role-file)
    ├── common.yml            # Paket dasar & dependensi sistem
    ├── docker.yml            # Instalasi Docker & Docker Compose
    ├── certificates.yml      # Pembuatan sertifikat SSL/TLS self-signed
    ├── database.yml          # Direktori penyimpanan MariaDB
    ├── redis.yml             # Direktori penyimpanan Redis
    ├── minio.yml             # Direktori penyimpanan MinIO
    ├── loadbalancer.yml      # Setup konfigurasi HAProxy/Nginx
    └── nextcloud.yml         # Salin compose & jalankan container stack
```

---

## 3. Penjelasan Detail Setiap Berkas Konfigurasi

### A. `ansible.cfg`
Berkas ini mengatur perilaku default dari eksekusi Ansible.
```ini
[defaults]
inventory = inventory.ini
host_key_checking = False
deprecation_warnings = False
stdout_callback = yaml
bin_ansible_callbacks = True
```
* **`inventory = inventory.ini`**: Memberitahu Ansible untuk membaca daftar host target dari file `inventory.ini` secara otomatis.
* **`host_key_checking = False`**: Mematikan verifikasi sidik jari key SSH saat terhubung ke server (sangat berguna untuk otomatisasi agar tidak terhenti oleh konfirmasi interaktif).
* **`stdout_callback = yaml`**: Mengubah format output log terminal Ansible menjadi format YAML yang jauh lebih mudah dibaca daripada JSON default.

### B. `inventory.ini`
Mendefinisikan daftar server target dan metode koneksinya.
```ini
[cloud_servers]
localhost ansible_connection=local
```
* **`[cloud_servers]`**: Nama grup server.
* **`localhost`**: Alamat target.
* **`ansible_connection=local`**: Memberitahu Ansible untuk mengeksekusi perintah langsung di mesin lokal (WSL2 Ubuntu) menggunakan terminal lokal, alih-alih mencoba terhubung via protokol SSH.

### C. `site.yml`
Ini adalah berkas *Playbook* utama yang mengoordinasikan seluruh proses deployment secara berurutan.
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
    ...
```
* **`become: yes`**: Meminta Ansible untuk menjalankan tugas dengan hak akses superuser (`root` / `sudo`) karena ada instalasi paket dan modifikasi folder sistem `/opt`.
* **`vars`**: Mendefinisikan variabel global seperti root folder proyek `/opt/private-cloud` dan password database agar mudah dikelola dari satu tempat.
* **`import_tasks`**: Memanggil berkas tugas parsial secara berurutan (*serial execution*).

---

## 4. Penjelasan Tugas Modular (Sub-Playbook di `roles/`)

### 1. `roles/common.yml`
Fokus pada pembaruan sistem dan pemasangan utilitas dasar.
* **Apt Update**: Memperbarui indeks paket manager lokal.
* **Install Packages**: Menginstal paket dasar (`curl` untuk download, `gnupg` untuk manajemen key, `ca-certificates` untuk HTTPS handshaking, dan `openssl` untuk keamanan).
* **Create Project Dirs**: Membuat folder root `/opt/private-cloud` dan folder config di target.

### 2. `roles/docker.yml`
Melakukan instalasi otomatis Docker Engine tanpa interaksi manual.
* **Keyring Setup & Download Key**: Mengunduh GPG Key resmi Docker ke `/etc/apt/keyrings/docker.asc` untuk validasi keamanan paket.
* **Add Apt Repository**: Mendaftarkan repositori resmi Docker di berkas sumber APT agar paket docker versi terbaru dapat diunduh.
* **Install Docker CE**: Memasang Docker Engine, Docker CLI, dan plugin Docker Compose.
* **Start Service**: Memastikan sistem Docker aktif (`started`) dan diatur untuk otomatis berjalan setelah boot (`enabled`).

### 3. `roles/certificates.yml`
Mengotomatisasi pembuatan sertifikat keamanan SSL/TLS lokal.
* **Openssl Req Command**: Membuat Private Key (`private.key`) dan Certificate (`certificate.crt`) berdurasi 365 hari. Subjek sertifikat diatur ke `localhost` agar cocok digunakan pada browser lokal.
* **Cat Command**: HAProxy membutuhkan satu file PEM gabungan. Tugas ini menggabungkan isi berkas private key dan crt ke dalam berkas `haproxy.pem`.
* **File Permissions**: Membatasi hak akses berkas `haproxy.pem` menjadi `0600` (hanya dapat dibaca oleh root) untuk alasan keamanan.

### 4. `roles/database.yml`, `roles/redis.yml`, `roles/minio.yml`
* Membuat folder penyimpanan persisten di host target:
  - `/opt/private-cloud/mariadb`
  - `/opt/private-cloud/redis`
  - `/opt/private-cloud/minio`
* Folder diatur kepemilikannya ke ID user `999` (id internal database MariaDB dan Redis) agar kontainer memiliki hak tulis/baca ke host OS.

### 5. `roles/loadbalancer.yml`
* Membuat direktori `/opt/private-cloud/config/haproxy` dan `/opt/private-cloud/config/nginx`.
* Menyalin berkas konfigurasi load balancer (`haproxy.cfg` dan `nginx.conf`) dari workspace proyek lokal Anda ke direktori target di host.

### 6. `roles/nextcloud.yml`
* Menyalin berkas `docker-compose.yml` dari workspace ke `/opt/private-cloud/docker/docker-compose.yml`.
* Menjalankan perintah Docker: `docker compose -f /opt/private-cloud/docker/docker-compose.yml up -d` untuk memicu pengunduhan image kontainer dan menjalankannya di latar belakang.

---

## 5. Perintah Linux untuk Eksekusi dan Pengujian

Sebelum mengeksekusi, pastikan Anda berada di direktori `ansible` pada terminal WSL2 Anda:
```bash
cd "/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/ansible"
```

### A. Uji Sintaks (Syntax Check)
Gunakan perintah berikut untuk memastikan tidak ada kesalahan indentasi atau sintaksis pada seluruh file YAML:
```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
```
*Output yang diharapkan:*
```text
playbook: site.yml
```

### B. Uji Koneksi Ping (Dry-Run Ping)
Memastikan Ansible dapat mengenali dan menjangkau host target (localhost):
```bash
ansible cloud_servers -i inventory.ini -m ping
```
*Output yang diharapkan:*
```text
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### C. Eksekusi Playbook Secara Penuh (Run Playbook)
Untuk menjalankan deployment otomatis secara keseluruhan, jalankan perintah:
```bash
ansible-playbook -i inventory.ini site.yml
```
* Penjelasan argumen:
  - `-i inventory.ini`: Menggunakan file inventori lokal.
  - `site.yml`: Berkas instruksi utama yang dijalankan.
* Selama proses eksekusi, Ansible akan menampilkan status `ok` (jika tidak ada perubahan yang perlu dilakukan), `changed` (jika Ansible melakukan perubahan sistem), atau `failed` (jika ada task yang gagal).
