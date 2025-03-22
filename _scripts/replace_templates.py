import sys
import re

def parse_args():
    """
    Parses command line arguments.
    Returns the file path and a dictionary of placeholder-value pairs.
    """
    # Check if there are enough arguments and an even number of key-value pairs
    if len(sys.argv) < 3 or (len(sys.argv) - 2) % 2 != 0:
        print("Usage: python3 replacetemplates.py <file> key1 value1 [key2 value2 ...]")
        sys.exit(1)

    file_path = sys.argv[1]

    # Collect key-value pairs from command-line arguments
    raw_pairs = sys.argv[2:]
    replacements = {
        raw_pairs[i]: raw_pairs[i + 1] for i in range(0, len(raw_pairs), 2)
    }

    return file_path, replacements

def replace_placeholders(file_path, replacements):
    """
    Reads the file, replaces all {{ key }} placeholders with their values,
    and writes the result back to the file.
    """
    try:
        # Read the template file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    # Replace each {{ key }} with its corresponding value
    for key, value in replacements.items():
        placeholder = "{{ " + key + " }}"
        content = re.sub(re.escape(placeholder), value, content)

    # Write updated content back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Replaced placeholders in {file_path}")

if __name__ == "__main__":
    file_path, replacements = parse_args()
    replace_placeholders(file_path, replacements)
