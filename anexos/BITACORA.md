# Bitácora de desarrollo

Registro de las decisiones, conceptos y problemas resueltos durante el desarrollo de TeamUp.

---

## Sesión del 6 de octubre de 2026

### 1. Estructura MVC

El código vive en la carpeta `teamup/`, que es un paquete de Python (por eso va en minúsculas).

```
TeamUp/
├── run.py              crea y arranca la app
└── teamup/
    ├── __init__.py     create_app()
    ├── extensions.py   db = SQLAlchemy()
    ├── models/         M - clases que representan las tablas
    ├── controllers/    C - rutas que reciben la petición y deciden qué hacer
    ├── templates/      V - archivos HTML que se muestran con render_template
    └── static/         CSS, JavaScript e imágenes
```

**¿Por qué `templates` y no `views`?**

- `render_template()` busca los HTML en una carpeta llamada `templates` por defecto. Se puede cambiar con `Flask(__name__, template_folder="views")`, pero se dejó la convención.
- En Flask, la palabra *view* se usa para la función que atiende una ruta (lo que en MVC es el controlador), así que llamar `views` a la carpeta de HTML confunde.

| MVC | En el proyecto |
|---|---|
| Modelo | `teamup/models/` |
| Vista | `teamup/templates/` |
| Controlador | `teamup/controllers/` (por ahora las rutas están en `__init__.py`) |

### 2. Application factory

Siguiendo la documentación de Flask, la app no se crea suelta sino dentro de una función:

```python
def create_app():
    app = Flask(__name__)
    # configuración, base de datos, rutas...
    return app
```

- `create_app()` va en `teamup/__init__.py`.
- `run.py`, fuera del paquete, es el **único punto de entrada**: importa `create_app`, crea la app y la arranca.
- Se eliminó un `teamup/app.py` que duplicaba lo que hace `run.py`.
- `if __name__ == "__main__":` hace que el servidor solo arranque cuando se ejecuta `python run.py` directamente.

### 3. Rutas públicas y privadas (Entrega 1)

Se evaluó dejar Explorar y Vitrina públicas y pedir login solo para acciones. Se descartó para esta entrega porque implica más programación (la barra superior tendría que cambiar según haya sesión o no).

**Decisión:** solo el landing, el login y el registro son públicos. Todo lo demás exige sesión.

| Pública | Privada |
|---|---|
| `/` landing | Explorar (página principal después del login) |
| `/login` | Foro, Vitrina, Mis proyectos (CRUD), Mi perfil |
| `/register` | |

Si alguien entra a una URL privada sin sesión, se le redirige al login. Más adelante, abrir Explorar o Vitrina solo requiere agregarlas a la lista de rutas públicas.

### 4. Vistas y Jinja

Se permite usar sintaxis Jinja en las vistas. El caso principal es `url_for`:

```html
<a href="{{ url_for('login') }}">Iniciar sesión</a>
```

- `url_for('login')` arma la URL a partir del **nombre de la función**, no de la ruta. Si mañana la ruta cambia de `/login` a `/iniciar-sesion`, los enlaces se actualizan solos.
- Las llaves `{{ }}` son Jinja: `render_template` las procesa antes de enviar el HTML al navegador.

### 5. Landing

Estructura de `index.html`:

| Parte | Contenido |
|---|---|
| `<header>` | Logo, "Crear cuenta" e "Iniciar sesión" |
| Portada | "Tu campus es tu equipo.", texto, botón "Empecemos" y el círculo de "Tu idea" |
| Cómo funciona | "De una idea a un gran equipo" con los 3 pasos |
| `<footer>` | Logo, "Juntos, las ideas despegan." y "Hecho para crear en tu campus." |

Estilos en `teamup/static/css/styles.css`:

- **Colores** definidos una sola vez en `:root` (coral, ocre, carbón, etc.). Cambiar uno ahí lo cambia en toda la página.
- **Layout** con `grid` y `flex`. En pantallas de menos de 900 px todo pasa a una columna.
- **Círculo de "Tu idea"** hecho con HTML y CSS, no con una imagen: anillos y círculo centrados, tarjetas y etiquetas ubicadas con `position: absolute` en porcentajes. Se puede animar más adelante.
- **Logo:** el original está en `assets/LOGO TEAMUP.png` (3712×1152, 1 MB). Para la web se usa una copia reducida en `teamup/static/img/logo.png` (800 px, 64 KB). Flask solo sirve imágenes que están dentro de `static/`.

### 6. Flujo de ramas en GitHub

El flujo es `dev` → `stage` → `main`.

En la pantalla de comparación de GitHub:

- **base** es la rama que **recibe** los cambios.
- **compare** es la rama de **donde salen** los cambios.

```
base: stage  ←  compare: dev      (paso 1)
base: main   ←  compare: stage    (paso 2)
```

Si GitHub muestra "0 files changed", las ramas ya tienen el mismo código y los commits listados son solo registros de merges.

### 7. Base de datos

**Cómo se conecta la app a SQL Server:**

```
Código Python  →  SQLAlchemy  →  pyodbc  →  ODBC Driver  →  SQL Server
```

- **SQLAlchemy (ORM):** traduce clases de Python a tablas SQL. Se usa a través de **Flask-SQLAlchemy**.
- **pyodbc:** la librería que habla con SQL Server.
- **ODBC Driver:** el driver de Microsoft (están instalados el 17 y el 18).

**Servidor local:**

- Instancia predeterminada `MSSQLSERVER`, SQL Server 2025, con Autenticación de Windows.
- En "Nombre del servidor" va **`localhost`**. No va el usuario de Windows (`DESKTOP-...\Camilo`): lo que va después de `\` se interpreta como nombre de instancia.
- La edición instalada es **Enterprise Evaluation**, que caduca a los 180 días. La edición Developer es gratuita y no caduca (se puede cambiar con "Edition Upgrade" en el instalador).

**Cadena de conexión:**

```
mssql+pyodbc://@localhost/TeamUp?driver=ODBC+Driver+17+for+SQL+Server
```

| Parte | Significado |
|---|---|
| `mssql+pyodbc://` | SQL Server usando pyodbc |
| `@` sin nada antes | Sin usuario ni contraseña: Autenticación de Windows |
| `localhost` | El servidor es la propia máquina |
| `/TeamUp` | Nombre de la base de datos |
| `driver=...` | Driver ODBC a usar |

Con el Driver 18 hay que agregar `&TrustServerCertificate=yes`, porque exige cifrado.

**¿Dónde se crea `db`? Importaciones circulares**

Si `db = SQLAlchemy()` se crea en `__init__.py`, se forma un círculo: `__init__.py` importa los modelos y los modelos importan `db` desde `__init__.py`. Python falla con `ImportError`.

La solución es un archivo aparte, `teamup/extensions.py`, que solo crea `db`:

```python
# teamup/extensions.py
db = SQLAlchemy()

# teamup/__init__.py
from teamup.extensions import db
db.init_app(app)

# teamup/models/usuario.py
from teamup.extensions import db
```

`db` se crea vacío y `db.init_app(app)` lo conecta con la app dentro de `create_app()`. Más adelante ahí también irá el `LoginManager`.

La conexión se probó y funciona contra la base `TeamUp`.

### 8. Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| `pip install pyodbc` pedía "Microsoft Visual C++ 14.0" | Python 3.14 y `pyodbc==5.1.0` no tiene paquete precompilado para esa versión | Instalar `pyodbc>=5.3.0` |
| Pylint: "Missing module/function docstring" | Avisos de estilo, no errores | Opcional: agregar `"""descripción"""` |
| `TemplateNotFound` | La ruta usa un HTML que no existe en `templates/` | Crear el archivo |
| No conectaba a SQL Server | En el servidor estaba el usuario de Windows; además SQL Server no estaba instalado al inicio | Instalar SQL Server y usar `localhost` |
| `ModuleNotFoundError: teamup.extensions` | `extensions.py` estaba en la raíz y no dentro de `teamup/` | Moverlo a `teamup/extensions.py` |
| `Either 'SQLALCHEMY_DATABASE_URI' ... must be set` | Nombre mal escrito: `SQLACHEMY` | Escribir `SQLALCHEMY_DATABASE_URI` |
| Cambios que no se veían | El archivo no estaba guardado | Guardar con Ctrl+S |

### 9. Siguiente paso

- Escribir la clase `Usuario` en `teamup/models/usuario.py` con sus columnas.
- Crear la tabla en SQL Server.
- Login, registro y protección de rutas.
- Agregar los formularios a `login.html` y `register.html`.
