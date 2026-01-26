#!/usr/bin/env python3
"""
Descarga thumbnails de libretro para todos los ROMs.
Guarda las imagenes en /thumbnails/{sistema}/{nombre}.png
"""

import os
import re
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Configuracion
ROMS_DIR = "/mnt/Expansion/roms"
THUMBNAILS_DIR = "/home/kroryan/docker-data/roms-server/thumbnails"

CONSOLES = {
    "gba": {
        "extensions": [".gba"],
        "libretro": "Nintendo - Game Boy Advance"
    },
    "gbc": {
        "extensions": [".gbc", ".gb"],
        "libretro": "Nintendo - Game Boy Color"
    },
    "snes": {
        "extensions": [".smc", ".sfc"],
        "libretro": "Nintendo - Super Nintendo Entertainment System"
    },
    "nds": {
        "extensions": [".nds"],
        "libretro": "Nintendo - Nintendo DS"
    },
    "nes": {
        "extensions": [".nes"],
        "libretro": "Nintendo - Nintendo Entertainment System"
    }
}

def clean_game_name(name):
    """Limpiar nombre del ROM para buscar thumbnail"""
    # Quitar extension
    name = re.sub(r'\.[^.]+$', '', name)
    # Quitar region tags
    name = re.sub(r'\s*[\[\(][EUJW]\]?\)?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\((Europe|USA|Japan|World|En|Fr|De|Es|It)[^\)]*\)', '', name, flags=re.IGNORECASE)
    # Quitar version tags
    name = re.sub(r'\s*\[!?\]?', '', name)
    name = re.sub(r'\s*\(Rev\s*\d*\)', '', name, flags=re.IGNORECASE)
    # Limpiar caracteres especiales
    name = name.replace('_', ' ')
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def get_name_variations(name):
    """Generar variaciones del nombre para buscar"""
    clean = clean_game_name(name)
    variations = [clean]

    # Variacion con guion
    if ' - ' not in clean:
        words = clean.split(' ')
        if len(words) > 1:
            variations.append(words[0] + ' - ' + ' '.join(words[1:]))

    # Sin "The" al principio
    if clean.startswith('The '):
        variations.append(clean[4:])

    # Traducciones comunes ES -> EN
    translations = {
        'Pokemon Esmeralda': 'Pokemon - Emerald Version',
        'Pokemon Rojo Fuego': 'Pokemon - FireRed Version',
        'Pokemon Verde Hoja': 'Pokemon - LeafGreen Version',
        'Pokemon Zafiro': 'Pokemon - Sapphire Version',
        'Pokemon Rubi': 'Pokemon - Ruby Version',
    }

    for es, en in translations.items():
        if es.lower() in clean.lower():
            variations.append(en)

    return list(set(variations))

def download_thumbnail(system_libretro, game_name, output_path):
    """Intentar descargar thumbnail de libretro"""
    variations = get_name_variations(game_name)
    base_url = "https://thumbnails.libretro.com"

    types = ["Named_Boxarts", "Named_Snaps", "Named_Titles"]

    for name in variations:
        encoded_name = urllib.parse.quote(name)
        encoded_system = urllib.parse.quote(system_libretro)

        for thumb_type in types:
            url = f"{base_url}/{encoded_system}/{thumb_type}/{encoded_name}.png"

            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(response.read())
                        return True
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
                continue

    return False

def main():
    print("=== Descargador de Thumbnails para ROMs ===\n")

    total_found = 0
    total_downloaded = 0
    total_failed = 0

    for console, info in CONSOLES.items():
        console_path = os.path.join(ROMS_DIR, console)
        if not os.path.exists(console_path):
            print(f"[SKIP] Carpeta no existe: {console_path}")
            continue

        print(f"\n--- {console.upper()} ({info['libretro']}) ---")

        # Listar ROMs
        roms = []
        for file in os.listdir(console_path):
            if any(file.lower().endswith(ext) for ext in info['extensions']):
                roms.append(file)

        roms.sort()
        print(f"Encontrados: {len(roms)} ROMs")
        total_found += len(roms)

        for i, rom in enumerate(roms, 1):
            # Nombre base sin extension para el thumbnail
            base_name = re.sub(r'\.[^.]+$', '', rom)
            thumb_path = os.path.join(THUMBNAILS_DIR, console, f"{base_name}.png")

            # Saltar si ya existe
            if os.path.exists(thumb_path):
                print(f"  [{i}/{len(roms)}] {base_name[:40]}... [EXISTE]")
                total_downloaded += 1
                continue

            print(f"  [{i}/{len(roms)}] {base_name[:40]}...", end=" ", flush=True)

            if download_thumbnail(info['libretro'], rom, thumb_path):
                print("[OK]")
                total_downloaded += 1
            else:
                print("[NO ENCONTRADO]")
                total_failed += 1

    print(f"\n=== RESUMEN ===")
    print(f"Total ROMs: {total_found}")
    print(f"Thumbnails descargados: {total_downloaded}")
    print(f"No encontrados: {total_failed}")
    print(f"\nThumbnails guardados en: {THUMBNAILS_DIR}")

if __name__ == "__main__":
    main()
