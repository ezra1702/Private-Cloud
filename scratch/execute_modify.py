import os

readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Locate BAB III
# "## BAB III: ANALISIS KEBUTUHAN SISTEM" is at line index 76 (0-based)
# "## BAB IV: DESAIN SISTEM" is at line index 113 (0-based)
# We delete indices 76 to 110 inclusive (which leaves the separator '---' at index 111, now shifting up)
bab3_start = -1
bab4_start = -1
for idx, line in enumerate(lines):
    if line.startswith("## BAB III:"):
        bab3_start = idx
    if line.startswith("## BAB IV:"):
        bab4_start = idx

print(f"BAB III index: {bab3_start}, BAB IV index: {bab4_start}")

# Slice out BAB III (excluding the separator line index 111, which is bab4_start - 2)
# The lines to keep are lines[:bab3_start] + lines[bab4_start - 2:]
# Let's double check if lines[bab4_start - 2] is indeed '---'
print(f"Line at bab4_start - 2: {repr(lines[bab4_start - 2])}")
print(f"Line at bab4_start - 1: {repr(lines[bab4_start - 1])}")

# Let's perform Section III deletion
modified_lines = lines[:bab3_start] + lines[bab4_start - 2:]

# 2. Locate BAB V and BAB VI in modified_lines
bab5_start = -1
bab6_start = -1
for idx, line in enumerate(modified_lines):
    if line.startswith("## BAB V:"):
        bab5_start = idx
    if line.startswith("## BAB VI:"):
        bab6_start = idx

print(f"BAB V index: {bab5_start}, BAB VI index: {bab6_start}")

# Slice out BAB V
# Similar to before, before BAB VI we have a divider at bab6_start - 2. Let's inspect them:
print(f"Line at bab6_start - 2: {repr(modified_lines[bab6_start - 2])}")
print(f"Line at bab6_start - 1: {repr(modified_lines[bab6_start - 1])}")

modified_lines = modified_lines[:bab5_start] + modified_lines[bab6_start - 2:]

# 3. Insert BLOK 2 heading right above Langkah 2.1
# Let's locate Langkah 2.1 in modified_lines
langkah21_idx = -1
for idx, line in enumerate(modified_lines):
    if line.startswith("#### Langkah 2.1:"):
        langkah21_idx = idx
        break

print(f"Langkah 2.1 index: {langkah21_idx}")
# We want to insert the BLOK 2 heading before Langkah 2.1.
# The lines preceding Langkah 2.1 are:
# ... Langkah 1.3 content ...
# \n
# ---\n
# \n
# #### Langkah 2.1:...
# Let's check lines preceding Langkah 2.1
print(f"Line at langkah21_idx - 3: {repr(modified_lines[langkah21_idx - 3])}")
print(f"Line at langkah21_idx - 2: {repr(modified_lines[langkah21_idx - 2])}")
print(f"Line at langkah21_idx - 1: {repr(modified_lines[langkah21_idx - 1])}")

# Let's insert "### BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER"
# We insert it right before Langkah 2.1 (after the blank line at langkah21_idx - 1)
blok2_heading = [
    "### BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER\n",
    "\n",
    "Blok ini memverifikasi fungsionalitas web Nextcloud, otentikasi akun, pemisahan hak akses, manajemen data, serta load balancing.\n",
    "\n"
]
modified_lines = modified_lines[:langkah21_idx] + blok2_heading + modified_lines[langkah21_idx:]

# 4. Standardize Penutup heading
for idx, line in enumerate(modified_lines):
    if line.startswith("## VII : PENUTUP"):
        modified_lines[idx] = "## VII: PENUTUP (Kesimpulan dan Saran)\n"
        print(f"Standardized Penutup heading at index {idx}")
        break

# 5. Insert Table of Contents (Daftar Isi)
# The first line is the title. We insert the Table of Contents right after it, with blank lines.
toc_content = """
## DAFTAR ISI

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
- [BAB IV: DESAIN SISTEM](#bab-iv-desain-sistem)
  - [4.1 Topology Jaringan Virtual (Network Topology)](#41-topology-jaringan-virtual-network-topology)
  - [4.2 Desain Alur Sistem Login dan Upload (UML Sequence)](#42-desain-alur-sistem-login-dan-upload-uml-sequence)
  - [4.3 Diagram Alur Sistem Failover (HA State Machine)](#43-diagram-alur-sistem-failover-ha-state-machine)
  - [4.4 Diagram Input-Process-Output (IPO)](#44-diagram-input-process-output-ipo)
  - [4.5 Desain Manajemen User dan Kuota](#45-desain-manajemen-user-dan-kuota)
- [BAB VI: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH](#bab-vi-langkah-langkah-implementasi-langkah-demi-langkah)
- [BAB VII: PENGUJIAN SISTEM (17 LANGKAH PENGUJIAN DETAIL)](#bab-vii-pengujian-sistem-17-langkah-pengujian-detail)
  - [BLOK 1: PENGUJIAN INFRASTRUKTUR DAN OTOMATISASI](#blok-1-pengujian-infrastruktur-dan-otomatisasi)
    - [Langkah 1.1: Pengujian Deployment Otomatis Menggunakan Ansible](#langkah-11-pengujian-deployment-otomatis-menggunakan-ansible)
    - [Langkah 1.2: Pengujian Keaktifan Docker Container](#langkah-12-pengujian-keaktifan-docker-container)
    - [Langkah 1.3: Uji Coba Persistensi Data (Data Persistence Check)](#langkah-13-uji-coba-persistensi-data-data-persistence-check)
  - [BLOK 2: PENGUJIAN FITUR APLIKASI DAN MANAJEMEN USER](#blok-2-pengujian-fitur-aplikasi-dan-manajemen-user)
    - [Langkah 2.1: Pengujian Akses Web Nextcloud (HTTPS)](#langkah-21-pengujian-akses-web-nextcloud-https)
    - [Langkah 2.2: Pengujian Pembuatan/Login Administrator](#langkah-22-pengujian-pembuatanlogin-administrator)
    - [Langkah 2.3: Pengujian Pembuatan User Baru dan Grup](#langkah-23-pengujian-pembuatan-user-baru-dan-grup)
    - [Langkah 2.4: Pengujian Login User Biasa](#langkah-24-pengujian-login-user-biasa)
    - [Langkah 2.5: Pengujian Upload File](#langkah-25-pengujian-upload-file)
    - [Langkah 2.6: Pengujian Berbagi Tautan Publik (External Share)](#langkah-26-pengujian-berbagi-tautan-publik-external-share)
    - [Langkah 2.7: Pengujian Hapus File](#langkah-27-pengujian-hapus-file)
  - [BLOK 3: PENGUJIAN LOAD BALANCING DAN HIGH AVAILABILITY](#blok-3-pengujian-load-balancing-dan-high-availability)
    - [Langkah 3.1: Pengujian Load Balancing](#langkah-31-pengujian-load-balancing)
    - [Langkah 3.2: Pengujian Round Robin](#langkah-32-pengujian-round-robin)
    - [Langkah 3.3: Pengujian Failover Container](#langkah-33-pengujian-failover-container)
    - [Langkah 3.4: Pengujian High Availability (HA)](#langkah-34-pengujian-high-availability-ha)
    - [Langkah 3.5: Pengujian Recovery Layanan](#langkah-35-pengujian-recovery-layanan)
    - [Langkah 3.6: Pengujian Monitoring Sistem Menggunakan Prometheus](#langkah-36-pengujian-monitoring-sistem-menggunakan-prometheus)
    - [Langkah 3.7: Pengujian Monitoring Sistem Menggunakan Grafana](#langkah-37-pengujian-monitoring-sistem-menggunakan-grafana)
- [VII: PENUTUP (Kesimpulan dan Saran)](#vii-penutup-kesimpulan-dan-saran)
  - [13.1 Kesimpulan](#131-kesimpulan)
  - [13.2 Saran](#132-saran)

---
"""

# Let's insert after the title (index 0 is the title, index 1 is empty line)
# We will insert it at index 1
modified_lines.insert(1, toc_content)

# Write back to README.md
with open(readme_path, "w", encoding="utf-8") as f:
    f.writelines(modified_lines)

print("Modification complete!")
