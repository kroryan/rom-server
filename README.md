# ROM Server

Un servidor web ligero y autoalojado para gestionar y jugar tus ROMs directamente desde el navegador usando EmulatorJS.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Consolas Soportadas](#consolas-soportadas)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos Previos](#requisitos-previos)
- [Guía de Instalación Completa](#guía-de-instalación-completa)
- [Primeros Pasos](#primeros-pasos)
- [Guía de Uso Completa](#guía-de-uso-completa)
- [Configuración Avanzada](#configuración-avanzada)
- [Solución de Problemas](#solución-de-problemas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)

---

## 🎮 Características

### Características Principales

- **Interfaz web moderna** - Navega por tus ROMs organizados por consola
- **Emulación en el navegador** - Juega directamente sin instalar nada gracias a EmulatorJS
- **100% autoalojado** - Tus ROMs se quedan en tu servidor, no se suben a ningún sitio
- **Ligero** - Solo usa nginx:alpine para la web + Python:alpine para subidas
- **Búsqueda integrada** - Encuentra tus juegos rápidamente
- **Responsive** - Funciona en PC, tablet y móvil
- **Descarga de ROMs** - Descarga ROMs individuales o packs completos por consola (ZIP)
- **Thumbnails** - Muestra carátulas de los juegos (desde libretro-thumbnails o locales)
- **Escaneo de biblioteca** - Botón para re-escanear y detectar nuevos juegos
- **Autenticación** - Protección con usuario y contraseña (opcional)

### Características Avanzadas

- **🔍 Búsqueda manual de thumbnails** - Busca y selecciona thumbnails desde libretro-thumbnails o URLs personalizadas
- **📤 Subida de ROMs** - Sube nuevos juegos directamente desde la interfaz web (cualquier consola)
- **🔍 Escaneo de thumbnails** - Identifica juegos sin carátula y áñadelas manualmente
- **🔧 Consola de debug** - Botón flotante para ver logs del servidor en tiempo real
- **💾 Descarga local de thumbnails** - Script Python para descargar thumbnails en lote
- **🎮 Todas las consolas visibles** - Todas las consolas se muestran incluso con 0 juegos para permitir subidas
- **🏷️ Filtrado automático de regiones** - Los tags como [E], [U], [J] se eliminan automáticamente de los nombres

---

## 🕹️ Consolas Soportadas

| Consola | Extensiones | Core EmulatorJS | Carpeta |
|---------|-------------|-----------------|---------|
| Game Boy Advance | `.gba` | mgba | `gba/` |
| Game Boy Color | `.gbc` | gambatte | `gbc/` |
| Game Boy | `.gb` | gambatte | `gb/` |
| Super Nintendo | `.smc`, `.sfc` | snes9x | `snes/` |
| Nintendo DS | `.nds` | melonds | `nds/` |
| Nintendo NES | `.nes` | fceumm | `nes/` |
| Nintendo 64 | `.n64`, `.z64`, `.v64` | mupen64plus_next | `n64/` |
| Sega Genesis / Mega Drive | `.genesis`, `.md`, `.smd` | genesis_plus_gx | `genesis/` |
| Sega Master System | `.sms` | genesis_plus_gx | `sms/` |
| Sega Game Gear | `.gg` | genesis_plus_gx | `gg/` |
| Atari 2600 | `.a26` | stella | `atari2600/` |
| PC Engine / TurboGrafx-16 | `.pce` | mednafen_pce_fast | `pce/` |
| Virtual Boy | `.vb` | mednafen_vb | `vb/` |

---

## 🏗️ Arquitectura del Sistema

El servidor ROM consta de dos contenedores Docker que trabajan juntos:

```
┌─────────────────────────────────────────────────────────────┐
│                     Navegador Web                           │
│                  (http://TU_IP:4500)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   Contenedor:        │      │   Contenedor:        │
│   emulador           │      │   upload-server      │
│   (nginx:alpine)     │      │   (python:3-alpine)  │
│                      │      │                      │
│  Puerto: 4500        │      │  Puerto: 8888        │
│                      │      │                      │
│  - Sirve index.html  │      │  - Recibe uploads    │
│  - Sirve ROMs        │◄─────┤  - Guarda ROMs       │
│  - Sirve thumbnails  │      │  - Descarga thumbs   │
└──────────────────────┘      └──────────────────────┘
           │                               │
           ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│  /mnt/Expansion/roms │      │/thumbnails/          │
│  (Archivos ROM)      │      │  (Imágenes)          │
└──────────────────────┘      └──────────────────────┘
```

---

## 📦 Requisitos Previos

### Software Necesario

1. **Docker** - Motor de contenedores
   ```bash
   # Verificar instalación
   docker --version
   ```

2. **Docker Compose** - Orquestación de contenedores
   ```bash
   # Verificar instalación
   docker compose version
   ```

### Hardware Recomendado

- **CPU**: Cualquier procesador moderno (Intel/AMD)
- **RAM**: Mínimo 2GB, recomendado 4GB+
- **Almacenamiento**: Depende de tu colección de ROMs
  - ROMs promedio: 5-50MB por juego
  - Thumbnails: ~50KB por imagen
- **Red**: Conexión a internet (para cargar EmulatorJS desde CDN)

### Permisos Necesarios

- Acceso de lectura/escritura a las carpetas de ROMs y thumbnails
- Puerto 4500 disponible (o el que elijas)
- Puerto 8888 disponible (para el servidor de subidas)

---

## 🚀 Guía de Instalación Completa

### PASO 1: Clonar el Repositorio

Clona el repositorio en tu servidor:

```bash
# Clonar el repositorio
git clone https://github.com/kroryan/rom-server.git
cd rom-server
```

**¿Qué contiene este repositorio?**

```
rom-server/
├── docker-compose.yml        # Configuración de Docker
├── index.html                # Interfaz web principal
├── nginx.conf                # Configuración de nginx
├── .htpasswd                 # Credenciales de autenticación
├── upload_server.py          # Servidor Python para subidas
└── download_thumbnails.py    # Script para descargar thumbnails
```

---

### PASO 2: Preparar las Carpetas

Decide dónde guardarás tus ROMs y thumbnails. En este ejemplo usaremos:

- **ROMs**: `/mnt/Expansion/roms/`
- **Thumbnails**: `/home/kroryan/docker-data/roms-server/thumbnails/`

Crea las carpetas:

```bash
# Crear carpeta principal de ROMs
sudo mkdir -p /mnt/Expansion/roms/

# Crear carpeta de thumbnails
sudo mkdir -p /home/kroryan/docker-data/roms-server/thumbnails/

# (Opcional) Crear subcarpetas para cada consola
sudo mkdir -p /mnt/Expansion/roms/{gba,gbc,gb,snes,nds,nes,n64,genesis,sms,gg,atari2600,pce,vb}

# Dar permisos adecuados (ajusta según tu usuario)
sudo chown -R $USER:$USER /mnt/Expansion/roms/
sudo chown -R $USER:$USER /home/kroryan/docker-data/roms-server/thumbnails/
```

**Importante**: Si vas a usar rutas diferentes, anótalas para el siguiente paso.

---

### PASO 3: Crear el Archivo docker-compose.yml

Crea un archivo llamado `docker-compose.yml` con el siguiente contenido:

```yaml
services:
  emulador:
    image: nginx:alpine
    container_name: emulador
    ports:
      - "4500:80"  # Puerto 4500 en tu sistema -> Puerto 80 en el contenedor
    volumes:
      # ROMs - read-write (rw) para permitir subidas desde la web
      - /mnt/Expansion/roms:/usr/share/nginx/html/roms:rw

      # Thumbnails - read-write (rw) para guardar imágenes descargadas
      - /home/kroryan/docker-data/roms-server/thumbnails:/usr/share/nginx/html/thumbnails:rw

      # Archivos de configuración - read-only (ro) para seguridad
      - /home/kroryan/docker-data/roms-server/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /home/kroryan/docker-data/roms-server/index.html:/usr/share/nginx/html/index.html:ro
      - /home/kroryan/docker-data/roms-server/.htpasswd:/etc/nginx/.htpasswd:ro

      # Temporal de nginx
      - /tmp/nginx:/var/cache/nginx

    # Comando para crear directorios temporales y iniciar nginx
    command: >
      sh -c "
      mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp /var/cache/nginx/fastcgi_temp /var/cache/nginx/uwsgi_temp /var/cache/nginx/scgi_temp &&
      chmod -R 777 /var/cache/nginx &&
      nginx -g 'daemon off;'
      "
    restart: unless-stopped

  upload-server:
    image: python:3-alpine
    container_name: upload-server
    ports:
      - "8888:8080"  # Puerto 8888 en tu sistema -> Puerto 8080 en el contenedor
    volumes:
      # ROMs - read-write (rw) para guardar archivos subidos
      - /mnt/Expansion/roms:/roms:rw

      # Thumbnails - read-write (rw) para guardar imágenes descargadas
      - /home/kroryan/docker-data/roms-server/thumbnails:/thumbnails:rw

      # Script del servidor - read-only (ro)
      - /home/kroryan/docker-data/roms-server/upload_server.py:/app/upload_server.py:ro

    working_dir: /app
    command: ["python3", "upload_server.py"]
    restart: unless-stopped
```

**⚠️ IMPORTANTE**: Debes modificar las rutas en `volumes:` según tu sistema:

| Ruta en el ejemplo | Cámbiala a... |
|-------------------|---------------|
| `/mnt/Expansion/roms` | Tu carpeta de ROMs |
| `/home/kroryan/docker-data/roms-server/thumbnails` | Tu carpeta de thumbnails |
| `/home/kroryan/docker-data/roms-server/nginx.conf` | Donde guardaste nginx.conf |
| `/home/kroryan/docker-data/roms-server/index.html` | Donde guardaste index.html |
| `/home/kroryan/docker-data/roms-server/.htpasswd` | Donde guardaste .htpasswd |
| `/home/kroryan/docker-data/roms-server/upload_server.py` | Donde guardaste upload_server.py |

---

### PASO 4: Colocar los Archivos de Configuración

Asegúrate de que todos los archivos están en sus lugares correctos:

```bash
# Copiar archivos desde el repositorio clonado
cp index.html /home/kroryan/docker-data/roms-server/index.html
cp nginx.conf /home/kroryan/docker-data/roms-server/nginx.conf
cp .htpasswd /home/kroryan/docker-data/roms-server/.htpasswd
cp upload_server.py /home/kroryan/docker-data/roms-server/upload_server.py
cp download_thumbnails.py /home/kroryan/docker-data/roms-server/download_thumbnails.py
```

**Verificar que todos los archivos existen:**

```bash
ls -la /home/kroryan/docker-data/roms-server/
```

Deberías ver:
```
index.html
nginx.conf
.htpasswd
upload_server.py
download_thumbnails.py
thumbnails/
```

---

### PASO 5: Iniciar los Contenedores

```bash
# Iniciar los contenedores en modo detached (segundo plano)
docker compose up -d
```

**¿Qué hace este comando?**

- `docker compose up` - Inicia los servicios definidos
- `-d` - Ejecuta en "detached mode" (en segundo plano)

**Verificar que los contenedores están corriendo:**

```bash
docker ps
```

Deberías ver algo como:

```
CONTAINER ID   IMAGE             STATUS         PORTS
emulador       nginx:alpine      Up 2 minutes   0.0.0.0:4500->80/tcp
upload-server  python:3-alpine   Up 2 minutes   0.0.0.0:8888->8080/tcp
```

---

### PASO 6: Acceder a la Interfaz Web

Abre tu navegador y ve a:

```
http://TU_IP:4500
```

**Ejemplos:**
- `http://192.168.1.100:4500` (IP local típica)
- `http://localhost:4500` (si estás en el mismo servidor)
- `http://rom-server.mi-dominio.com:4500` (si tienes DNS configurado)

### Credenciales por Defecto

```
Usuario: gamer
Contraseña: gamer123
```

---

## 🎯 Primeros Pasos

### Opción A: Ya Tienes ROMs

Si ya tienes ROMs, simplemente cópialas a las carpetas correspondientes:

```bash
# Ejemplo: Copiar ROMs de Game Boy Advance
cp /ruta/a/tus/roms/gba/*.gba /mnt/Expansion/roms/gba/

# Ejemplo: Copiar ROMs de Nintendo DS
cp /ruta/a/tus/roms/nds/*.nds /mnt/Expansion/roms/nds/
```

Luego, en la interfaz web:
1. Haz clic en "🔄 Escanear Biblioteca" (arriba derecha)
2. Los juegos aparecerán automáticamente

### Opción B: Empezar Desde Cero

Si no tienes ROMs aún:

1. **Abre la interfaz web** en `http://TU_IP:4500`
2. **Inicia sesión** con las credenciales por defecto
3. **Verás las 13 consolas** todas mostrando "0 juegos"
4. **Haz clic en cualquier consola** (ej: "Game Boy Advance")
5. **Verás un mensaje** indicando que no hay juegos
6. **Haz clic en "⬆ Subir ROMs"** (arriba derecha)
7. **Selecciona la consola destino** del desplegable
8. **Arrastra tus archivos ROM** o haz clic para seleccionarlos
9. **Los archivos se subirán** automáticamente y aparecerán en la lista

---

## 📖 Guía de Uso Completa

### 1. Pantalla Principal (Consolas)

Al acceder a la web, verás todas las consolas disponibles:

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│   🎮 GBA            │   🟢 GBC            │   🕹️ SNES           │
│   15 juegos         │   8 juegos          │   12 juegos         │
│   ⬇ Descargar Pack  │   ⬇ Descargar Pack  │   ⬇ Descargar Pack  │
├─────────────────────┼─────────────────────┼─────────────────────┤
│   📱 NDS            │   🕹️ NES            │   🎯 N64            │
│   0 juegos          │   5 juegos          │   3 juegos          │
│   ⬇ Sin juegos      │   ⬇ Descargar Pack  │   ⬇ Descargar Pack  │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

**Botones disponibles:**
- **🔄 Escanear Biblioteca** (arriba derecha) - Reescanea todas las consolas para detectar nuevos juegos
- **⬆ Subir ROMs** (arriba derecha) - Abre el modal para subir nuevos juegos

**Comportamiento:**
- Consolas con juegos: Muestra "⬇ Descargar Pack" (activo)
- Consolas vacías: Muestra "⬇ Sin juegos" (inactivo, gris)
- Haz clic en cualquier consola para ver sus juegos

---

### 2. Vista de Juegos de una Consola

Al hacer clic en una consola, verás sus juegos en una rejilla:

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Volver    Game Boy Advance (15 juegos)     ⬆ Subir ROMs      │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 [Buscar juegos...]                                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ [IMAGEN] │  │ [IMAGEN] │  │ [ICONO]  │  │ [IMAGEN] │       │
│  │          │  │          │  │   🎮     │  │          │       │
│  │ Pokemon  │  │ Mario    │  │ Zelda    │  │ Metroid  │       │
│  │ ▶Jugar   │  │ ▶Jugar   │  │ ▶Jugar   │  │ ▶Jugar   │       │
│  │ ⬇ROM     │  │ ⬇ROM     │  │ ⬇ROM     │  │ ⬇ROM     │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

**Elementos de cada tarjeta de juego:**
- **🔍** (esquina superior derecha) - Buscar thumbnail manualmente
- **Carátula del juego** - Haz clic para jugar
- **Nombre del juego** - Haz clic para jugar
- **▶ Jugar** - Lanzar el emulador
- **⬇ ROM** - Descargar el archivo ROM

---

### 3. Jugar un Juego

1. **Haz clic** en "▶ Jugar" o en la carátula del juego
2. **Se abrirá el emulador** en pantalla completa
3. **Controles por defecto:**
   - **Flechas direccionales** - Movimiento
   - **Z** - Botón A
   - **X** - Botón B
   - **Enter** - Start
   - **Shift** - Select
4. **Cerrar el emulador:**
   - Haz clic en "✖ Cerrar" (arriba derecha)

---

### 4. Subir ROMs

1. **Haz clic en "⬆ Subir ROMs"** (disponible desde cualquier pantalla)
2. **Se abrirá el modal de subida:**
   ```
   ┌─────────────────────────────────────┐
   │     ⬆ Subir ROMs                   │
   ├─────────────────────────────────────┤
   │ Consola: [Game Boy Advance ▼]      │
   │                                     │
   │  ╔══════════════════════════════╗   │
   │  ║   Arrastra archivos aquí     ║   │
   │  ║   o haz clic para seleccionar ║   │
   │  ╚══════════════════════════════╝   │
   │                                     │
   │ Archivos seleccionados:             │
   │ • Pokemon.gba            [Eliminar] │
   │ • Zelda.gba              [Eliminar] │
   │                                     │
   │ Nota: Los nombres se limpiarán     │
   │ automáticamente [E], [U], etc.      │
   │                                     │
   │ [Cancelar]  [Subir 2 archivos]      │
   └─────────────────────────────────────┘
   ```
3. **Selecciona la consola destino** del desplegable
4. **Arrastra archivos** o haz clic para seleccionar
5. **Haz clic en "Subir"**
6. **Los archivos se guardarán** en la carpeta de la consola

---

### 5. Buscar y Añadir Thumbnails

#### Método A: Buscar en Libretro (Recomendado)

1. **Haz clic en 🔍** en la esquina de cualquier tarjeta de juego
2. **En el modal, haz clic en "🔍 Buscar en Libretro"**
3. **Se abrirá el buscador de libretro:**
   ```
   ┌─────────────────────────────────────────────┐
   │     🔍 Buscar en Libretro                  │
   ├─────────────────────────────────────────────┤
   │ Nombre: [Pokemon Emerald          ] [Buscar]│
   │                                             │
   │ Resultados:                                 │
   │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐           │
   │  │ IMG │ │ IMG │ │ IMG │ │ IMG │           │
   │  │Emer.│ │Ruby │ │Saph.│ │FireR│           │
   │  └─────┘ └─────┘ └─────┘ └─────┘           │
   │                                             │
   │ [Cancelar]              [Seleccionar]       │
   └─────────────────────────────────────────────┘
   ```
4. **Escribe parte del nombre** del juego (ej: "Pokemon Emerald")
5. **Haz clic en "Buscar"**
6. **Selecciona una imagen** de la rejilla
7. **Haz clic en "Seleccionar"**
8. **La imagen se guardará** localmente

#### Método B: URL Directa

1. **Haz clic en 🔍** en la esquina de cualquier tarjeta de juego
2. **Pega una URL directa de imagen** (ej: `https://example.com/image.png`)
3. **Haz clic en "Buscar"**
4. **La imagen se previsualizará**
5. **Haz clic en "Guardar"**

---

### 6. Escanear Thumbnails Faltantes

1. **Desde la vista de cualquier consola**, haz clic en **🔍 Escanear Thumbs**
2. **El sistema analizará** qué juegos no tienen thumbnail
3. **Se mostrará una lista** de juegos sin carátula
4. **Para cada juego**, puedes hacer clic en "🔍 Buscar" para añadirlo manualmente

---

### 7. Consola de Debug

1. **Haz clic en el botón 🔧 Debug** (abajo izquierda)
2. **Se abrirá un panel flotante** con los logs del servidor
3. **Haz clic en 🔄 Refrescar** para actualizar los logs

**Útil para:**
- Verificar que las subidas funcionan correctamente
- Diagnosticar errores de thumbnails
- Monitorizar la actividad del servidor

---

### 8. Descargar Packs de ROMs

1. **Desde la pantalla principal**, cada consola tiene un botón "⬇ Descargar Pack"
2. **Haz clic en él** para descargar todas las ROMs de esa consola en un archivo ZIP
3. **El ZIP se generará** automáticamente y se descargará a tu ordenador

---

### 9. Descargar ROMs Individuales

1. **Desde la vista de juegos**, haz clic en **⬇ ROM** en cualquier tarjeta
2. **La ROM se descargará** directamente a tu ordenador

---

## ⚙️ Configuración Avanzada

### Cambiar el Puerto

Edita `docker-compose.yml`:

```yaml
services:
  emulador:
    ports:
      - "8080:80"  # Cambia 8080 por el puerto que prefieras
```

Luego reinicia:

```bash
docker compose down
docker compose up -d
```

Ahora accede a `http://TU_IP:8080`

---

### Cambiar Credenciales de Autenticación

#### Opción A: Generar nuevas credenciales

```bash
# Instalar apache2-utils (si no está instalado)
sudo apt-get install apache2-utils  # Debian/Ubuntu
sudo yum install httpd-tools         # CentOS/RHEL

# Generar nuevo archivo .htpasswd
htpasswd -c /home/kroryan/docker-data/roms-server/.htpasswd nuevo_usuario

# Se te pedirá que introduzcas la contraseña dos veces
```

Reinicia el contenedor:

```bash
docker restart emulador
```

#### Opción B: Desactivar autenticación

⚠️ **No recomendado para servidores accesibles desde internet**

Edita `nginx.conf` y comenta las líneas de auth_basic:

```nginx
# auth_basic "Zona Privada - Mis ROMs";
# auth_basic_user_file /etc/nginx/.htpasswd;
```

Reinicia el contenedor:

```bash
docker restart emulador
```

---

### Modo Offline (Sin Internet)

Si no tienes conexión a internet o prefieres no depender del CDN:

1. **Descarga EmulatorJS:**
   ```bash
   wget https://github.com/EmulatorJS/EmulatorJS/releases/latest/download/data.zip
   unzip data.zip -d /home/kroryan/docker-data/roms-server/data
   ```

2. **Añade el volumen en docker-compose.yml:**
   ```yaml
   volumes:
     - /home/kroryan/docker-data/roms-server/data:/usr/share/nginx/html/data:ro
   ```

3. **Edita `index.html` y cambia:**
   ```javascript
   window.EJS_pathtodata = '/data/';
   ```

4. **Reinicia:**
   ```bash
   docker compose down
   docker compose up -d
   ```

---

### Descargar Thumbnails Automáticamente

Para descargar todos los thumbnails de tu colección:

```bash
# Ejecutar el script
python3 download_thumbnails.py
```

**Lo que hace este script:**
- Busca en libretro-thumbnails los thumbnails de todos tus ROMs
- Aplica traducciones automáticas (ES -> EN)
- Elimina tags de región ([E], [U], [J], etc.) de los nombres
- Guarda los thumbnails localmente para acceso rápido
- Compatible con todas las extensiones de las consolas soportadas

---

## 🔧 Solución de Problemas

### Los thumbnails no se muestran

**Síntoma:** Las tarjetas de juego muestran un icono en lugar de la carátula.

**Soluciones:**

1. **Limpiar cache del navegador:**
   - Presiona `F12` para abrir las herramientas de desarrollador
   - En la consola, escribe: `localStorage.clear()`
   - Recarga la página (`F5`)

2. **Reescanear la biblioteca:**
   - Haz clic en "🔄 Escanear Biblioteca" (arriba derecha)

3. **Ver los logs:**
   - Abre la consola de debug (🔧 Debug, abajo izquierda)
   - Busca errores relacionados con thumbnails

---

### La subida de ROMs no funciona

**Síntoma:** Al intentar subir una ROM, no aparece en la lista.

**Soluciones:**

1. **Verificar que el servidor de subidas está corriendo:**
   ```bash
   docker ps | grep upload-server
   ```
   Si no aparece, inicia:
   ```bash
   docker compose up -d upload-server
   ```

2. **Revisar la consola de debug:**
   - Abre 🔧 Debug
   - Busca errores como "Permission denied" o "No such file"

3. **Verificar permisos:**
   ```bash
   ls -la /mnt/Expansion/roms/
   ```
   Asegúrate de que tu usuario tiene permisos de escritura.

4. **Asegúrate de seleccionar la consola correcta** antes de subir.

---

### Error de CORS

**Síntoma:** Error en la consola del navegador: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solución:**

```bash
docker restart emulador upload-server
```

---

### El emulador no carga

**Síntoma:** Al hacer clic en "▶ Jugar", el emulador no se inicia.

**Soluciones:**

1. **Verificar conexión a internet:**
   - EmulatorJS se carga desde CDN
   - Si no hay internet, usa el [Modo Offline](#modo-offline-sin-internet)

2. **Abrir la consola del navegador:**
   - Presiona `F12`
   - Busca errores en la pestaña "Console"

3. **Verificar que el ROM es compatible:**
   - Algunos ROMs pueden no ser compatibles
   - Prueba con otro ROM de la misma consola

4. **Limpiar cache:**
   - `Ctrl + Shift + Del`
   - Selecciona "Imágenes y archivos en caché"
   - Haz clic en "Borrar datos"

---

### Contenedor no inicia

**Síntoma:** `docker compose up -d` muestra un error.

**Soluciones:**

1. **Verificar que los puertos están disponibles:**
   ```bash
   netstat -tuln | grep -E '4500|8888'
   ```
   Si están en uso, cambia los puertos en `docker-compose.yml`

2. **Verificar que las rutas en volumes son correctas:**
   ```bash
   ls -la /mnt/Expansion/roms/
   ls -la /home/kroryan/docker-data/roms-server/
   ```

3. **Ver los logs del contenedor:**
   ```bash
   docker logs emulador
   docker logs upload-server
   ```

---

### Cannot connect to the Docker daemon

**Síntoma:** Error al ejecutar comandos de Docker.

**Solución:**

```bash
# Iniciar el servicio Docker
sudo systemctl start docker

# Habilitar Docker para que inicie automáticamente
sudo systemctl enable docker

# Añadir tu usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER

# Cerrar sesión y volver a iniciar para aplicar cambios
```

---

## 📁 Estructura del Proyecto

```
rom-server/
├── docker-compose.yml        # Configuración de Docker Compose
├── index.html                # Interfaz web principal (~1400 líneas)
├── nginx.conf                # Configuración de nginx
├── .htpasswd                 # Archivo de autenticación
├── upload_server.py          # Servidor Python para subidas
├── download_thumbnails.py    # Script para descargar thumbnails
├── LICENSE                   # Licencia MIT
└── README.md                 # Este archivo
```

### Estructura en el Servidor

```
/mnt/Expansion/roms/                    # Carpeta principal de ROMs
├── gba/                                # Game Boy Advance
│   ├── Pokemon Emerald.gba
│   └── Mario Kart Super Circuit.gba
├── gbc/                                # Game Boy Color
│   └── Pokemon Yellow.gbc
├── gb/                                 # Game Boy
│   └── Tetris.gb
├── snes/                               # Super Nintendo
│   └── Super Mario World.smc
├── nds/                                # Nintendo DS
│   └── Pokemon Platinum.nds
├── nes/                                # Nintendo NES
│   └── Super Mario Bros.nes
├── n64/                                # Nintendo 64
│   └── Super Mario 64.z64
├── genesis/                            # Sega Genesis / Mega Drive
│   └── Sonic the Hedgehog.md
├── sms/                                # Sega Master System
│   └── Alex Kidd in Miracle World.sms
├── gg/                                 # Sega Game Gear
│   └── Sonic.gg
├── atari2600/                          # Atari 2600
│   └── Pac-Man.a26
├── pce/                                # PC Engine / TurboGrafx-16
│   └── Bomberman.pce
└── vb/                                 # Virtual Boy
    └── Mario's Tennis.vb

/home/kroryan/docker-data/roms-server/
├── thumbnails/                         # Carpeta de thumbnails
│   ├── gba/
│   │   ├── Pokemon Emerald.png
│   │   └── Mario Kart Super Circuit.png
│   └── gbc/
│       └── Pokemon Yellow.png
├── index.html                          # Interfaz web
├── nginx.conf                          # Configuración nginx
├── .htpasswd                           # Credenciales
├── upload_server.py                    # Servidor de subidas
└── download_thumbnails.py              # Script de thumbnails
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso | Versión |
|------------|-----|---------|
| **nginx:alpine** | Servidor web | Latest |
| **Python:3-alpine** | Servidor de subidas | 3.x |
| **EmulatorJS** | Emulación en navegador | Latest (CDN) |
| **Docker** | Contenedorización | 20.x+ |
| **Docker Compose** | Orquestación | 2.x+ |
| **HTML/CSS/JavaScript** | Interfaz web | ES6+ |
| **libretro-thumbnails** | Base de datos de thumbnails | - |
| **JSZip** | Creación de archivos ZIP | 3.10.1 |

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver [LICENSE](LICENSE) para más detalles.

---

## ⚖️ Aviso Legal

Este proyecto es solo para uso personal con ROMs que poseas legalmente.

- **NO** incluye ni distribuye ROMs
- **NO** facilita la descarga de ROMs protegidas por copyright
- **NO** se hace responsable del uso indebido de este software

**Uso permitido:**
- Juegos que poseas en formato físico (cartuchos, discos)
- ROMs de dominio público
- ROMs que hayas creado tú mismo
- Homebrew y juegos independientes

---

## 🙏 Créditos

- **[EmulatorJS](https://emulatorjs.org/)** - Motor de emulación en el navegador
- **[nginx](https://nginx.org/)** - Servidor web de alto rendimiento
- **[libretro-thumbnails](https://thumbnails.libretro.com/)** - Base de datos de thumbnails
- **[RetroArch](https://www.libretro.com/)** - Cores de emulación

---

## 🤝 Contribuir

Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcion'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisa la sección [Solución de Problemas](#solución-de-problemas)
2. Busca [issues existentes](https://github.com/kroryan/rom-server/issues)
3. Crea un nuevo issue con:
   - Descripción detallada del problema
   - Pasos para reproducirlo
   - Logs relevantes
   - Tu sistema operativo y versión de Docker

---

**Hecho con ❤️ por [kroryan](https://github.com/kroryan)**

---

## 📝 Historial de Cambios

### v1.0.0 (Última)
- 13 consolas soportadas
- Subida de ROMs desde la interfaz web
- Búsqueda de thumbnails en libretro-thumbnails
- Escaneo de thumbnails faltantes
- Consola de debug en tiempo real
- Filtrado automático de tags de región
- Todas las consolas visibles (incluso con 0 juegos)
- Descarga de packs completos por consola
