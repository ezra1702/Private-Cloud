import os
import textwrap

parts = [
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part1.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part2.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part3.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part4.md",
    "c:/Users/USER/Desktop/System Administator/Private-Cloud/scratch/readme_part5.md"
]

target_file = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"

def smart_wrap(text, width=80):
    lines = text.splitlines()
    wrapped_lines = []
    in_code_block = False
    
    for line in lines:
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            wrapped_lines.append(line)
            continue
            
        if in_code_block:
            # Keep code blocks exactly as they are
            wrapped_lines.append(line)
        else:
            # If it's a heading, list item, or table row, don't wrap it aggressively
            trimmed = line.strip()
            if trimmed.startswith("#") or trimmed.startswith("*") or trimmed.startswith("-") or trimmed.startswith("|") or trimmed.startswith("+") or not trimmed:
                wrapped_lines.append(line)
            else:
                # Wrap normal paragraph text
                wrapped = textwrap.wrap(line, width=width)
                if wrapped:
                    wrapped_lines.extend(wrapped)
                else:
                    wrapped_lines.append("") # empty line
                    
    return "\n".join(wrapped_lines)

merged_content = ""

for part in parts:
    print(f"Reading {part}...")
    with open(part, "r", encoding="utf-8") as f:
        content = f.read()
        wrapped_content = smart_wrap(content, width=50)
        merged_content += wrapped_content + "\n\n"

with open(target_file, "w", encoding="utf-8") as f:
    f.write(merged_content)

print(f"Smart merged and wrapped successfully into {target_file}!")
