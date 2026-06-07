with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

# Let's split by lines
lines = readme_content.splitlines()

# We will find the line indices of headings
headings = []
for idx, line in enumerate(lines):
    if line.startswith("#"):
        headings.append((idx, line))

for h in headings:
    print(h)
