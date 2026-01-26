# ROM Server

Un servidor web ligero y autoalojado para gestionar y jugar tus ROMs directamente desde el navegador usando EmulatorJS.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## Caracteristicas

- **Interfaz web moderna** - Navega por tus ROMs organizados por consola
- **Emulacion en el navegador** - Juega directamente sin instalar nada gracias a EmulatorJS
- **100% autoalojado** - Tus ROMs se quedan en tu servidor, no se suben a ningun sitio
- **Ligero** - Solo usa nginx:alpine (~20MB)
- **Busqueda integrada** - Encuentra tus juegos rapidamente
- **Responsive** - Funciona en PC, tablet y movil
- **Descarga de ROMs** - Descarga ROMs individuales o packs completos por consola (ZIP)
- **Thumbnails** - Muestra caratulas de los juegos (desde libretro-thumbnails o locales)
- **Escaneo de biblioteca** - Boton para re-escanear y detectar nuevos juegos
- **Autenticacion** - Proteccion con usuario y contrasena (opcional)

## Consolas soportadas

| Consola | Extensiones | Core EmulatorJS |
|---------|-------------|-----------------|
| Game Boy Advance | `.gba` | mgba |
| Game Boy / Game Boy Color | `.gb`, `.gbc` | gambatte |
| Super Nintendo | `.smc`, `.sfc` | snes9x |
| Nintendo DS | `.nds` | melonds |
| NES | `.nes` | fceumm |
| Sega Genesis | `.md`, `.bin` | genesis_plus_gx |
| PlayStation | `.bin`, `.cue` | pcsx_rearmed |

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

### 2. Organiza tus ROMs

Crea una carpeta con tus ROMs organizados por consola:

```
/ruta/a/tus/roms/
├── gba/
│   ├── Pokemon Esmeralda.gba
│   └── Mario Kart.gba
├── gbc/
│   ├── Pokemon Amarillo.gbc
│   └── Zelda Links Awakening.gbc
├── snes/
│   ├── Super Mario World.smc
│   └── Chrono Trigger.sfc
└── nds/
    ├── Pokemon Platino.nds
    └── Mario Kart DS.nds
```

### 3. Configura docker-compose.yml

Edita `docker-compose.yml` y cambia la ruta de los ROMs:

```yaml
volumes:
  - /TU/RUTA/A/ROMS:/usr/share/nginx/html/roms:ro
```

### 4. Inicia el servidor

```bash
docker compose up -d
```

### 5. Accede desde el navegador

Abre `http://TU_IP:4500` en tu navegador.

## Estructura del proyecto

```
rom-server/
├── docker-compose.yml    # Configuracion de Docker
├── config/
│   ├── nginx.conf        # Configuracion de nginx
│   └── index.html        # Interfaz web
└── README.md
```

## Autenticacion

El servidor puede protegerse con usuario y contrasena usando autenticacion basica de nginx.

### Credenciales por defecto

- **Usuario:** `gamer`
- **Contrasena:** `gamer123`

### Configurar autenticacion

1. Genera el archivo `.htpasswd`:

```bash
# Instala htpasswd si no lo tienes
apt install apache2-utils

# Crea el archivo con tu usuario
htpasswd -c config/.htpasswd tu_usuario
```

2. Anade el volumen en `docker-compose.yml`:

```yaml
volumes:
  - ./config/.htpasswd:/etc/nginx/.htpasswd:ro
```

3. Asegurate que `nginx.conf` incluya:

```nginx
auth_basic "Zona Privada - Mis ROMs";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### Desactivar autenticacion

Comenta o elimina las lineas de `auth_basic` en `config/nginx.conf`.

## Configuracion avanzada

### Cambiar el puerto

Edita `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Cambia 8080 por el puerto que prefieras
```

### Anadir mas consolas

Edita `config/index.html` y anade la consola en el objeto `CONSOLES`:

```javascript
const CONSOLES = {
    // ... consolas existentes ...
    nes: { name: 'Nintendo NES', core: 'fceumm', extensions: ['.nes'] },
    genesis: { name: 'Sega Genesis', core: 'genesis_plus_gx', extensions: ['.md', '.bin'] }
};
```

Luego crea la carpeta correspondiente en tu directorio de ROMs.

### Thumbnails / Caratulas

Por defecto, los thumbnails se cargan desde [libretro-thumbnails](https://thumbnails.libretro.com/).

Para descargar los thumbnails localmente (mejor rendimiento):

```bash
# Ejecuta el script de descarga
python3 config/download_thumbnails.py
```

Esto descargara las caratulas a la carpeta `thumbnails/` que sera servida por nginx.

### Usar sin internet (offline completo)

Por defecto, EmulatorJS se carga desde CDN. Para uso 100% offline:

1. Descarga EmulatorJS: https://github.com/EmulatorJS/EmulatorJS/releases
2. Extrae en una carpeta `data/`
3. Monta la carpeta en docker-compose:
   ```yaml
   volumes:
     - ./data:/usr/share/nginx/html/data:ro
   ```
4. Cambia en `index.html`:
   ```javascript
   window.EJS_pathtodata = '/data/';
   ```

## Solucion de problemas

### Los juegos no aparecen

1. Verifica que los ROMs esten en la carpeta correcta
2. Comprueba que las extensiones sean correctas (`.gba`, `.smc`, etc.)
3. Revisa los logs: `docker logs emulador`

### Error de CORS

El servidor nginx ya incluye cabeceras CORS. Si tienes problemas:

```bash
docker restart emulador
```

### El emulador no carga

- Verifica tu conexion a internet (EmulatorJS se carga desde CDN)
- Abre la consola del navegador (F12) para ver errores
- Algunos ROMs pueden no ser compatibles

### Nintendo DS muy lento

El emulador de NDS (melonds) es intensivo. Recomendaciones:
- Usa un navegador moderno (Chrome/Firefox actualizado)
- Cierra otras pestanas
- En moviles puede no funcionar bien

## Capturas de pantalla

### Pantalla principal
```
+------------------------------------------+
|              Mis ROMs                    |
+------------------------------------------+
|  +------------+  +------------+          |
|  | Game Boy   |  | Game Boy   |          |
|  | Advance    |  | Color      |          |
|  | 78 juegos  |  | 589 juegos |          |
|  +------------+  +------------+          |
|                                          |
|  +------------+  +------------+          |
|  | Super      |  | Nintendo   |          |
|  | Nintendo   |  | DS         |          |
|  | 164 juegos |  | 38 juegos  |          |
|  +------------+  +------------+          |
+------------------------------------------+
```

### Lista de juegos
```
+------------------------------------------+
| <- Volver    Game Boy Advance (78)       |
+------------------------------------------+
| [Buscar juego...                       ] |
+------------------------------------------+
| Pokemon Esmeralda                        |
| Pokemon Rojo Fuego                       |
| Mario Kart Super Circuit                 |
| Zelda Minish Cap                         |
| ...                                      |
+------------------------------------------+
```

## Tecnologias utilizadas

- **nginx:alpine** - Servidor web ligero
- **EmulatorJS** - Emulacion en el navegador
- **Docker** - Contenedorizacion
- **HTML/CSS/JavaScript** - Interfaz web

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

---

Hecho con mass por [kroryan](https://github.com/kroryan)
