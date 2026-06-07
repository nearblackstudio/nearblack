#!/usr/bin/env python3
"""Local dev server that mimics Vercel's cleanUrls (/portfolio -> portfolio.html)."""
import http.server, socketserver, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        fs = super().translate_path(p)
        # extensionless, non-directory request -> serve the matching .html
        if p != "/" and not os.path.splitext(p)[1] and not os.path.isdir(fs):
            html = fs + ".html"
            if os.path.exists(html):
                return html
        return fs

    def end_headers(self):
        # never cache during local dev so CSS/HTML edits show immediately
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4321
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving {ROOT} on http://localhost:{PORT} (clean URLs, no-cache)")
    httpd.serve_forever()
