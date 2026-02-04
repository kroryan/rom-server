#!/usr/bin/env python3
"""
Servidor simple para subida de archivos ROM y thumbnails.
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import threading
import time
import re
import zlib
import struct

# Configuración
ROMS_DIR = "/roms"
THUMBNAILS_DIR = "/thumbnails"

# Buffer de logs
log_buffer = []
thumb_log_buffer = []

thumb_scan_state = {
    "running": False,
    "total": 0,
    "processed": 0,
    "found": 0,
    "generated": 0,
    "failed": 0,
    "current": "",
    "started_at": None,
    "finished_at": None
}
thumb_scan_lock = threading.Lock()

LIBRETRO_MAP = {
    "gb": "Nintendo - Game Boy",
    "gbc": "Nintendo - Game Boy Color",
    "gba": "Nintendo - Game Boy Advance"
}

ROM_EXTENSIONS = {
    "gb": [".gb"],
    "gbc": [".gbc", ".gb"],
    "gba": [".gba"]
}

def log_message(msg):
    """Añadir mensaje al log"""
    log_buffer.append(msg)
    if len(log_buffer) > 1000:
        log_buffer.pop(0)
    print(msg)
    sys.stdout.flush()



def log_thumb(msg):
    thumb_log_buffer.append(msg)
    if len(thumb_log_buffer) > 1000:
        thumb_log_buffer.pop(0)
    print(msg)
    sys.stdout.flush()



def clean_game_name(name: str) -> str:
    # quitar extension
    clean = re.sub(r'\.[^.]+$', '', name)
    # normalizar separadores
    clean = re.sub(r'_+', ' ', clean)
    # quitar tags entre [] o ()
    clean = re.sub(r'\s*[\[(][^\]\)]*[\])]\s*', ' ', clean)
    # quitar sufijos comunes
    clean = re.sub(r'(Rev\s*\d+|Revision\s*\d+|v\d+(?:\.\d+)*|Beta|Proto|Prototype|Demo|Sample|Hack|Translation|Trainer|Fixed|Unl|Pirate|Alt|Alt\s*\d+)', ' ', clean, flags=re.I)
    # limpiar espacios
    clean = re.sub(r'[-]{2,}', '-', clean)
    clean = re.sub(r'\s*[-—:]\s*$', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def name_variations(clean: str):
    variations = [clean]
    if clean.lower().startswith('the '):
        variations.append(clean[4:])
        variations.append(f"{clean[4:]}, The")
    if '&' in clean:
        variations.append(clean.replace('&', 'and'))
    if ' and ' in clean:
        variations.append(clean.replace(' and ', ' & '))
    # únicos
    seen = set()
    out = []
    for v in variations:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def try_download_libretro(system, game_name, output_path):
    base_url = f"https://thumbnails.libretro.com/{urllib.parse.quote(system)}"
    types = ["Named_Boxarts", "Named_Snaps", "Named_Titles"]
    for thumb_type in types:
        encoded = urllib.parse.quote(game_name + '.png')
        url = f"{base_url}/{thumb_type}/{encoded}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(resp.read())
                    return True
        except Exception:
            continue
    return False


def write_png(path, width, height, rgba_bytes):
    # rgba_bytes: bytes length width*height*4
    def chunk(tag, data):
        return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)

    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(rgba_bytes[start:start+stride])
    compressed = zlib.compress(bytes(raw), level=6)

    header = struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)


def draw_text(buffer, width, height, x, y, text, color, scale=2):
    font = {
        'A': ["01110","10001","10001","11111","10001","10001","10001"],
        'B': ["11110","10001","10001","11110","10001","10001","11110"],
        'C': ["01110","10001","10000","10000","10000","10001","01110"],
        'D': ["11100","10010","10001","10001","10001","10010","11100"],
        'E': ["11111","10000","10000","11110","10000","10000","11111"],
        'F': ["11111","10000","10000","11110","10000","10000","10000"],
        'G': ["01110","10001","10000","10111","10001","10001","01110"],
        'H': ["10001","10001","10001","11111","10001","10001","10001"],
        'I': ["11111","00100","00100","00100","00100","00100","11111"],
        'J': ["00111","00010","00010","00010","10010","10010","01100"],
        'K': ["10001","10010","10100","11000","10100","10010","10001"],
        'L': ["10000","10000","10000","10000","10000","10000","11111"],
        'M': ["10001","11011","10101","10101","10001","10001","10001"],
        'N': ["10001","11001","10101","10011","10001","10001","10001"],
        'O': ["01110","10001","10001","10001","10001","10001","01110"],
        'P': ["11110","10001","10001","11110","10000","10000","10000"],
        'Q': ["01110","10001","10001","10001","10101","10010","01101"],
        'R': ["11110","10001","10001","11110","10100","10010","10001"],
        'S': ["01111","10000","10000","01110","00001","00001","11110"],
        'T': ["11111","00100","00100","00100","00100","00100","00100"],
        'U': ["10001","10001","10001","10001","10001","10001","01110"],
        'V': ["10001","10001","10001","10001","10001","01010","00100"],
        'W': ["10001","10001","10001","10101","10101","10101","01010"],
        'X': ["10001","10001","01010","00100","01010","10001","10001"],
        'Y': ["10001","10001","01010","00100","00100","00100","00100"],
        'Z': ["11111","00001","00010","00100","01000","10000","11111"],
        '0': ["01110","10001","10011","10101","11001","10001","01110"],
        '1': ["00100","01100","00100","00100","00100","00100","01110"],
        '2': ["01110","10001","00001","00010","00100","01000","11111"],
        '3': ["11110","00001","00001","01110","00001","00001","11110"],
        '4': ["00010","00110","01010","10010","11111","00010","00010"],
        '5': ["11111","10000","10000","11110","00001","00001","11110"],
        '6': ["01110","10000","10000","11110","10001","10001","01110"],
        '7': ["11111","00001","00010","00100","01000","01000","01000"],
        '8': ["01110","10001","10001","01110","10001","10001","01110"],
        '9': ["01110","10001","10001","01111","00001","00001","01110"],
        '-': ["00000","00000","00000","11111","00000","00000","00000"],
        '.': ["00000","00000","00000","00000","00000","00110","00110"],
        ',': ["00000","00000","00000","00000","00110","00110","01100"],
        ' ': ["00000","00000","00000","00000","00000","00000","00000"],
        '&': ["01100","10010","10100","01000","10101","10010","01101"],
        "'": ["00100","00100","00000","00000","00000","00000","00000"],
        ':': ["00000","00110","00110","00000","00110","00110","00000"],
    }

    text = ''.join(ch if ch in font else ' ' for ch in text)
    cursor_x = x
    for ch in text:
        glyph = font.get(ch)
        if glyph:
            for row, rowbits in enumerate(glyph):
                for col, bit in enumerate(rowbits):
                    if bit == '1':
                        for sy in range(scale):
                            py = y + row * scale + sy
                            if 0 <= py < height:
                                for sx in range(scale):
                                    px = cursor_x + col * scale + sx
                                    if 0 <= px < width:
                                        idx = (py * width + px) * 4
                                        buffer[idx:idx+4] = bytes(color)
        cursor_x += (6 * scale)


def create_placeholder_png(path, title, console_name):
    width = 512
    height = 512
    buf = bytearray(width * height * 4)
    # gradient
    for y in range(height):
        t = y / (height - 1)
        r = int(15 + (26-15) * t)
        g = int(52 + (26-52) * t)
        b = int(96 + (46-96) * t)
        for x in range(width):
            idx = (y * width + x) * 4
            buf[idx:idx+4] = bytes([r, g, b, 255])

    # title
    title = title.upper()
    title = re.sub(r"[^A-Z0-9 \-\.&',:]", ' ', title)
    words = title.split()
    lines = []
    current = ''
    for w in words:
        test = f"{current} {w}".strip()
        if len(test) > 18 and current:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    lines = lines[:2]

    # center text
    y_start = 200
    for i, line in enumerate(lines):
        line_width = len(line) * 6 * 3
        x = max(10, (width - line_width) // 2)
        draw_text(buf, width, height, x, y_start + i * 40, line, (255, 255, 255, 255), scale=3)

    # console name
    cn = console_name.upper()
    cn = re.sub(r"[^A-Z0-9 \-\.&',:]", ' ', cn)
    line_width = len(cn) * 6 * 2
    x = max(10, (width - line_width) // 2)
    draw_text(buf, width, height, x, height - 60, cn, (156, 163, 175, 255), scale=2)

    write_png(path, width, height, buf)


def scan_thumbnails(consoles):
    with thumb_scan_lock:
        if thumb_scan_state["running"]:
            return False
        thumb_scan_state.update({
            "running": True,
            "total": 0,
            "processed": 0,
            "found": 0,
            "generated": 0,
            "failed": 0,
            "current": "",
            "started_at": time.time(),
            "finished_at": None
        })

    tasks = []
    for entry in consoles:
        console = entry.get('console') if isinstance(entry, dict) else None
        if not console:
            continue
        system = entry.get('system') or LIBRETRO_MAP.get(console)
        exts = entry.get('extensions') or ROM_EXTENSIONS.get(console, [])
        rom_dir = os.path.join(ROMS_DIR, console)
        if not os.path.isdir(rom_dir):
            continue
        for fname in os.listdir(rom_dir):
            lower = fname.lower()
            if exts and not any(lower.endswith(ext) for ext in exts):
                continue
            clean = clean_game_name(fname)
            thumb_path = os.path.join(THUMBNAILS_DIR, console, f"{clean}.png")
            if os.path.exists(thumb_path):
                continue
            tasks.append((console, fname, clean, thumb_path, system))

    with thumb_scan_lock:
        thumb_scan_state["total"] = len(tasks)

    for console, fname, clean, thumb_path, system in tasks:
        with thumb_scan_lock:
            thumb_scan_state["current"] = f"{console}/{fname}"
        ok = False
        if system:
            for name in name_variations(clean):
                if try_download_libretro(system, name, thumb_path):
                    ok = True
                    break
        if ok:
            log_thumb(f"[OK] {console}: {clean} (libretro)")
            with thumb_scan_lock:
                thumb_scan_state["found"] += 1
        else:
            try:
                create_placeholder_png(thumb_path, clean, system or console)
                log_thumb(f"[GEN] {console}: {clean} (placeholder)")
                with thumb_scan_lock:
                    thumb_scan_state["generated"] += 1
            except Exception as e:
                log_thumb(f"[FAIL] {console}: {clean} ({e})")
                with thumb_scan_lock:
                    thumb_scan_state["failed"] += 1

        with thumb_scan_lock:
            thumb_scan_state["processed"] += 1

    with thumb_scan_lock:
        thumb_scan_state["running"] = False
        thumb_scan_state["finished_at"] = time.time()
    return True


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

        elif self.path.startswith('/thumbs/status'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with thumb_scan_lock:
                payload = dict(thumb_scan_state)
            self.wfile.write(json.dumps(payload).encode())
        elif self.path.startswith('/thumbs/logs'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'logs': thumb_log_buffer[-200:]}).encode())
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def do_POST(self):
        log_message(f"POST request to {self.path}")

        if self.path == '/upload/thumbnail':
            self.handle_thumbnail_upload()
        elif self.path == '/upload/thumbnail_base64':
            self.handle_thumbnail_base64()
        elif self.path == '/upload/rom':
            self.handle_rom_upload()
        elif self.path == '/thumbs/scan':
            self.handle_thumbs_scan()
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

    def handle_thumbnail_base64(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            game = data.get('game', '')
            folder = data.get('folder', '')
            data_url = data.get('data', '')

            if not game or not folder or not data_url:
                log_message("Error: Missing parameters in thumbnail_base64 upload")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error": "Missing parameters"}')
                return

            if not data_url.startswith('data:image/png;base64,'):
                log_message("Error: Invalid data URL")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid data"}')
                return

            import base64
            b64 = data_url.split(',', 1)[1]
            image_bytes = base64.b64decode(b64)

            thumb_dir = os.path.join(THUMBNAILS_DIR, folder)
            os.makedirs(thumb_dir, exist_ok=True)
            thumb_path = os.path.join(thumb_dir, f"{game}.png")

            with open(thumb_path, 'wb') as f:
                f.write(image_bytes)

            log_message(f"Thumbnail (base64) saved: {thumb_path}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'path': thumb_path}).encode())

        except Exception as e:
            log_message(f"Error in thumbnail_base64 upload: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    def handle_thumbs_scan(self):
        try:
            with thumb_scan_lock:
                if thumb_scan_state.get('running'):
                    self.send_response(409)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Scan already running'}).encode())
                    return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else b'{}'
            data = json.loads(body.decode() or '{}')

            consoles = []
            if isinstance(data, dict) and isinstance(data.get('consoles'), list):
                for item in data['consoles']:
                    if isinstance(item, dict) and item.get('console'):
                        consoles.append({
                            'console': item.get('console'),
                            'system': item.get('system'),
                            'extensions': item.get('extensions')
                        })
            elif isinstance(data, dict) and data.get('console'):
                consoles.append({
                    'console': data.get('console'),
                    'system': data.get('system'),
                    'extensions': data.get('extensions')
                })
            else:
                consoles = [
                    {'console': 'gb', 'system': LIBRETRO_MAP.get('gb'), 'extensions': ['.gb']},
                    {'console': 'gbc', 'system': LIBRETRO_MAP.get('gbc'), 'extensions': ['.gbc', '.gb']},
                    {'console': 'gba', 'system': LIBRETRO_MAP.get('gba'), 'extensions': ['.gba']}
                ]

            def runner():
                targets = ', '.join([c['console'] for c in consoles])
                log_thumb(f"[START] scan consoles: {targets}")
                scan_thumbnails(consoles)
                log_thumb("[DONE] scan finished")

            t = threading.Thread(target=runner, daemon=True)
            t.start()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'started': True, 'consoles': [c['console'] for c in consoles]}).encode())
        except Exception as e:
            log_thumb(f"Error starting scan: {e}")
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
