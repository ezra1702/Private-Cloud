import glob
import re

files = glob.glob("*.md")
for f in files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    matches = re.findall(r"img/skenario\S*", content)
    if matches:
        print(f"{f} contains references: {set(matches)}")
