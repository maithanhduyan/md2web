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
