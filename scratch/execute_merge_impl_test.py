import os
import re

readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"
base_dir = "c:/Users/USER/Desktop/System Administator/Private-Cloud"

# Helper to read file content
def read_conf_file(rel_path):
    path = os.path.join(base_dir, rel_path)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return f"# File {rel_path} not found"

# 1. Read all configuration files
ansible_cfg = read_conf_file("ansible/ansible.cfg")
inventory_ini = read_conf_file("ansible/inventory.ini")
site_yml = read_conf_file("ansible/site.yml")
role_common = read_conf_file("ansible/roles/common.yml")
role_docker = read_conf_file("ansible/roles/docker.yml")
role_certs = read_conf_file("ansible/roles/certificates.yml")
role_db = read_conf_file("ansible/roles/database.yml")
role_redis = read_conf_file("ansible/roles/redis.yml")
role_minio = read_conf_file("ansible/roles/minio.yml")
role_lb = read_conf_file("ansible/roles/loadbalancer.yml")
role_nextcloud = read_conf_file("ansible/roles/nextcloud.yml")

docker_compose = read_conf_file("docker/docker-compose.yml")
haproxy_cfg = read_conf_file("config/haproxy/haproxy.cfg")
nginx_conf = read_conf_file("config/nginx/nginx.conf")
prometheus_yml = read_conf_file("config/prometheus/prometheus.yml")
datasource_yml = read_conf_file("config/grafana/provisioning/datasources/datasource.yml")

# 2. Generate directory tree
dir_tree = """Private-Cloud/
├── README.md
├── skenario.md
├── checkpoint3.md
├── ansible/
│   ├── ansible.cfg
│   ├── inventory.ini
│   ├── site.yml
│   └── roles/
│       ├── common.yml
│       ├── docker.yml
│       ├── certificates.yml
│       ├── database.yml
│       ├── redis.yml
│       ├── minio.yml
│       ├── loadbalancer.yml
│       └── nextcloud.yml
├── config/
│   ├── haproxy/
│   │   └── haproxy.cfg
│   ├── nginx/
│   │   └── nginx.conf
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── provisioning/
│           └── datasources/
│               └── datasource.yml
├── docker/
│   └── docker-compose.yml
└── img/
    ├── langkah1.1.png
    ├── langkah1.2.png
    └── ... (24 berkas gambar bukti pengujian)
"""

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate BAB I, BAB II, BAB III, BAB IV, BAB V, BAB VI
# We split the file content to replace BAB IV and BAB V completely.
# Let's locate the parts.
# Prefix: up to "## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI"
# Suffix: from "## BAB VI: PENUTUP (Kesimpulan dan Saran)" to the end

prefix_part = content.split("## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI")[0]
suffix_part = content.split("## BAB VI: PENUTUP (Kesimpulan dan Saran)")[1]

# Now let's extract the test steps from the current BAB V in README.md
# We split BAB V by "#### Pengujian Langkah Z: ..."
# Let's parse each step and extract its contents:
# - Tujuan Pengujian
# - Desain Langkah
# - Input Uji
# - Prosedur Langkah Pengujian
# - Output yang Diharapkan
# - Hasil Pengujian
# - Analisis Rekayasa Teknis
# - Images

# Let's search for matches in content:
step_headers = [
    "#### Pengujian Langkah 1: Pengujian Deployment Otomatis Menggunakan Ansible",
    "#### Pengujian Langkah 2: Pengujian Keaktifan Docker Container",
    "#### Pengujian Langkah 3: Uji Coba Persistensi Data (Data Persistence Check)",
    "#### Pengujian Langkah 4: Pengujian Akses Web Nextcloud (HTTPS)",
    "#### Pengujian Langkah 5: Pengujian Pembuatan/Login Administrator",
    "#### Pengujian Langkah 6: Pengujian Pembuatan User Baru dan Grup",
    "#### Pengujian Langkah 7: Pengujian Login User Biasa",
    "#### Pengujian Langkah 8: Pengujian Upload File",
    "#### Pengujian Langkah 9: Pengujian Berbagi Tautan Publik (External Share)",
    "#### Pengujian Langkah 10: Pengujian Hapus File",
    "#### Pengujian Langkah 11: Pengujian Load Balancing",
    "#### Pengujian Langkah 12: Pengujian Round Robin",
    "#### Pengujian Langkah 13: Pengujian Failover Container",
    "#### Pengujian Langkah 14: Pengujian High Availability (HA)",
    "#### Pengujian Langkah 15: Pengujian Recovery Layanan",
    "#### Pengujian Langkah 16: Pengujian Monitoring Sistem Menggunakan Prometheus",
    "#### Pengujian Langkah 17: Pengujian Monitoring Sistem Menggunakan Grafana"
]

steps_parsed = {}
for i in range(1, 18):
    curr_header = step_headers[i-1]
    next_header = step_headers[i] if i < 17 else "## BAB VI: PENUTUP"
    
    # Extract the block between curr_header and next_header
    pattern = re.compile(re.escape(curr_header) + r"(.*?)(?=" + re.escape(next_header) + r"|---)", re.DOTALL)
    match = pattern.search(content)
    if match:
        steps_parsed[i] = match.group(1).strip()
    else:
        # Fallback if there is a minor formatting issue (like no divider at the end)
        pattern = re.compile(re.escape(curr_header) + r"(.*)", re.DOTALL)
        match = pattern.search(content)
        if match:
            # slice until next_header
            steps_parsed[i] = match.group(1).split(next_header)[0].strip()
        else:
            print(f"Error parsing step {i}!")
            exit(1)

# Now, we construct the new merged BAB V
new_bab4 = f"""## BAB IV: STRUKTUR DIREKTORI & PENYIAPAN LINGKUNGAN

### 4.1 Struktur Direktori Proyek
Sebelum memulai otomatisasi, struktur direktori proyek pada workspace diatur sebagai berikut:
```text
{dir_tree}```

### 4.2 Persiapan Lingkungan Pra-Implementasi
Sebelum menerapkan 17 langkah utama, administrator sistem mempersiapkan lingkungan dasar (*hypervisor*) sebagai berikut:

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
"""

new_bab5 = """## BAB V: IMPLEMENTASI DAN PENGUJIAN SISTEM (17 LANGKAH DETAIL)

Seluruh langkah di bawah ini menggabungkan tahapan rekayasa konfigurasi, kode implementasi, serta prosedur dan hasil pengujian sistem secara lengkap.

### BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI
"""

# Let's insert the code configurations inside each step:
# Step 1
step1_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas-berkas konfigurasi Ansible utama untuk mengotomatisasi deployment stack:
  - **`ansible.cfg`**:
    ```ini
    {ansible_cfg}
    ```
  - **`inventory.ini`**:
    ```ini
    {inventory_ini}
    ```
  - **`site.yml`**:
    ```yaml
    {site_yml}
    ```
  - **`roles/common.yml`**:
    ```yaml
    {role_common}
    ```
"""

# Step 2
step2_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas orkestrator kontainer `docker-compose.yml` dan task otomatisasi instalasi Docker:
  - **`docker/docker-compose.yml`**:
    ```yaml
    {docker_compose}
    ```
  - **`roles/docker.yml`**:
    ```yaml
    {role_docker}
    ```
"""

# Step 3
step3_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah tugas penyiapan direktori basis data MariaDB dan Redis cache pada host target:
  - **`roles/database.yml`**:
    ```yaml
    {role_db}
    ```
  - **`roles/redis.yml`**:
    ```yaml
    {role_redis}
    ```
"""

# Step 4
step4_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas generator sertifikat SSL self-signed dan penyiapan load balancer HAProxy:
  - **`roles/certificates.yml`**:
    ```yaml
    {role_certs}
    ```
"""

# Step 5
step5_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah tugas otomatisasi penyediaan Nextcloud container dan setup trusted domains:
  - **`roles/nextcloud.yml`**:
    ```yaml
    {role_nextcloud}
    ```
"""

# Step 11
step11_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah tugas penyiapan load balancer dan konfigurasi utama `haproxy.cfg`:
  - **`roles/loadbalancer.yml`**:
    ```yaml
    {role_lb}
    ```
  - **`config/haproxy/haproxy.cfg`**:
    ```haproxy
    {haproxy_cfg}
    ```
"""

# Step 12
step12_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas konfigurasi Nginx alternatif (`nginx.conf`) untuk perbandingan load balancing:
  - **`config/nginx/nginx.conf`**:
    ```nginx
    {nginx_conf}
    ```
"""

# Step 16
step16_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas konfigurasi Prometheus (`prometheus.yml`) untuk target scraping:
  - **`config/prometheus/prometheus.yml`**:
    ```yaml
    {prometheus_yml}
    ```
"""

# Step 17
step17_code = f"""
- **Kode Konfigurasi & Implementasi**:
  Berikut adalah berkas konfigurasi data source Grafana secara deklaratif (`datasource.yml`):
  - **`config/grafana/provisioning/datasources/datasource.yml`**:
    ```yaml
    {datasource_yml}
    ```
"""

# We map each step to its content and its optional code configuration
step_codes = {
    1: step1_code,
    2: step2_code,
    3: step3_code,
    4: step4_code,
    5: step5_code,
    11: step11_code,
    12: step12_code,
    16: step16_code,
    17: step17_code
}

# Construct the output for BAB V step-by-step
for i in range(1, 18):
    if i == 4:
        new_bab5 += "\n### BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER\n\n"
    elif i == 11:
        new_bab5 += "\n### BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY\n\n"
        
    curr_header = step_headers[i-1]
    curr_body = steps_parsed[i]
    
    new_bab5 += curr_header + "\n"
    
    # Inject code configuration if exists
    if i in step_codes:
        new_bab5 += step_codes[i] + "\n"
        
    new_bab5 += curr_body + "\n\n---\n\n"

# Remove the trailing "---" divider from the last step
new_bab5 = new_bab5.strip()
if new_bab5.endswith("---"):
    new_bab5 = new_bab5[:-3].strip()

# Combine everything
final_document = prefix_part + new_bab4 + "\n\n" + new_bab5 + "\n\n\n## BAB VI: PENUTUP (Kesimpulan dan Saran)" + suffix_part

# Update the Table of Contents in final_document
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
  - [3.1 Topology Jaringan Virtual (Network Topology)](#31-topology-jaringan-virtual-network-topology)
  - [3.2 Desain Alur Sistem Login dan Upload (UML Sequence)](#32-desain-alur-sistem-login-dan-upload-uml-sequence)
  - [3.3 Diagram Alur Sistem Failover (HA State Machine)](#33-diagram-alur-sistem-failover-ha-state-machine)
  - [3.4 Diagram Input-Process-Output (IPO)](#34-diagram-input-process-output-ipo)
  - [3.5 Desain Manajemen User dan Kuota](#35-desain-manajemen-user-dan-kuota)
- [BAB IV: STRUKTUR DIREKTORI & PENYIAPAN LINGKUNGAN](#bab-iv-struktur-direktori--penyiapan-lingkungan)
  - [4.1 Struktur Direktori Proyek](#41-struktur-direktori-proyek)
  - [4.2 Persiapan Lingkungan Pra-Implementasi](#42-persiapan-lingkungan-pra-implementasi)
- [BAB V: IMPLEMENTASI DAN PENGUJIAN SISTEM (17 LANGKAH DETAIL)](#bab-v-implementasi-dan-pengujian-sistem-17-langkah-detail)
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
  - [6.1 Kesimpulan](#61-kesimpulan)
  - [6.2 Saran](#62-saran)
"""

pattern_toc = re.compile(r"## DAFTAR ISI.*?(## BAB I: PENDAHULUAN)", re.DOTALL)
final_document = pattern_toc.sub(new_toc + "\n\n\\1", final_document)

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(final_document)

print("Merging complete!")
