#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""preview_server.py — статический сервер витрины Художника (зона 04-artist/).

Отдаёт только файлы внутри 04-artist/ (без .git и чужих зон), редиректит / -> /viewer/.
Bind 0.0.0.0 для live-preview платформы. Без внешних зависимостей.

Запуск: .venv/bin/python 04-artist/tools/preview_server.py [порт]
"""
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # 04-artist/
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/viewer/")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("Витрина 04-artist/ на http://0.0.0.0:%d/ -> /viewer/" % PORT, flush=True)
    httpd.serve_forever()
