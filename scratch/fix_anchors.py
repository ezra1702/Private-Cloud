readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI LANGKAH DEMI LANGKAH", "## BAB IV: LANGKAH-LANGKAH IMPLEMENTASI")

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Anchors aligned successfully!")
