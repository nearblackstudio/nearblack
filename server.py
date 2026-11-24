#!/usr/bin/env python3
"""Local dev server that mimics Vercel's cleanUrls (/portfolio -> portfolio.html)."""
import http.server, socketserver, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        fs = super().translate_path(p)
        if p != "/" and not os.path.splitext(p)[1]:
            # /blog or /blog/ -> blog.html, even though a blog/ folder exists (like Vercel cleanUrls)
            html = fs.rstrip("/" + os.sep) + ".html"
            if os.path.exists(html) and not os.path.exists(os.path.join(fs, "index.html")):
                return html
        return fs

    def send_head(self):
        # /blog/ -> 308 to /blog, like Vercel's trailingSlash:false (keeps relative asset paths working)
        p = self.path.split("?", 1)[0].split("#", 1)[0]
        if p.endswith("/") and p != "/" and os.path.isfile(self.translate_path(p)):
            q = self.path[len(p):]
            self.send_response(308)
            self.send_header("Location", p.rstrip("/") + q)
            self.end_headers()
            return None
        return super().send_head()

    def end_headers(self):
        # never cache during local dev so CSS/HTML edits show immediately
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4321
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving {ROOT} on http://localhost:{PORT} (clean URLs, no-cache)")
    httpd.serve_forever()
