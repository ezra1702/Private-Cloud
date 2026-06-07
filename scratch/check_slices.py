with open("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Section III Boundary ---")
for idx in range(74, 82):
    print(f"Line {idx+1}: {repr(lines[idx])}")
print("...")
for idx in range(110, 116):
    print(f"Line {idx+1}: {repr(lines[idx])}")

print("\n--- Section V Boundary ---")
for idx in range(232, 240):
    print(f"Line {idx+1}: {repr(lines[idx])}")
print("...")
for idx in range(864, 872):
    print(f"Line {idx+1}: {repr(lines[idx])}")
