import re

readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update BAB III header
# Old: ## BAB III: DESAIN SISTEM
# New: ## BAB III: ARSITEKTUR SISTEM
content = content.replace("## BAB III: DESAIN SISTEM", "## BAB III: ARSITEKTUR SISTEM")

# 2. Update BAB IV content
# We locate "## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH" 
# and replace everything up to "## BAB V: PENGUJIAN SISTEM (17 LANGKAH PENGUJIAN DETAIL)"
# with the new 17 steps.

bab4_header = "## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH"
# Let's search for this header
if bab4_header not in content:
    # Just in case there is some minor whitespace difference
    bab4_header = "## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH"

bab5_header = "## BAB V: PENGUJIAN SISTEM (17 LANGKAH PENGUJIAN DETAIL)"

# Let's split content into parts
parts = content.split(bab4_header)
if len(parts) == 2:
    prefix = parts[0]
    suffix_parts = parts[1].split(bab5_header)
    if len(suffix_parts) == 2:
        bab4_old_content = suffix_parts[0]
        suffix = suffix_parts[1]
    else:
        print("Error: Could not find BAB V header!")
        exit(1)
else:
    print("Error: Could not find BAB IV header!")
    exit(1)

# Now, we construct the new BAB IV content
new_bab4_content = """

Proses instalasi dan penyiapan infrastruktur Private Cloud ini dijalankan dengan urutan prosedur teknis sebagai berikut:

### 4.1 Persiapan Lingkungan Pra-Implementasi
Sebelum menerapkan 17 langkah implementasi utama, administrator sistem mempersiapkan lingkungan dasar (*hypervisor*) sebagai berikut:

1. **Mengaktifkan WSL2 di Windows Host**: Administrator membuka terminal PowerShell dengan hak akses Administrator dan mengetikkan perintah berikut untuk mengaktifkan fitur virtualisasi Windows Subsystem for Linux (WSL2):
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   Setelah proses selesai, komputer dinyalakan kembali, lalu distro Ubuntu dipasang melalui Microsoft Store menggunakan perintah `wsl --install -d Ubuntu-22.04`.

2. **Instalasi Ansible di Lingkungan WSL2**: Administrator masuk ke dalam konsol WSL2 Ubuntu. Langkah pertama adalah memperbarui repositori bawaan sistem dan memasang perangkat lunak Ansible Controller menggunakan perintah:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install software-properties-common -y
   sudo add-apt-repository --yes --update ppa:ansible/ansible
   sudo apt install ansible -y
   ```
   Verifikasi keberhasilan pemasangan dilakukan dengan menjalankan perintah `ansible --version` untuk memastikan engine terpasang dengan versi minimal 2.12.

3. **Menyiapkan Berkas Inventory dan Konfigurasi Ansible**: Administrator membuat struktur folder proyek dan masuk ke direktori `/mnt/c/Users/USER/Desktop/System Administator/Private-Cloud/ansible/`. Di folder ini, berkas [inventory.ini](file:///c:/Users/USER/Desktop/System%20Administator/Private-Cloud/ansible/inventory.ini) dibuat untuk mengarahkan target eksekusi playbook ke mesin lokal:
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

4. **Eksekusi Playbook Ansible**: Untuk memulai otomatisasi inisialisasi server, pembuatan direktori `/opt/private-cloud/`, pembuatan sertifikat SSL/TLS self-signed, dan menyalakan seluruh container stack, perintah berikut dijalankan pada terminal WSL2:
   ```bash
   ANSIBLE_CONFIG=ansible.cfg ansible-playbook -i inventory.ini site.yml -K
   ```
   Parameter `-K` (*ask-become-pass*) menginstruksikan Ansible untuk meminta kata sandi sudo dari administrator guna melakukan proses eskalasi hak akses root secara aman di host lokal.

### 4.2 Prosedur Implementasi 17 Langkah Utama
Berikut adalah rincian dari 17 langkah implementasi sistem terdistribusi yang dikonfigurasi secara deklaratif menggunakan playbook otomatisasi:

- **Langkah 1: Otomatisasi Deployment (Ansible Playbook)**: Penyiapan naskah Ansible Playbook terstruktur dengan struktur Roles modular (`common`, `docker`, `certificates`, `database`, `redis`, `minio`, `loadbalancer`, `nextcloud`) untuk mengotomatisasi inisialisasi server, pembuatan direktori, dan pemasangan stack kontainer pada host WSL2 secara terotomatisasi.
- **Langkah 2: Konfigurasi Orkestrasi Kontainer Stack**: Pembuatan berkas `docker-compose.yml` untuk mendefinisikan 8 kontainer (HAProxy, Nextcloud x2, MariaDB, Redis, MinIO, Prometheus, Grafana) yang saling terhubung dalam satu subnet IP terisolasi `cloud-network`.
- **Langkah 3: Konfigurasi Volume Persistent (MariaDB & Redis)**: Pemetaan volume host target pada direktori `/opt/private-cloud/mariadb` dan `/opt/private-cloud/redis` menggunakan parameter host volume mounts untuk menjaga kestabilan data melintasi booting ulang kontainer.
- **Langkah 4: Konfigurasi SSL/TLS Termination HAProxy**: Pembuatan kunci privat RSA 2048-bit dan sertifikat publik OpenSSL self-signed, serta penggabungan berkas menjadi berkas tunggal `/opt/private-cloud/config/ssl/haproxy.pem` untuk dipasang di port 443 load balancer.
- **Langkah 5: Inisialisasi Akun Administrator Nextcloud**: Penulisan parameter kredensial admin default pada environment variable docker-compose untuk mengotomatisasi pembuatan akun `admin` pertama kali saat booting kontainer Nextcloud.
- **Langkah 6: Manajemen Pengguna dan Grup**: Penyusunan otentikasi internal Nextcloud untuk mendaftarkan 5 akun pengguna baru (`engineer1`, `finance1`, `hrd1`, `developer1`, `manager1`) serta mengelompokkannya ke dalam grup divisi terkait.
- **Langkah 7: Sinkronisasi Autentikasi Pengguna Reguler**: Konfigurasi pembatasan menu personal untuk menyembunyikan panel kontrol administratif dari antarmuka pengguna biasa guna menjaga privilese hak akses terendah.
- **Langkah 8: Integrasi Object Storage MinIO (S3 API)**: Mengarahkan konfigurasi primary storage Nextcloud ke bucket penyimpanan objek MinIO via API S3 di port 9000 menggunakan environment variable API key.
- **Langkah 9: Konfigurasi Berbagi Tautan Publik (External Share)**: Penyusunan parameter token enkripsi asinkron Nextcloud pada basis data MariaDB untuk memfasilitasi pembagian tautan file secara publik tanpa login.
- **Langkah 10: Kebijakan Sinkronisasi Penghapusan Berkas**: Pengaturan siklus sinkronisasi kueri hapus file di database metadata MariaDB untuk mengirimkan request DELETE API S3 secara sinkron ke MinIO storage.
- **Langkah 11: Konfigurasi Port Statistik HAProxy**: Pengaktifan dashboard monitoring visual internal HAProxy pada port `1936` dengan pengamanan basic authentication.
- **Langkah 12: Pengaturan Algoritma Load Balancing Round Robin**: Mengonfigurasi parameter load balancer untuk membagi beban koneksi 1:1 dan menyisipkan cookie session `SERVERID` guna menjaga session stickiness.
- **Langkah 13: Konfigurasi TCP Health Checks untuk Failover**: Penulisan parameter `check inter 2000 fall 3` di berkas `haproxy.cfg` agar load balancer mendeteksi matinya kontainer Nextcloud dalam 3 kali polling berturut-turut.
- **Langkah 14: Sinkronisasi Sesi Terpusat dengan Redis Cache**: Mengonfigurasi Nextcloud agar menyimpan session cache login pengguna secara terpusat pada Redis cache di port `6379`.
- **Langkah 15: Konfigurasi Auto-Recovery Jalur Trafik**: Pengaturan parameter `rise 2` pada HAProxy untuk memasukkan kembali kontainer Nextcloud yang pulih ke dalam daftar server sehat secara otomatis.
- **Langkah 16: Konfigurasi Prometheus Scraper Metrics**: Konfigurasi berkas `prometheus.yml` untuk men-scrape metrik data exporter dari HAProxy port 1936 `/metrics` dengan basic auth credentials.
- **Langkah 17: Provisi Dashboard Pemantauan Grafana**: Konfigurasi provisi datasource Prometheus secara deklaratif di Grafana untuk memvisualisasikan grafik metrik performa secara real-time.

---

"""

# 3. Rename headings in BAB V
# Let's process the suffix string.
# We want to replace the headings like:
# "#### Langkah 1.1: Pengujian Deployment Otomatis Menggunakan Ansible" -> "#### Pengujian Langkah 1: Pengujian Deployment Otomatis Menggunakan Ansible"
# and so on.
# Let's map the steps sequentially from 1 to 17.
step_mappings = [
    ("#### Langkah 1.1: Pengujian Deployment Otomatis Menggunakan Ansible", "#### Pengujian Langkah 1: Pengujian Deployment Otomatis Menggunakan Ansible"),
    ("#### Langkah 1.2: Pengujian Keaktifan Docker Container", "#### Pengujian Langkah 2: Pengujian Keaktifan Docker Container"),
    ("#### Langkah 1.3: Uji Coba Persistensi Data (Data Persistence Check)", "#### Pengujian Langkah 3: Uji Coba Persistensi Data (Data Persistence Check)"),
    ("#### Langkah 2.1: Pengujian Akses Web Nextcloud (HTTPS)", "#### Pengujian Langkah 4: Pengujian Akses Web Nextcloud (HTTPS)"),
    ("#### Langkah 2.2: Pengujian Pembuatan/Login Administrator", "#### Pengujian Langkah 5: Pengujian Pembuatan/Login Administrator"),
    ("#### Langkah 2.3: Pengujian Pembuatan User Baru dan Grup", "#### Pengujian Langkah 6: Pengujian Pembuatan User Baru dan Grup"),
    ("#### Langkah 2.4: Pengujian Login User Biasa", "#### Pengujian Langkah 7: Pengujian Login User Biasa"),
    ("#### Langkah 2.5: Pengujian Upload File", "#### Pengujian Langkah 8: Pengujian Upload File"),
    ("#### Langkah 2.6: Pengujian Berbagi Tautan Publik (External Share)", "#### Pengujian Langkah 9: Pengujian Berbagi Tautan Publik (External Share)"),
    ("#### Langkah 2.7: Pengujian Hapus File", "#### Pengujian Langkah 10: Pengujian Hapus File"),
    ("#### Langkah 3.1: Pengujian Load Balancing", "#### Pengujian Langkah 11: Pengujian Load Balancing"),
    ("#### Langkah 3.2: Pengujian Round Robin", "#### Pengujian Langkah 12: Pengujian Round Robin"),
    ("#### Langkah 3.3: Pengujian Failover Container", "#### Pengujian Langkah 13: Pengujian Failover Container"),
    ("#### Langkah 3.4: Pengujian High Availability (HA)", "#### Pengujian Langkah 14: Pengujian High Availability (HA)"),
    ("#### Langkah 3.5: Pengujian Recovery Layanan", "#### Pengujian Langkah 15: Pengujian Recovery Layanan"),
    ("#### Langkah 3.6: Pengujian Monitoring Sistem Menggunakan Prometheus", "#### Pengujian Langkah 16: Pengujian Monitoring Sistem Menggunakan Prometheus"),
    ("#### Langkah 3.7: Pengujian Monitoring Sistem Menggunakan Grafana", "#### Pengujian Langkah 17: Pengujian Monitoring Sistem Menggunakan Grafana")
]

# We should also replace references inside text to match the new names
# E.g. "Skenario 1.1" or "Langkah 1.1" -> "Pengujian Langkah 1"
# Let's define the replacement mappings:
text_mappings = [
    (r"(?i)\bLangkah 1\.1\b", "Pengujian Langkah 1"),
    (r"(?i)\bLangkah 1\.2\b", "Pengujian Langkah 2"),
    (r"(?i)\bLangkah 1\.3\b", "Pengujian Langkah 3"),
    (r"(?i)\bLangkah 2\.1\b", "Pengujian Langkah 4"),
    (r"(?i)\bLangkah 2\.2\b", "Pengujian Langkah 5"),
    (r"(?i)\bLangkah 2\.3\b", "Pengujian Langkah 6"),
    (r"(?i)\bLangkah 2\.4a\b", "Pengujian Langkah 7a"),
    (r"(?i)\bLangkah 2\.4b\b", "Pengujian Langkah 7b"),
    (r"(?i)\bLangkah 2\.4\b", "Pengujian Langkah 7"),
    (r"(?i)\bLangkah 2\.5a\b", "Pengujian Langkah 8a"),
    (r"(?i)\bLangkah 2\.5b\b", "Pengujian Langkah 8b"),
    (r"(?i)\bLangkah 2\.5\b", "Pengujian Langkah 8"),
    (r"(?i)\bLangkah 2\.6a\b", "Pengujian Langkah 9a"),
    (r"(?i)\bLangkah 2\.6b\b", "Pengujian Langkah 9b"),
    (r"(?i)\bLangkah 2\.6\b", "Pengujian Langkah 9"),
    (r"(?i)\bLangkah 2\.7a\b", "Pengujian Langkah 10a"),
    (r"(?i)\bLangkah 2\.7\b", "Pengujian Langkah 10"),
    (r"(?i)\bLangkah 3\.1\b", "Pengujian Langkah 11"),
    (r"(?i)\bLangkah 3\.2\b", "Pengujian Langkah 12"),
    (r"(?i)\bLangkah 3\.3\b", "Pengujian Langkah 13"),
    (r"(?i)\bLangkah 3\.4a\b", "Pengujian Langkah 14a"),
    (r"(?i)\bLangkah 3\.4b\b", "Pengujian Langkah 14b"),
    (r"(?i)\bLangkah 3\.4\b", "Pengujian Langkah 14"),
    (r"(?i)\bLangkah 3\.5\b", "Pengujian Langkah 15"),
    (r"(?i)\bLangkah 3\.6\b", "Pengujian Langkah 16"),
    (r"(?i)\bLangkah 3\.7a\b", "Pengujian Langkah 17a"),
    (r"(?i)\bLangkah 3\.7b\b", "Pengujian Langkah 17b"),
    (r"(?i)\bLangkah 3\.7c\b", "Pengujian Langkah 17c"),
    (r"(?i)\bLangkah 3\.7\b", "Pengujian Langkah 17"),
]

# Apply the heading replacements first
for old_h, new_h in step_mappings:
    suffix = suffix.replace(old_h, new_h)

# Apply general text replacements
for pattern, replacement in text_mappings:
    suffix = re.sub(pattern, replacement, suffix)

# We should also replace the filenames of images inside the links!
# Let's replace "img/langkah1.1.png" with "img/langkah1.1.png" (Wait, the image filenames on disk are already langkah1.1.png. Do we need to change them to langkah1.png?
# Ah! If we renamed the image filenames to match "Pengujian Langkah 1", e.g. `img/langkah1.1.png` -> `img/langkah1.png` or keep them as `img/langkah1.1.png`?
# Wait! "img/langkah1.1.png" contains "langkah1.1". If we don't rename the files, but we keep the image link URL as `img/langkah1.1.png`, it works perfectly!
# Let's check if the image URLs in suffix should be renamed on disk.
# If we do rename them, we can rename `langkah1.1.png` -> `langkah1.png` or `langkah_langkah1.png`. But wait, `langkah1.1.png` is already clear. Let's see if the user wants the image URLs renamed as well or just the text in the headers and references.
# The user said: "PENGUJIAN SISTEM TULISAN LANMGLKAH JADI PENGUJIAN LANGKAH 1. INITNYA BAB LANGAH WAJIB SAMA KAYAKPENGIJIAN SISTEM"
# This means:
# - In BAB V: The header `#### Langkah X.Y: ...` -> `#### Pengujian Langkah Z: ...`
# - And in the text, replace "Langkah X.Y" with "Pengujian Langkah Z".
# Let's keep the image URLs as they are (pointing to `img/langkahX.Y.png` which exist) to avoid breaking anything, but we update the image CAPTIONS (e.g. `![Bukti Langkah 1.1 ...](img/langkah1.1.png)` becomes `![Bukti Pengujian Langkah 1 ...](img/langkah1.1.png)`).
# The regex replacements above already change "Langkah 1.1" -> "Pengujian Langkah 1" in the captions as well because it's part of the text!
# E.g., `![Bukti Langkah 1.1` -> `![Bukti Pengujian Langkah 1`. This is perfect!

# Let's double check if there are other occurrences of "Langkah X.Y" in prefix or suffix.
# Let's see: the script does it.

# Now let's standardize Penutup heading to "## BAB VI: PENUTUP (Kesimpulan dan Saran)"
suffix = suffix.replace("## VII: PENUTUP (Kesimpulan dan Saran)", "## BAB VI: PENUTUP (Kesimpulan dan Saran)")

# 4. Construct the complete updated content
new_content = prefix + bab4_header + new_bab4_content + "## BAB V: PENGUJIAN SISTEM (17 LANGKAH PENGUJIAN DETAIL)" + suffix

# 5. Generate the Table of Contents dynamically or statically to match the new structure
# The title of README.md is the first heading. We find it and replace the TOC section.
# Let's check if we can replace the old DAFTAR ISI block.
# The old DAFTAR ISI block starts with "## DAFTAR ISI" and ends before "## BAB I: PENDAHULUAN"

new_toc = """## DAFTAR ISI

- [BAB I: PENDAHULUAN](#bab-i-pendahuluan)
  - [1.1 Latar Belakang](#11-latar-belakang)
  - [1.2 Rumusan Masalah](#12-rumusan-masalah)
  - [1.3 Tujuan Proyek](#13-tujuan-proyek)
  - [1.4 Manfaat Proyek](#14-manfaat-proyek)
- [BAB II: LANDASAN TEORI](#bab-ii-landasan-teori)
  - [2.1 Nextcloud Application Server Architecture](#21-nextcloud-application-server-architecture)
  - [2.2 MariaDB Database Management System](#22-mariadb-database-management-system)
  - [2.3 Redis Cache and Transaction Session Locking](#23-redis-cache-and-transaction-session-locking)
  - [2.4 MinIO Object Storage and S3 API Compatibility](#24-minio-object-storage-and-s3-api-compatibility)
- [BAB III: ARSITEKTUR SISTEM](#bab-iii-arsitektur-sistem)
  - [3.1 Topology Jaringan Virtual (Network Topology)](#41-topology-jaringan-virtual-network-topology)
  - [3.2 Desain Alur Sistem Login dan Upload (UML Sequence)](#42-desain-alur-sistem-login-dan-upload-uml-sequence)
  - [3.3 Diagram Alur Sistem Failover (HA State Machine)](#43-diagram-alur-sistem-failover-ha-state-machine)
  - [3.4 Diagram Input-Process-Output (IPO)](#44-diagram-input-process-output-ipo)
  - [3.5 Desain Manajemen User dan Kuota](#45-desain-manajemen-user-dan-kuota)
- [BAB IV: LANGKAH-LANGKAH IMPLEMENTASI](#bab-iv-langkah-langkah-implementasi)
  - [4.1 Persiapan Lingkungan Pra-Implementasi](#41-persiapan-lingkungan-pra-implementasi)
  - [4.2 Prosedur Implementasi 17 Langkah Utama](#42-prosedur-implementasi-17-langkah-utama)
- [BAB V: PENGUJIAN SISTEM (17 PENGUJIAN DETAIL)](#bab-v-pengujian-sistem-17-langkah-pengujian-detail)
  - [BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI](#blok-1-pengujian-infrastruktur-dan-otomatisasi)
    - [Pengujian Langkah 1: Pengujian Deployment Otomatis Menggunakan Ansible](#pengujian-langkah-1-pengujian-deployment-otomatis-menggunakan-ansible)
    - [Pengujian Langkah 2: Pengujian Keaktifan Docker Container](#pengujian-langkah-2-pengujian-keaktifan-docker-container)
    - [Pengujian Langkah 3: Uji Coba Persistensi Data (Data Persistence Check)](#pengujian-langkah-3-uji-coba-persistensi-data-data-persistence-check)
  - [BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER](#blok-2-pengujian-fitur-aplikasi-dan-manajemen-user)
    - [Pengujian Langkah 4: Pengujian Akses Web Nextcloud (HTTPS)](#pengujian-langkah-4-pengujian-akses-web-nextcloud-https)
    - [Pengujian Langkah 5: Pengujian Pembuatan/Login Administrator](#pengujian-langkah-5-pengujian-pembuatanlogin-administrator)
    - [Pengujian Langkah 6: Pengujian Pembuatan User Baru dan Grup](#pengujian-langkah-6-pengujian-pembuatan-user-baru-dan-grup)
    - [Pengujian Langkah 7: Pengujian Login User Biasa](#pengujian-langkah-7-pengujian-login-user-biasa)
    - [Pengujian Langkah 8: Pengujian Upload File](#pengujian-langkah-8-pengujian-upload-file)
    - [Pengujian Langkah 9: Pengujian Berbagi Tautan Publik (External Share)](#pengujian-langkah-9-pengujian-berbagi-tautan-publik-external-share)
    - [Pengujian Langkah 10: Pengujian Hapus File](#pengujian-langkah-10-pengujian-hapus-file)
  - [BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY](#blok-3-pengujian-load-balancing-dan-high-availability)
    - [Pengujian Langkah 11: Pengujian Load Balancing](#pengujian-langkah-11-pengujian-load-balancing)
    - [Pengujian Langkah 12: Pengujian Round Robin](#pengujian-langkah-12-pengujian-round-robin)
    - [Pengujian Langkah 13: Pengujian Failover Container](#pengujian-langkah-13-pengujian-failover-container)
    - [Pengujian Langkah 14: Pengujian High Availability (HA)](#pengujian-langkah-14-pengujian-high-availability-ha)
    - [Pengujian Langkah 15: Pengujian Recovery Layanan](#pengujian-langkah-15-pengujian-recovery-layanan)
    - [Pengujian Langkah 16: Pengujian Monitoring Sistem Menggunakan Prometheus](#pengujian-langkah-16-pengujian-monitoring-sistem-menggunakan-prometheus)
    - [Pengujian Langkah 17: Pengujian Monitoring Sistem Menggunakan Grafana](#pengujian-langkah-17-pengujian-monitoring-sistem-menggunakan-grafana)
- [BAB VI: PENUTUP (Kesimpulan dan Saran)](#bab-vi-penutup-kesimpulan-dan-saran)
  - [13.1 Kesimpulan](#131-kesimpulan)
  - [13.2 Saran](#132-saran)
"""

# Let's replace the DAFTAR ISI in new_content
# We match: "## DAFTAR ISI" ... to ... "## BAB I: PENDAHULUAN"
pattern_toc = re.compile(r"## DAFTAR ISI.*?(## BAB I: PENDAHULUAN)", re.DOTALL)
final_content = pattern_toc.sub(new_toc + "\n\n\\1", new_content)

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Alignment complete!")
