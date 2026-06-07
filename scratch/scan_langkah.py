with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.findall(r"(?i).{0,40}langkah.{0,40}", content)
print("--- Occurrences of 'langkah' (first 15) ---")
for m in matches[:15]:
    print(m.strip().replace("\n", " "))

print(f"Total occurrences found: {len(re.findall(r'(?i)langkah', content))}")
