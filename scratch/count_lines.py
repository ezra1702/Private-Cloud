import glob
import os

files = glob.glob("*.md") + glob.glob("scratch/*.md")
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            lines = file.readlines()
            print(f"{f}: {len(lines)} lines, {os.path.getsize(f)} bytes")
    except Exception as e:
        print(f"Error reading {f}: {e}")
