import os

def create_missing_content_files():
    base_dir = os.path.join('docs', 'documents', 'stories')
    
    for root, dirs, files in os.walk(base_dir):
        # Skip the base directory itself
        if root == base_dir:
            continue
        
        if 'content.md_insert' not in files:
            content_file_path = os.path.join(root, 'content.md_insert')
            with open(content_file_path, 'w') as f:
                pass  # Create an empty file
            print(f"Created missing file: {content_file_path}")

if __name__ == "__main__":
    create_missing_content_files()
