# Cấu trúc Dự án như sau:

```
├── content
│   ├── about.md
│   ├── blogs
│   │   ├── index.md
│   │   ├── post1.md
│   │   └── post2.md
│   ├── index.md
│   ├── magazine
│   │   ├── article1.md
│   │   └── article2.md
│   └── quotes
│       ├── quote1.md
│       └── quote2.md
├── docs
├── generate.py
├── templates
│   ├── base.html
│   ├── blog.html
│   ├── magazine.html
│   └── quotes.html
└── watch.py
```

# Danh sách Các Tệp Dự án:

## ../generate.py

```
import os
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
import shutil
import sys
from pathlib import Path

# Đường dẫn thư mục
CONTENT_DIR = 'content'
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = Path('docs')

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def process_markdown_file(md_path, relative_dir):
    """
    Xử lý một file Markdown:
    - Nếu file HTML đầu ra đã tồn tại và mới hơn file Markdown, bỏ qua build.
    - Ngược lại, chuyển đổi Markdown sang HTML và render qua template.
    """
    # Xác định đường dẫn file HTML đầu ra
    output_subdir = os.path.join(OUTPUT_DIR, relative_dir)
    os.makedirs(output_subdir, exist_ok=True)
    html_filename = os.path.splitext(os.path.basename(md_path))[0] + '.html'
    output_file = os.path.join(output_subdir, html_filename)

    # Kiểm tra thời gian sửa đổi để thực hiện incremental build
    if os.path.exists(output_file):
        md_mtime = os.path.getmtime(md_path)
        html_mtime = os.path.getmtime(output_file)
        if md_mtime <= html_mtime:
            print(f"[Bỏ qua] {output_file} đã mới hơn file Markdown.")
            return  # Không cần build lại

    # Đọc file Markdown và tách metadata (front matter)
    post = frontmatter.load(md_path)
    md_content = post.content
    meta = post.metadata

    # Chuyển Markdown sang HTML
    html_body = markdown.markdown(md_content, extensions=['extra', 'meta'])

    # Lựa chọn template theo metadata (mặc định là 'base')
    layout = meta.get('layout', 'base')
    template_name = f"{layout}.html"
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Không tìm thấy template {template_name}, sử dụng base.html. Lỗi: {e}")
        template = env.get_template('base.html')

    # Render HTML với metadata và nội dung đã chuyển đổi
    rendered_html = template.render(meta=meta, content=html_body)

    # Ghi file HTML vào thư mục OUTPUT_DIR
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    print(f"[Cập nhật] {output_file}")
    return output_file

def traverse_content_dir():
    clean_output()  # Xóa toàn bộ nội dung cũ trước khi build
    
    generated_paths = set()  # Lưu trữ các file đã tạo
    
    for root, dirs, files in os.walk(CONTENT_DIR):
        relative_dir = os.path.relpath(root, CONTENT_DIR)
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                output_path = process_markdown_file(md_path, relative_dir)
                if output_path:
                    generated_paths.add(output_path)
    
    print("✅ Build thành công!")
    
    
def nojekyll():
    """
    Tạo file .nojekyll để GitHub Pages không xử lý Jekyll.
    """
    nojekyll_file = os.path.join(OUTPUT_DIR, '.nojekyll')
    with open(nojekyll_file, 'w') as f:
        f.write('')
    print(f"[Tạo] {nojekyll_file}")
    
    
# Thêm hàm clean_output và sửa logic chính
def clean_output():
    """Phiên bản dùng pathlib an toàn hơn"""
    if OUTPUT_DIR.exists():
        for item in OUTPUT_DIR.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()  # Xóa file
                elif item.is_dir():
                    shutil.rmtree(item)  # Xóa thư mục
            except Exception as e:
                print(f"⚠️ Không thể xóa {item}: {e}")
            
if __name__ == '__main__':
    try:
        print("🔄 Đang bắt đầu quá trình build...")
        traverse_content_dir()
        nojekyll()
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

```

 ## ../watch.py

```
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generate import traverse_content_dir  # Hàm build toàn bộ nội dung

CONTENT_DIR = 'content'
TEMPLATE_DIR = 'templates'

class WatchEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Nếu file không phải là thư mục
        if not event.is_directory:
            # Nếu file là Markdown hoặc file HTML trong templates (có thể có đuôi .html)
            if event.src_path.endswith('.md') or event.src_path.endswith('.html'):
                print(f"[Modified] {event.src_path} đã thay đổi, cập nhật lại HTML...")
                traverse_content_dir()

    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.md') or event.src_path.endswith('.html'):
                print(f"[Created] {event.src_path} được tạo mới, cập nhật lại HTML...")
                traverse_content_dir()

    def on_deleted(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.md') or event.src_path.endswith('.html'):
                print(f"[Deleted] {event.src_path} đã bị xóa, cập nhật lại HTML...")
                traverse_content_dir()

if __name__ == "__main__":
    event_handler = WatchEventHandler()
    observer = Observer()
    # Theo dõi thư mục nội dung
    observer.schedule(event_handler, path=CONTENT_DIR, recursive=True)
    # Theo dõi thư mục templates
    observer.schedule(event_handler, path=TEMPLATE_DIR, recursive=True)
    
    observer.start()
    print(f"Đang theo dõi thay đổi trong các thư mục '{CONTENT_DIR}' và '{TEMPLATE_DIR}'... (Nhấn Ctrl+C để dừng)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

```

 