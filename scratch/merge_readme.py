import re

# Read skenario.md
with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/skenario.md", "r", encoding="utf-8") as f:
    skenario_content = f.read()

# Find ## BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI and keep everything from there
match = re.search(r"## BLOK 1:.*", skenario_content, re.DOTALL)
if match:
    skenario_body = match.group(0)
else:
    skenario_body = skenario_content

# Read README.md
with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

# Replace the old topics list section in README.md
old_topics = """### **Integrasi Topik Administrasi Sistem Server:**
Sistem ini dibangun secara komprehensif dengan menggabungkan 5 topik utama perkuliahan Administrasi Sistem Server:
1. **Containerization & Orchestration (Docker)**: Mengemas semua modul infrastruktur ke dalam container terisolasi yang diorkestrasi secara utuh menggunakan *Docker Compose*, menjamin portabilitas dan konsistensi sistem.
2. **Secure Web Server & SSL Termination (HAProxy)**: Menggunakan HAProxy sebagai pintu gerbang utama yang bertindak sebagai reverse proxy untuk melakukan enkripsi HTTPS SSL/TLS secara terpusat (*SSL Termination*), serta mengalihkan semua lalu lintas HTTP (port 80) secara otomatis ke HTTPS (port 443).
3. **Infrastructure as Code (Ansible)**: Mengotomatisasi seluruh siklus deployment dari mulai inisialisasi direktori, instalasi Docker Engine, generator sertifikat SSL self-signed, hingga penyalinan file konfigurasi menggunakan *Ansible Playbook* modular berbasis *Roles*.
4. **High Availability & Stateless Storage (HAProxy, Redis, MinIO)**: Mengimplementasikan pembagian beban trafik 1:1 (*Round Robin*), mempertahankan sesi login pengguna menggunakan *Session Cookie* (cookie persistence), menggunakan Redis sebagai *transactional lock* database sesi, serta mengalihkan penyimpanan data Nextcloud menjadi *stateless* menggunakan API S3 MinIO.
5. **Infrastruktur Monitoring (Prometheus & Grafana)**: Memantau keaktifan kontainer dan metrik kinerja menggunakan server Prometheus yang secara periodik men-scrape metrik internal dari HAProxy (via *Prometheus-exporter*) dan divisualisasikan dalam bentuk grafik interaktif di Grafana."""

new_topics = """### **Integrasi Topik Administrasi Sistem Server (Kurikulum):**
Sistem ini dibangun secara komprehensif dengan mengimplementasikan dan menggabungkan **6 dari 8 topik utama** perkuliahan Administrasi Sistem Server:

1. **Topik 2: Manajemen User**: Mengatur otentikasi internal Nextcloud, pembagian grup terisolasi (`Admin`, `Engineer`, `Finance`, `HRD Manager`, `Developer`, `Manager`), pengaturan hak akses data personal, serta kebijakan kuota kapasitas disk penyimpanan (5 GB - 25 GB) secara granular.
2. **Topik 3: Web Server**: Menggunakan HAProxy sebagai secure gateway dengan konfigurasi SSL/TLS *Termination* di port 443 dan mengalihkan (*redirect*) otomatis trafik HTTP port 80 ke HTTPS. Layanan Nextcloud di backend berjalan di atas web server Apache (port 80 internal).
3. **Topik 4: Virtualisasi**: Menggunakan virtualisasi Windows Subsystem for Linux 2 (WSL2) dengan distro Ubuntu 22.04 LTS sebagai infrastruktur virtual dasar (*hypervisor*) yang menjalankan docker engine dan server Ansible controller.
4. **Topik 5: Docker – Kontainer**: Orkestrasi multi-kontainer terisolasi (8 kontainer: HAProxy, Nextcloud x2, MariaDB, Redis, MinIO, Prometheus, Grafana) yang saling terhubung dalam satu virtual bridge network `cloud-network`.
5. **Topik 7: Infrastructure as Code (Terraform dan Ansible)**: Mengotomatisasi siklus hidup kontainer, pembuatan SSL, inisialisasi volume directori host target, dan penyalinan file konfigurasi menggunakan **Ansible Playbook** terstruktur dengan Ansible Roles.
6. **Topik 8: High Availability**: Mengimplementasikan pembagian beban trafik 1:1 (*Round Robin*), *session stickiness* menggunakan cookie `SERVERID`, mekanisme failover otomatis jika salah satu kontainer aplikasi mati, serta arsitektur server aplikasi *stateless* terpusat pada MinIO S3 API dan Redis cache."""

readme_content = readme_content.replace(old_topics, new_topics)

# Replace Section 6 "PENGUJIAN SISTEM" in README.md
# The section is between "## 6. PENGUJIAN SISTEM" and "## 7. ANALISIS SISTEM"
# We can use regex to find and replace everything between those two headers
pattern = r"(## 6\. PENGUJIAN SISTEM\n\n).*?(\n\n## 7\. ANALISIS SISTEM)"

# To avoid escape character issues in replacement text, we will use a lambda function in re.sub
modified_readme = re.sub(pattern, lambda m: m.group(1) + "Berikut adalah rincian dari seluruh skenario pengujian fungsionalitas, keamanan, ketersediaan tinggi (High Availability), dan monitoring sistem secara terperinci beserta langkah-langkah uji dan analisis gambarnya:\n\n" + skenario_body + m.group(2), readme_content, flags=re.DOTALL)

with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "w", encoding="utf-8") as f:
    f.write(modified_readme)

print("Merged successfully!")
