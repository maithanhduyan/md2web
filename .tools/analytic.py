import os

def collect_files(root_dir, extensions, filenames, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    matches = []
    for root, dirs, files_in_dir in os.walk(root_dir):
        # Loại trừ các thư mục không mong muốn
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files_in_dir:
            # Bỏ qua các tệp không mong muốn
            if filename in exclude_files:
                continue
            if filename.endswith(tuple(extensions)) or filename in filenames:
                filepath = os.path.join(root, filename)
                matches.append(filepath)
    return matches

def get_directory_tree(root_dir, exclude_dirs=None, exclude_files=None, prefix=''):
    """
    Tạo một chuỗi biểu diễn cấu trúc thư mục dưới dạng cây.
    """
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    
    tree_str = ''
    entries = sorted(os.listdir(root_dir))
    entries = [e for e in entries if e not in exclude_dirs and e not in exclude_files]
    entries_count = len(entries)
    
    for index, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        connector = '└── ' if index == entries_count - 1 else '├── '
        tree_str += f"{prefix}{connector}{entry}\n"
        if os.path.isdir(path):
            extension = '    ' if index == entries_count - 1 else '│   '
            tree_str += get_directory_tree(path, exclude_dirs, exclude_files, prefix + extension)
    return tree_str

def write_markdown(files, output_file, root_dir, exclude_dirs=None, exclude_files=None):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Viết cấu trúc thư mục đầu tiên
        f.write('# Cấu trúc Dự án như sau:\n\n')
        tree = get_directory_tree(root_dir, exclude_dirs, exclude_files)
        f.write('```\n')
        f.write(tree)
        f.write('```\n\n')
        
        # Viết nội dung các tệp
        f.write('# Danh sách Các Tệp Dự án:\n\n')
        for filepath in files:
            f.write(f'## {filepath}\n\n')
            f.write('```\n')
            try:
                with open(filepath, 'r', encoding='utf-8') as file_content:
                    f.write(file_content.read())
            except Exception as e:
                f.write(f'**Lỗi đọc tệp:** {e}\n')
            f.write('\n```\n\n ')

if __name__ == '__main__':
    root_dir = '../'
    output_file = 'project_structure.md'
    extensions = ['.py']  # Danh sách các phần mở rộng tệp
    filenames = []  # Danh sách các tên tệp cụ thể
    exclude_dirs = ['node_modules', 'data', '.tools', '.vscode', '.git', 'lib', '.venv', 'venv']  # Thư mục cần bỏ qua
    exclude_files = ['.gitignore', 'requirements.txt', 'README.md', '.github', '.site', '__pycache__','static', 'LICENSE']  # Tệp cần bỏ qua
    files = collect_files(root_dir, extensions, filenames, exclude_dirs, exclude_files)
    write_markdown(files, output_file, root_dir, exclude_dirs, exclude_files)