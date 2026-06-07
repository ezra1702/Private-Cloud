import os

parts = [
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part1.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part2.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part3.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part4.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part5.md"
]

target_file = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

merged_content = ""

for part in parts:
    print(f"Reading {part}...")
    with open(part, "r", encoding="utf-8") as f:
        merged_content += f.read() + "\n\n"

# Clean up double blank lines at ends if any, then write to target
with open(target_file, "w", encoding="utf-8") as f:
    f.write(merged_content)

print(f"Merged successfully into {target_file}!")
