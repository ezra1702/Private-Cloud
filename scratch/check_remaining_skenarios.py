import re

files = [
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/skenario.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/checkpoint3.md"
]

for f in files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    matches = re.findall(r"(?i)\bskenario\w*\b", content)
    print(f"{f}: {len(matches)} occurrences left. Matches: {set(matches)}")
