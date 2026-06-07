with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.findall(r"(?i)sken\w*", content)
print("Matches for 'sken*':", set(matches))
