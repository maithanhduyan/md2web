import os
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader

# Đường dẫn thư mục
CONTENT_DIR = 'content'
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'docs\website'

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

def traverse_content_dir():
    """
    Duyệt đệ quy thư mục CONTENT_DIR và xử lý tất cả các file Markdown.
    Cấu trúc thư mục OUTPUT_DIR sẽ tương ứng với cấu trúc thư mục CONTENT_DIR.
    """
    for root, dirs, files in os.walk(CONTENT_DIR):
        # Lấy đường dẫn tương đối so với CONTENT_DIR
        relative_dir = os.path.relpath(root, CONTENT_DIR)
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                process_markdown_file(md_path, relative_dir)

def nojekyll():
    """
    Tạo file .nojekyll để GitHub Pages không xử lý Jekyll.
    """
    nojekyll_file = os.path.join(OUTPUT_DIR, '.nojekyll')
    with open(nojekyll_file, 'w') as f:
        f.write('')
    print(f"[Tạo] {nojekyll_file}")
    
if __name__ == '__main__':
    traverse_content_dir()
    nojekyll()
