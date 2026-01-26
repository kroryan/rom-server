# ROM Server

Un servidor web ligero y autoalojado para gestionar y jugar tus ROMs directamente desde el navegador usando EmulatorJS.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## Características

- **Interfaz web moderna** - Navega por tus ROMs organizados por consola
- **Emulacion en el navegador** - Juega directamente sin instalar nada gracias a EmulatorJS
- **100% autoalojado** - Tus ROMs se quedan en tu servidor, no se suben a ningun sitio
- **Ligero** - Solo usa nginx:alpine para la web + Python:alpine para subidas
- **Busqueda integrada** - Encuentra tus juegos rapidamente
- **Responsive** - Funciona en PC, tablet y movil
- **Descarga de ROMs** - Descarga ROMs individuales o packs completos por consola (ZIP)
- **Thumbnails** - Muestra caratulas de los juegos (desde libretro-thumbnails o locales)
- **Escaneo de biblioteca** - Boton para re-escanear y detectar nuevos juegos
- **Autenticacion** - Proteccion con usuario y contrasena (opcional)

### Características Avanzadas

- **🔍 Búsqueda manual de thumbnails** - Busca y selecciona thumbnails desde libretro-thumbnails o URLs personalizadas
- **📤 Subida de ROMs** - Sube nuevos juegos directamente desde la interfaz web (cualquier consola)
- **🔍 Escaneo de thumbnails** - Identifica juegos sin caratula y añadelas manualmente
- **🔧 Consola de debug** - Botón flotante para ver logs del servidor en tiempo real
- **💾 Descarga local de thumbnails** - Script Python para descargar thumbnails en lote
- **🎮 Todas las consolas visibles** - Todas las consolas se muestran incluso con 0 juegos para permitir subidas

## Consolas soportados

| Consola | Extensiones | Core EmulatorJS |
|---------|-------------|-----------------|
| Game Boy Advance | `.gba` | mgba |
| Game Boy / Game Boy Color | `.gb`, `.gbc` | gambatte |
| Super Nintendo | `.smc`, `.sfc` | snes9x |
| Nintendo DS | `.nds` | melonds |
| NES | `.nes` | fceumm |

## Requisitos

- Docker y Docker Compose
- ROMs organizados en carpetas por consola
- Conexion a internet (para cargar EmulatorJS desde CDN)

## Instalacion rapida

### 1. Clona el repositorio

```bash
git clone https://github.com/kroryan/rom-server.git
cd rom-server
```

### 2. Configura docker-compose.yml

Edita `docker-compose.yml` y cambia las rutas a tus carpetas:

```yaml
volumes:
  - /TU/RUTA/A/ROMS:/usr/share/nginx/html/roms:rw       # Tus ROMs (rw para permitir subidas)
  - /TU/RUTA/A/thumbnails:/usr/share/nginx/html/thumbnails:rw  # Carpeta para thumbnails
```

### 3. Crea las carpetas necesarias

```bash
# Crear carpeta de ROMs
mkdir -p /TU/RUTA/A/ROMS

# Crear carpeta de thumbnails
mkdir -p /TU/RUTA/A/thumbnails

# (Opcional) Crear subcarpetas para cada consola
mkdir -p /TU/RUTA/A/ROMS/{gba,gbc,snes,nds,nes}
```

> **Nota:** No es necesario crear las carpetas de las consolas. El sistema mostrará todas las consolas disponibles (incluso con 0 juegos) y podrás subir ROMs desde la interfaz web.

### 4. Inicia el servidor

```bash
docker compose up -d
```

### 5. Accede desde el navegador

Abre `http://TU_IP:4500` en tu navegador.

**Credenciales por defecto:**
- Usuario: `gamer`
- Contraseña: `gamer123`

## Uso de la Interfaz

### Empezar sin ROMs (desde cero)

Si acabas de instalar el servidor y no tienes ROMs aún:

1. Todas las consolas aparecerán en la pantalla principal mostrando "0 juegos"
2. Haz clic en cualquier consola (ej: Game Boy Advance)
3. Verás un mensaje indicando que no hay juegos
4. Haz clic en el botón **⬆ Subir ROMs** arriba a la derecha
5. Selecciona la consola donde quieres subir el juego
6. Arrastra tus archivos ROM o haz clic para seleccionarlos
7. Los archivos se subirán automáticamente y aparecerán en la lista

### Búsqueda Manual de Thumbnails

1. Haz clic en el botón 🔍 en la esquina de cualquier tarjeta de juego
2. Se abre un modal con dos opciones:
   - **Buscar URL**: Pega una URL directa de imagen
   - **🔍 Buscar en Libretro**: Busca en la base de datos de libretro-thumbnails
3. Para buscar en libretro:
   - Escribe parte del nombre del juego (ej: "Pokemon Emerald", "Mario Kart")
   - Haz clic en "Buscar"
   - Se muestran miniaturas de los resultados
   - Selecciona una para previsualizar
   - Guarda el thumbnail localmente

### Subida de ROMs

1. Haz clic en el botón ⬆ Subir ROMs
2. Selecciona la consola destino del desplegable
3. Arrastra archivos o haz clic para seleccionar
4. Los archivos se suben automáticamente a la carpeta de la consola

> **Nota:** Los nombres de los ROMs se limpian automáticamente. Los tags de región como `[E]`, `[U]`, `[J]`, `[T+Esp]`, etc. se eliminan para facilitar la búsqueda de thumbnails.

### Escaneo de Thumbnails

1. Desde la vista de cualquier consola, haz clic en 🔍 Escanear Thumbs
2. El sistema analiza qué juegos no tienen thumbnail
3. Para cada juego sin thumbnail, puedes hacer clic en "🔍 Buscar" para añadirlo manualmente

### Consola de Debug

1. Haz clic en el botón 🔧 Debug (abajo izquierda)
2. Se abre un panel con los logs del servidor de subidas en tiempo real
3. Haz clic en 🔄 Refrescar para actualizar los logs

## Descarga de Thumbnails Automática

Para descargar todos los thumbnails automáticamente:

```bash
# Ejecuta el script
python3 download_thumbnails.py
```

Este script:
- Busca en libretro-thumbnails los thumbnails de todos tus ROMs
- Aplica traducciones automáticas (ES -> EN)
- Elimina tags de región ([E], [U], [J], etc.) de los nombres
- Guarda los thumbnails localmente para acceso rápido
- Compatible con las extensiones de las consolas soportadas

## Configuracion avanzada

### Cambiar el puerto

Edita `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Cambia 8080 por el puerto que prefieras
```

### Autenticacion

#### Desactivar autenticacion

Edita `config/nginx.conf` y comenta las lineas de auth_basic:

```nginx
# auth_basic "Zona Privada - Mis ROMs";
# auth_basic_user_file /etc/nginx/.htpasswd;
```

#### Cambiar credenciales

```bash
# Genera nuevo archivo .htpasswd
htpasswd -c .htpasswd nuevo_usuario
```

### Modo offline (sin internet)

1. Descarga EmulatorJS: https://github.com/EmulatorJS/EmulatorJS/releases
2. Descomprime y coloca en una carpeta `data/`
3. Añade a docker-compose.yml:
   ```yaml
   volumes:
     - ./data:/usr/share/nginx/html/data:ro
   ```
4. Cambia en `index.html`:
   ```javascript
   window.EJS_pathtodata = '/data/';
   ```

## Estructura del proyecto

```
rom-server/
├── docker-compose.yml        # Configuracion de Docker
├── config/
│   ├── nginx.conf            # Configuracion de nginx
│   ├── index.html            # Interfaz web
│   ├── .htpasswd             # Archivo de autenticacion
│   ├── download_thumbnails.py # Script para descargar thumbnails
│   └── upload_server.py      # Servidor de subidas (Python)
└── README.md
```

## Solucion de problemas

### Los thumbnails no se muestran

1. **Limpiar cache**: Pulsa F12 y ejecuta `localStorage.clear()`
2. **Reescanear**: Usa el botón "🔄 Escanear Biblioteca"
3. **Ver logs**: Abre la consola de debug (🔧 Debug)

### La subida de ROMs no funciona

1. Verifica que el servidor de subidas este corriendo: `docker ps | grep upload-server`
2. Revisa la consola de debug para ver errores
3. Asegúrate de seleccionar la consola correcta antes de subir

### Error de CORS

```bash
docker restart emulador upload-server
```

### El emulador no carga

- Verifica tu conexion a internet
- Abre la consola del navegador (F12) para ver errores
- Algunos ROMs pueden no ser compatibles

## Tecnologias utilizadas

- **nginx:alpine** - Servidor web ligero
- **Python:3-alpine** - Servidor de subidas
- **EmulatorJS** - Emulacion en el navegador
- **Docker** - Contenedorizacion
- **HTML/CSS/JavaScript** - Interfaz web
- **libretro-thumbnails** - Base de datos de thumbnails
- **JSZip** - Creacion de archivos ZIP

## Contribuir

Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -m 'Anade nueva funcion'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## Aviso legal

Este proyecto es solo para uso personal con ROMs que poseas legalmente. No incluye ni distribuye ROMs. El autor no se hace responsable del uso indebido de este software.

## Licencia

MIT License - ver [LICENSE](LICENSE) para mas detalles.

## Creditos

- [EmulatorJS](https://emulatorjs.org/) - Motor de emulacion
- [nginx](https://nginx.org/) - Servidor web
- [libretro-thumbnails](https://thumbnails.libretro.com/) - Base de datos de thumbnails

---

Hecho con ❤️ por [kroryan](https://github.com/kroryan)
