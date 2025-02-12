import os
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
import shutil
import sys
from pathlib import Path

# Đường dẫn thư mục
GITHUB_PAGES_REPO_NAME = "https://maithanhduyan.github.io/md2web/"  # 🚨 Điền tên repo của bạn (nếu là Project site)
BASE_URL = f"/{GITHUB_PAGES_REPO_NAME}" if GITHUB_PAGES_REPO_NAME else ""
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
