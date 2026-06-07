import re

with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    content = f.read()

# Find all occurrences of "skenario" (case-insensitive) and print them in context
matches = re.findall(r"(?i).{0,40}skenario.{0,40}", content)
print("--- Found occurrences in context (first 15) ---")
for m in matches[:15]:
    print(m.strip().replace("\n", " "))

print(f"Total occurrences found: {len(re.findall(r'(?i)skenario', content))}")
