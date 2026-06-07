with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.findall(r"(?i)skenario\.md", content)
print("Matches for 'skenario.md':", matches)
