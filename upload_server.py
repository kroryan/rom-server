#!/usr/bin/env python3
"""
Servidor simple para subida de archivos ROM y thumbnails.
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

# Configuración
ROMS_DIR = "/roms"
THUMBNAILS_DIR = "/thumbnails"

# Buffer de logs
log_buffer = []

def log_message(msg):
    """Añadir mensaje al log"""
    log_buffer.append(msg)
    if len(log_buffer) > 1000:
        log_buffer.pop(0)
    print(msg)
    sys.stdout.flush()

class UploadHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        msg = f"{self.log_date_time_string()} - {format % args}"
        log_message(msg)

    def do_OPTIONS(self):
        # Manejar preflight OPTIONS sin duplicar headers
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_GET(self):
        if self.path == '/logs':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'logs': log_buffer[-100:]}).encode())
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def do_POST(self):
        log_message(f"POST request to {self.path}")

        if self.path == '/upload/thumbnail':
            self.handle_thumbnail_upload()
        elif self.path == '/upload/rom':
            self.handle_rom_upload()
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def handle_rom_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid content type"}')
                return

            boundary = content_type.split('boundary=')[-1]
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            parts = body.split(('--' + boundary).encode())

            folder = None
            filename = None
            file_data = None

            for part in parts:
                if b'Content-Disposition' in part:
                    if b'name="folder"' in part:
                        lines = part.split(b'\r\n')
                        for i, line in enumerate(lines):
                            if b'name="folder"' in line and i + 2 < len(lines):
                                folder = lines[i + 2].decode().strip()
                                break

                    elif b'name="file"' in part:
                        for line in part.split(b'\r\n'):
                            if b'filename=' in line:
                                filename = line.split(b'filename=')[-1].strip(b'"').decode()
                                break
                        if b'\r\n\r\n' in part:
                            file_data = part.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0]

            if not folder or not file_data or not filename:
                log_message("Error: Missing data in ROM upload")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error": "Missing data"}')
                return

            log_message(f"Uploading ROM: {filename} to {folder}/")

            rom_dir = os.path.join(ROMS_DIR, folder)
            os.makedirs(rom_dir, exist_ok=True)
            rom_path = os.path.join(rom_dir, filename)

            with open(rom_path, 'wb') as f:
                f.write(file_data)

            log_message(f"ROM uploaded successfully: {rom_path}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'path': rom_path}).encode())

        except Exception as e:
            log_message(f"Error in ROM upload: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_thumbnail_upload(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            game = data.get('game', '')
            folder = data.get('folder', '')
            url = data.get('url', '')

            if not game or not folder or not url:
                log_message("Error: Missing parameters in thumbnail upload")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error": "Missing parameters"}')
                return

            log_message(f"Downloading thumbnail for {game} from {url}")

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    thumb_dir = os.path.join(THUMBNAILS_DIR, folder)
                    os.makedirs(thumb_dir, exist_ok=True)
                    thumb_path = os.path.join(thumb_dir, f"{game}.png")

                    with open(thumb_path, 'wb') as f:
                        f.write(response.read())

                    log_message(f"Thumbnail saved: {thumb_path}")

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True, 'path': thumb_path}).encode())
                else:
                    raise Exception(f'HTTP {response.status}')

        except Exception as e:
            log_message(f"Error in thumbnail upload: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

def main():
    port = 8080
    server = HTTPServer(('0.0.0.0', port), UploadHandler)
    log_message(f"Upload server running on port {port}")
    log_message(f"ROMs dir: {ROMS_DIR}")
    log_message(f"Thumbnails dir: {THUMBNAILS_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_message("Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()
