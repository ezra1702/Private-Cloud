import glob
import os
import re

for root, dirs, files in os.walk("c:/Users/USER/Desktop/System Administator/Private-Cloud"):
    for f in files:
        if f.endswith((".md", ".txt", ".py", ".ini", ".cfg", ".yml")):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                matches = re.findall(r"(?i)\bskenario\w*\b", content)
                if matches:
                    print(f"{path}: {len(matches)} matches, e.g., {set(matches[:5])}")
            except Exception as e:
                pass
