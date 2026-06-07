import re

def unwrap_and_replace(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Case-preserving replacements for "skenario"
    # We want to replace skenario -> langkah
    # Pattern: \bskenario\b
    # But wait, Indonesian has "skenario-skenario" -> "langkah-langkah"
    # and "skenarionya" -> "langkahnya"
    # Let's write a replacement function
    def replace_sken(match):
        word = match.group(0)
        # Check case
        if word == "skenario":
            return "langkah"
        elif word == "Skenario":
            return "Langkah"
        elif word == "SKENARIO":
            return "LANGKAH"
        elif word.lower() == "skenario-skenario":
            if word.startswith("S"):
                return "Langkah-langkah"
            return "langkah-langkah"
        elif word.lower() == "skenarionya":
            if word.startswith("S"):
                return "Langkahnya"
            return "langkahnya"
        elif word.lower() == "skenario1":
            if word.startswith("S"):
                return "Langkah1"
            return "langkah1"
        elif word.lower() == "skenario2":
            if word.startswith("S"):
                return "Langkah2"
            return "langkah2"
        # Fallback
        if word.isupper():
            return word.replace("SKENARIO", "LANGKAH")
        elif word[0].isupper():
            return word.replace("Skenario", "Langkah")
        else:
            return word.replace("skenario", "langkah")

    # Let's test the regex pattern for skenario
    # Skenario can be followed by letters (e.g. skenarionya, skenario-skenario)
    # Let's match: (skenario-skenario|skenarionya|skenario\d+|skenario) (case-insensitive)
    content_replaced = re.sub(r"(?i)\bskenario-skenario\b|\bskenarionya\b|\bskenario\d+\b|\bskenario\b", replace_sken, content)

    # Now let's unwrap the lines
    lines = content_replaced.splitlines()
    output_lines = []
    
    in_code_block = False
    buffer = []
    
    def flush_buffer():
        if not buffer:
            return
        # Join lines in buffer. 
        # For markdown, we join them with a single space.
        # But wait, if a line ends with a hyphen "-", do we add a space?
        # Let's check: in textwrap, "on-premise" -> "on-" and "premise".
        # If we join "on-" and "premise" with a space, it's "on- premise".
        # Let's handle it by checking if line ends with a hyphen.
        # If line ends with a hyphen, we can join them without a space?
        # Actually, let's look at the words. "on-premise" is typical.
        # Let's do a smart join:
        joined = ""
        for i, line in enumerate(buffer):
            if i == 0:
                joined = line
            else:
                # If the previous part ends with a hyphen, and it's followed by a letter, don't add a space
                if joined.endswith("-") and not joined.endswith(" -"):
                    joined += line
                else:
                    joined += " " + line
        output_lines.append(joined)
        buffer.clear()

    list_item_regex = re.compile(r"^\s*([-*+]|\d+\.)\s")

    for line in lines:
        stripped = line.strip()
        
        # Toggle code block
        if stripped.startswith("```"):
            flush_buffer()
            in_code_block = not in_code_block
            output_lines.append(line)
            continue
            
        if in_code_block:
            output_lines.append(line)
            continue
            
        # Outside code block
        # Check if line is empty or is a separator or starts with a heading or table row
        if (not stripped or 
            stripped.startswith("#") or 
            stripped.startswith("|") or 
            stripped.startswith("---") or
            list_item_regex.match(stripped)):
            
            # If the current line starts a new list item, we must flush the buffer first
            flush_buffer()
            
            # If it's a list item, we can start buffering it, because list items can span multiple lines!
            if list_item_regex.match(stripped):
                buffer.append(line)
            else:
                output_lines.append(line)
        else:
            # It's a regular text line (continuation of a paragraph or list item)
            # If buffer is empty, start buffering. If buffer is not empty, append to buffer.
            buffer.append(line)
            
    flush_buffer()
    
    return "\n".join(output_lines)

# Let's test the result
result = unwrap_and_replace("c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md")
print(f"Original lines: {len(open('c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md', 'r', encoding='utf-8').readlines())}")
print(f"Unwrapped lines: {len(result.splitlines())}")

# Let's check some snippets around the intro
lines = result.splitlines()
print("\n--- FIRST 30 LINES OF RESULT ---")
for i in range(min(30, len(lines))):
    print(f"{i+1}: {lines[i]}")
