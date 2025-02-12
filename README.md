[![Deploy static content to Pages](https://github.com/maithanhduyan/md2web/actions/workflows/deploy.yml/badge.svg)](https://github.com/maithanhduyan/md2web/actions/workflows/deploy.yml)

# md2web

## For Dev

> python -m venv .venv

> .venv\Scripts\activate

> pip install -r requirements.txt

> python watch.py

## Test

- Lỗi đường dẫn:

  Kiểm tra các link trong template đã dùng relative path.
  Test local bằng cách chạy server:

> python -m http.server 8000 --directory docs/
