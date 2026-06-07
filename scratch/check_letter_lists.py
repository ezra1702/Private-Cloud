import re

with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = re.compile(r"^\s*[a-zA-Z]\.\s")
for i, line in enumerate(lines):
    if pattern.match(line):
        print(f"Line {i+1}: {line.strip()}")
