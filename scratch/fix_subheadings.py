import re

readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update BAB III sub-headings
content = content.replace("### 4.1 Topology Jaringan Virtual", "### 3.1 Topology Jaringan Virtual")
content = content.replace("### 4.2 Desain Alur Sistem", "### 3.2 Desain Alur Sistem")
content = content.replace("### 4.3 Diagram Alur Sistem", "### 3.3 Diagram Alur Sistem")
content = content.replace("### 4.4 Diagram Input-Process-Output", "### 3.4 Diagram Input-Process-Output")
content = content.replace("### 4.5 Desain Manajemen User", "### 3.5 Desain Manajemen User")

# 2. Update BAB VI sub-headings
content = content.replace("### 13.1 Kesimpulan", "### 6.1 Kesimpulan")
content = content.replace("### 13.2 Saran", "### 6.2 Saran")

# 3. Update Table of Contents references
content = content.replace("  - [4.1 Topology Jaringan Virtual (Network Topology)](#41-topology-jaringan-virtual-network-topology)", "  - [3.1 Topology Jaringan Virtual (Network Topology)](#31-topology-jaringan-virtual-network-topology)")
content = content.replace("  - [4.2 Desain Alur Sistem Login dan Upload (UML Sequence)](#42-desain-alur-sistem-login-dan-upload-uml-sequence)", "  - [3.2 Desain Alur Sistem Login dan Upload (UML Sequence)](#32-desain-alur-sistem-login-dan-upload-uml-sequence)")
content = content.replace("  - [4.3 Diagram Alur Sistem Failover (HA State Machine)](#43-diagram-alur-sistem-failover-ha-state-machine)", "  - [3.3 Diagram Alur Sistem Failover (HA State Machine)](#33-diagram-alur-sistem-failover-ha-state-machine)")
content = content.replace("  - [4.4 Diagram Input-Process-Output (IPO)](#44-diagram-input-process-output-ipo)", "  - [3.4 Diagram Input-Process-Output (IPO)](#34-diagram-input-process-output-ipo)")
content = content.replace("  - [4.5 Desain Manajemen User dan Kuota](#45-desain-manajemen-user-dan-kuota)", "  - [3.5 Desain Manajemen User dan Kuota](#35-desain-manajemen-user-dan-kuota)")

content = content.replace("  - [13.1 Kesimpulan](#131-kesimpulan)", "  - [6.1 Kesimpulan](#61-kesimpulan)")
content = content.replace("  - [13.2 Saran](#132-saran)", "  - [6.2 Saran](#62-saran)")

# Update headers anchors if they are used in text (unlikely, but let's check)
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Sub-headings fixed!")
