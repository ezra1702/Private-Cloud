import glob
import os

for root, dirs, files in os.walk("c:/Users/USER/Desktop/System Administator/Private-Cloud"):
    for f in files:
        if f.lower() == "readme.md":
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            print(f"{path}: {len(lines)} lines, {os.path.getsize(path)} bytes")
