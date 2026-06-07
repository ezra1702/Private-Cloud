import os
import glob
import re

# 1. Rename all files in img/ starting with "skenario" to "langkah"
img_dir = "c:/Users/USER/Desktop/System Administator/Private-Cloud/img"
print("--- Renaming image files ---")
for filepath in glob.glob(os.path.join(img_dir, "*skenario*")):
    filepath = filepath.replace("\\", "/")
    filename = os.path.basename(filepath)
    # preserve casing during replacement
    new_filename = filename.replace("skenario", "langkah").replace("Skenario", "Langkah")
    new_filepath = os.path.join(img_dir, new_filename).replace("\\", "/")
    print(f"Renaming: {filename} -> {new_filename}")
    try:
        os.rename(filepath, new_filepath)
    except Exception as e:
        print(f"Error renaming {filepath}: {e}")

# Helper function for case-preserving word replacement of "skenario"
def replace_word_skenario(text):
    def repl(match):
        s = match.group(0)
        res = []
        parts = re.split(r'(?i)(skenario)', s)
        for part in parts:
            if part.lower() == 'skenario':
                if part.isupper():
                    res.append('LANGKAH')
                elif part[0].isupper():
                    res.append('Langkah')
                else:
                    res.append('langkah')
            else:
                res.append(part)
        return "".join(res)
    
    pattern = re.compile(r'(?i)\b[a-z0-9-]*skenario[a-z0-9-]*\b')
    return pattern.sub(repl, text)

# 2. Process README.md
readme_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"
print("\n--- Processing README.md (Unwrapping & Replacing) ---")
with open(readme_path, "r", encoding="utf-8") as f:
    readme_content = f.read()

# Apply replacement first
readme_replaced = replace_word_skenario(readme_content)

# Now unwrap lines
lines = readme_replaced.splitlines()
output_lines = []
in_code_block = False
buffer = []

def flush_buffer():
    if not buffer:
        return
    joined = ""
    for i, line in enumerate(buffer):
        if i == 0:
            joined = line
        else:
            if joined.endswith("-") and not joined.endswith(" -"):
                joined += line
            else:
                joined += " " + line
    output_lines.append(joined)
    buffer.clear()

list_item_regex = re.compile(r"^\s*([-*+]|\d+\.)\s")

for line in lines:
    stripped = line.strip()
    
    if stripped.startswith("```"):
        flush_buffer()
        in_code_block = not in_code_block
        output_lines.append(line)
        continue
        
    if in_code_block:
        output_lines.append(line)
        continue
        
    if (not stripped or 
        stripped.startswith("#") or 
        stripped.startswith("|") or 
        stripped.startswith("---") or
        stripped.startswith(">") or
        list_item_regex.match(stripped)):
        
        flush_buffer()
        if list_item_regex.match(stripped):
            buffer.append(line)
        else:
            output_lines.append(line)
    else:
        buffer.append(line)

flush_buffer()

final_readme = "\n".join(output_lines)
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(final_readme)
print(f"README.md updated successfully! Line count: {len(final_readme.splitlines())}")

# 3. Process skenario.md (replace skenario -> langkah, no unwrapping)
skenario_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/skenario.md"
if os.path.exists(skenario_path):
    print("\n--- Processing skenario.md (Replacing only) ---")
    with open(skenario_path, "r", encoding="utf-8") as f:
        sk_content = f.read()
    sk_replaced = replace_word_skenario(sk_content)
    with open(skenario_path, "w", encoding="utf-8") as f:
        f.write(sk_replaced)
    print("skenario.md updated successfully!")

# 4. Process checkpoint3.md (replace skenario -> langkah, no unwrapping)
cp3_path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/checkpoint3.md"
if os.path.exists(cp3_path):
    print("\n--- Processing checkpoint3.md (Replacing only) ---")
    with open(cp3_path, "r", encoding="utf-8") as f:
        cp3_content = f.read()
    cp3_replaced = replace_word_skenario(cp3_content)
    with open(cp3_path, "w", encoding="utf-8") as f:
        f.write(cp3_replaced)
    print("checkpoint3.md updated successfully!")
