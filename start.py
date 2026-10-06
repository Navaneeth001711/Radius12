import os
import sys
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / 'backend'
FRONTEND = ROOT / 'frontend'
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from app import app


def run_api():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


def run_frontend():
    os.chdir(FRONTEND)
    server = ThreadingHTTPServer(('127.0.0.1', 5500), SimpleHTTPRequestHandler)
    print('Frontend: http://127.0.0.1:5500/Radius.html')
    print('Admin:    http://127.0.0.1:5500/admin.html')
    server.serve_forever()

if __name__ == '__main__':
    print('Starting Radius Local Service Finder...')
    print('API:      http://127.0.0.1:5000/api/health')
    print('Default admin login: admin@radius.local / admin123  (change via ADMIN_EMAIL / ADMIN_PASSWORD)')
    threading.Thread(target=run_api, daemon=True).start()
    run_frontend()
