
import sys
import os
import jinja2
import json

def parse_args():
    if len(sys.argv) < 3 or (len(sys.argv) - 2) % 2 != 0:
        print("Usage: python3 replace_templates.py <file> key1 value1 [key2 value2 ...]")
        sys.exit(1)

    file_path = sys.argv[1]
    raw_pairs = sys.argv[2:]
    replacements = {}

    for i in range(0, len(raw_pairs), 2):
        key = raw_pairs[i]
        value = raw_pairs[i + 1]
        try:
            parsed = json.loads(value)
            replacements[key] = parsed
        except (json.JSONDecodeError, TypeError):
            replacements[key] = value

    return file_path, replacements

def render_template(file_path, context):
    template_dir = os.path.dirname(file_path)
    template_file = os.path.basename(file_path)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template(template_file)
    output = template.render(context)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ Rendered Jinja2 template: {file_path}")

if __name__ == "__main__":
    file_path, context = parse_args()
    render_template(file_path, context)
