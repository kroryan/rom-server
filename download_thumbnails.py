#!/usr/bin/env python3
"""
Descarga thumbnails de libretro para todos los ROMs.
Versión mejorada que intenta directamente sin lista completa.
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from difflib import SequenceMatcher

# Configuracion
ROMS_DIR = "/mnt/Expansion/roms"
THUMBNAILS_DIR = "/home/kroryan/docker-data/roms-server/thumbnails"

CONSOLES = {
    "gba": {
        "extensions": [".gba"],
        "libretro": "Nintendo_-_Game_Boy_Advance"
    },
    "gbc": {
        "extensions": [".gbc", ".gb"],
        "libretro": "Nintendo_-_Game_Boy_Color"
    },
    "snes": {
        "extensions": [".smc", ".sfc"],
        "libretro": "Nintendo_-_Super_Nintendo_Entertainment_System"
    },
    "nds": {
        "extensions": [".nds"],
        "libretro": "Nintendo_-_Nintendo_DS"
    },
    "nes": {
        "extensions": [".nes"],
        "libretro": "Nintendo_-_Nintendo_Entertainment_System"
    }
}

# Variaciones de nombres a intentar para cada ROM
# Patrones comunes de nombres en libretro
NAME_PATTERNS = [
    # Original limpio
    "{clean}",
    # Con region
    "{clean} (USA)",
    "{clean} (USA, Europe)",
    "{clean} (Europe)",
    "{clean} (Europe) (En)",
    "{clean} (Japan)",
    # Traducido con title case
    "{translated_title}",
    "{translated_title} (USA)",
    "{translated_title} (USA, Europe)",
    "{translated_title} (Europe)",
    # Traducido en lowercase
    "{translated}",
    "{translated} (USA)",
    "{translated} (USA, Europe)",
    "{translated} (Europe)",
    # Para juegos con "Version" añadida (ej: Pokemon Emerald Version)
    "{translated_title} Version (USA, Europe)",
    "{translated_title} Version (USA)",
    "{translated_title} Version (Europe)",
    "{translated_title} Version",
    # Formato con guion (ej: "Mario - Kart Super Circuit")
    "{first_word} - {rest}",
    "{first_word} - {rest} (USA, Europe)",
    "{first_word} - {rest} (Europe)",
    "{first_word} - {rest} (USA)",
    # Nombre original del archivo
    "{original}",
]

# Traducciones comunes ES/EU -> EN
TRANSLATIONS = {
    # Pokemon
    'esmeralda': 'emerald',
    'rojo': 'red',
    'fuego': 'fire',
    'verde': 'green',
    'hoja': 'leaf',
    'zafiro': 'sapphire',
    'rubi': 'ruby',
    'diamante': 'diamond',
    'perla': 'pearl',
    'platino': 'platinum',
    'oro': 'gold',
    'plata': 'silver',
    'cristal': 'crystal',
    'negro': 'black',
    'blanco': 'white',
    'mundo': 'world',
    'misterioso': 'mystery',
    'dungeon': 'dungeon',
    # Mario
    'hermanos': 'bros',
    'hermano': 'brother',
    'hermana': 'sister',
    # Zelda
    'un enlace al pasado': 'a link to the past',
    'despertar del enlace': "link's awakening",
    'el': 'the',
    'la': 'the',
    'los': 'the',
    'las': 'the',
    'y': 'and',
    'de': 'of',
    'del': 'of the',
    'en': 'in',
    'aventura': 'adventure',
    'guerrero': 'warrior',
    'batalla': 'battle',
    'caballero': 'knight',
}

def clean_name(name):
    """Limpiar nombre para comparacion"""
    # Quitar extension
    name = re.sub(r'\.[^.]+$', '', name)
    # Quitar tags de region
    name = re.sub(r'\s*[\[\(][EUJWS!]\]?\)?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\((Europe|USA|Japan|World|En|Fr|De|Es|It|Eu)[^\)]*\)', '', name, flags=re.IGNORECASE)
    # Quitar tags de version
    name = re.sub(r'\s*\(Rev\s*\d*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(v[\d\.]+\)', '', name, flags=re.IGNORECASE)
    # Caracteres especiales
    name = name.replace('_', ' ')
    name = re.sub(r"[':!,\.\-]+", ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def translate_name(name):
    """Traducir nombre de ES a EN"""
    words = name.lower().split()
    translated = []
    for word in words:
        # Si la palabra esta en el diccionario, reemplazarla
        translated.append(TRANSLATIONS.get(word, word))
    return ' '.join(translated)

def get_possible_names(rom_filename):
    """Generar lista de posibles nombres a intentar"""
    base_name = re.sub(r'\.[^.]+$', '', rom_filename)
    clean = clean_name(rom_filename)
    translated = translate_name(clean)

    # Extraer primera palabra y el resto para patrones especiales
    words = translated.split()
    first_word = words[0].title() if words else ""
    rest = ' '.join(words[1:]) if len(words) > 1 else ""
    translated_title = translated.title()

    possible = []

    # PATRONES ESPECIALES PARA POKEMON
    # Pokemon tiene un formato especial: "Pokemon - X Version (USA, Europe)"
    if translated.lower().startswith('pokemon') and len(words) >= 2:
        # La segunda palabra es el nombre del juego (Emerald, Ruby, etc)
        pokemon_name = words[1].title()
        # "Pokemon - Emerald Version (USA, Europe)"
        possible.append(f"Pokemon - {pokemon_name} Version (USA, Europe)")
        possible.append(f"Pokemon - {pokemon_name} Version (USA)")
        possible.append(f"Pokemon - {pokemon_name} Version (Europe)")
        possible.append(f"Pokemon - {pokemon_name} Version")
        possible.append(f"Pokemon - {pokemon_name} (USA, Europe)")
        possible.append(f"Pokemon - {pokemon_name} (USA)")
        possible.append(f"Pokemon - {pokemon_name} (Europe)")
        possible.append(f"Pokemon - {pokemon_name}")

    # PATRONES GENERALES
    for pattern in NAME_PATTERNS:
        try:
            name = pattern.format(
                clean=clean,
                translated=translated,
                translated_title=translated_title,
                original=base_name,
                first_word=first_word,
                rest=rest
            )
            if name and name not in possible:
                possible.append(name)
        except KeyError:
            # Si el patron tiene una clave que no tenemos, saltar
            pass

    return possible

def download_thumbnail(system_libretro, game_name, output_path):
    """Descargar thumbnail desde libretro GitHub"""
    repo_name = system_libretro
    base_url = f"https://raw.githubusercontent.com/libretro-thumbnails/{repo_name}/master"

    types = ["Named_Boxarts", "Named_Snaps", "Named_Titles"]

    for thumb_type in types:
        # GitHub usa espacios URL-encoded
        encoded_name = urllib.parse.quote(game_name + '.png')
        url = f"{base_url}/{thumb_type}/{encoded_name}"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.read())
                    return True, thumb_type
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            else:
                raise
        except Exception:
            continue

    return False, None

def main():
    print("=== Descargador de Thumbnails para ROMs (v3 - Directo) ===\n")

    total_found = 0
    total_downloaded = 0
    total_failed = 0

    for console, info in CONSOLES.items():
        console_path = os.path.join(ROMS_DIR, console)
        if not os.path.exists(console_path):
            print(f"[SKIP] Carpeta no existe: {console_path}")
            continue

        print(f"\n=== {console.upper()} ===")

        # Listar ROMs
        roms = []
        for file in sorted(os.listdir(console_path)):
            if any(file.lower().endswith(ext) for ext in info['extensions']):
                roms.append(file)

        print(f"ROMs locales: {len(roms)}\n")
        total_found += len(roms)

        for i, rom in enumerate(roms, 1):
            base_name = re.sub(r'\.[^.]+$', '', rom)
            thumb_path = os.path.join(THUMBNAILS_DIR, console, f"{base_name}.png")

            # Saltar si ya existe
            if os.path.exists(thumb_path):
                print(f"  [{i}/{len(roms)}] {base_name[:45]:<45} [EXISTE]")
                total_downloaded += 1
                continue

            print(f"  [{i}/{len(roms)}] {base_name[:45]:<45}", end=" ", flush=True)

            # Obtener nombres posibles y probar cada uno
            possible_names = get_possible_names(rom)
            success = False
            tried = []

            for name in possible_names[:15]:  # Limitar a 15 intentos
                if name in tried:
                    continue
                tried.append(name)
                ok, thumb_type = download_thumbnail(info['libretro'], name, thumb_path)
                if ok:
                    short_name = name[:30] + "..." if len(name) > 30 else name
                    print(f"[OK] {short_name}")
                    total_downloaded += 1
                    success = True
                    break

            if not success:
                print("[NO ENCONTRADO]")
                total_failed += 1

    print(f"\n=== RESUMEN ===")
    print(f"Total ROMs: {total_found}")
    print(f"Thumbnails: {total_downloaded}")
    print(f"No encontrados: {total_failed}")
    print(f"\nGuardados en: {THUMBNAILS_DIR}")

if __name__ == "__main__":
    main()
