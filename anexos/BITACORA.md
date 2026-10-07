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

> Todo esto quedó hecho en la segunda parte de la sesión (abajo).

---

## Sesión del 6 de octubre de 2026 (segunda parte): entorno, registro y login

### 10. Entorno virtual y `requirements.txt`

**Instalación en la máquina:** Python 3.14.7 instalado con `winget` (con "Add to PATH"). Después de instalar hay que **cerrar y abrir VS Code**: las terminales abiertas antes no ven el nuevo PATH y `python` abre el aviso de Microsoft Store.

```powershell
python -m venv venv                  # crear el entorno (una vez por máquina)
.\venv\Scripts\Activate.ps1          # activarlo: aparece (venv) en la terminal
pip install -r requirements.txt      # instalar las librerías
python run.py
```

Si PowerShell no deja ejecutar `Activate.ps1`: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (una sola vez).

En VS Code hay que elegir el intérprete del entorno (`Ctrl+Shift+P` → *Python: Select Interpreter* → `.\venv\Scripts\python.exe`); si no, marca los imports en amarillo ("could not be resolved").

**¿Se sube el `venv` a GitHub?** Se evaluó y se decidió que **no**:

- El `venv` guarda rutas absolutas de la máquina donde se creó (`pyvenv.cfg` → `home = C:\Users\Camilo\...\Python314`). En otra compu no funciona.
- Son ~1.800 archivos (42 MB) que generan conflictos imposibles de resolver en los merges.

Lo que se comparte es **`requirements.txt`**, con las versiones exactas (`pip freeze`):

| Situación | Comando |
|---|---|
| Bajé cambios del otro | `pip install -r requirements.txt` (solo instala lo nuevo) |
| Agregué una librería | `pip install <libreria>` y `pip freeze > requirements.txt`, y commit del archivo |

`requirements.txt` no instala lo que no es de Python: **Python 3.14**, el **ODBC Driver 17** y **SQL Server** con la base `TeamUp` se instalan aparte. La base vacía se crea a mano (`CREATE DATABASE TeamUp`); las tablas las crea la app.

### 11. Registro alineado con los modelos

- **Una sola universidad:** se quitó el selector de universidad (fue una confusión de alcance).
- **Carreras desde la base:** antes estaban escritas a mano en el HTML. Ahora la lista vive en la clase (`CARRERAS` en `carrera.py`), se inserta en la tabla al crearla, el controlador la consulta y el `<select>` se arma con Jinja. El usuario ve el nombre, pero se envía el `idCarrera`, que es lo que pide la FK `carreraUsuario`.
- **Semestre:** del 1 al 10 como número (se quitó "Egresado" porque la columna es `Integer`).

**Modelo `Usuario` actualizado:** alias `nombreUsuario` (único), primer y segundo nombre, primer y segundo apellido (los segundos opcionales), correo único, una sola contraseña `passwordUsuario` (se eliminó `contrasenaUsuario`, que estaba duplicada), semestre y carrera.

Como `create_all()` **no modifica tablas existentes**, se borró la tabla `usuario` (estaba vacía) para que se creara con las columnas nuevas.

### 12. Login con Flask-Login

| Pieza | Para qué |
|---|---|
| `login_manager = LoginManager()` en `extensions.py` | Igual que `db`: se crea vacío y se conecta en `create_app()` |
| `SECRET_KEY` | Firma la cookie de sesión para que nadie la edite. Sin ella no funcionan sesiones ni `flash` |
| `login_manager.login_view = "auth.login"` | A dónde manda `@login_required` si no hay sesión |
| `UserMixin` en `Usuario` | Da `is_authenticated` y lo demás que necesita Flask-Login |
| `get_id()` en `Usuario` | Flask-Login busca `id` por defecto; el nuestro se llama `idUsuario` |
| `@login_manager.user_loader` | La cookie solo guarda el id; en cada petición esta función busca al usuario en la base y lo deja en `current_user` |

Funcionamiento:

- **Registro:** valida, guarda la contraseña como hash (`generate_password_hash`, nunca en texto plano), inicia sesión y va a `/explorar`.
- **Login:** con **correo o alias**. Compara con `check_password_hash`. Si falla, mensaje genérico "Correo o contraseña incorrectos." (no se dice cuál falló, a propósito). Si venía de una página protegida, vuelve a ella (`?next=`).
- **Logout:** `/logout` cierra la sesión y manda al login.
- **Explorar** (`/explorar`) tiene `@login_required`: sin sesión redirige a `/login?next=/explorar` con el mensaje "Inicia sesión para continuar."

### 13. Controladores con Blueprints

Las rutas salieron de `__init__.py`. Ahora `__init__.py` solo configura y registra los controladores:

| Blueprint | Archivo | Rutas |
|---|---|---|
| `auth` | `controllers/auth.py` | `/register`, `/login`, `/logout` |
| `principal` | `controllers/principal.py` | `/`, `/explorar` |

Un Blueprint es un grupo de rutas en otro archivo; `app.register_blueprint(auth)` las suma a la app. En `url_for` va el nombre del Blueprint primero: `url_for('auth.login')`.

### 14. Validaciones con Flask-WTF

La primera versión validaba con una cadena de `if / elif` dentro del controlador. Problemas: un solo error a la vez, el error no aparecía junto al campo y el controlador mezclaba reglas con lógica. Se pasó a **Flask-WTF**:

- `teamup/forms.py` tiene `RegistroForm` y `LoginForm`. Cada campo declara sus reglas:
  - `validators`: `DataRequired`, `Length`, `Email`, `Regexp`, `EqualTo` (contraseñas iguales), `NumberRange`.
  - `filters`: limpian antes de validar (quitar espacios, correo en minúsculas).
  - Métodos `validate_<campo>`: reglas que consultan la base (alias y correo repetidos, carrera existente). WTForms los ejecuta solo.
- En el controlador: `if form.validate_on_submit():` (es POST y pasaron todas las reglas) → guardar. Si no, se vuelve a mostrar el formulario con los errores.
- `templates/_campos.html` tiene macros de Jinja (`campo`, `selector`, `token`) que dibujan cada campo con su etiqueta, borde rojo y mensaje de error debajo.
- Se muestran **todos los errores a la vez**, cada uno en su campo, y el formulario conserva lo escrito (menos las contraseñas).
- **CSRF:** `{{ token(form) }}` agrega un campo oculto con un código secreto; sin él, el formulario se rechaza. Vence a la hora: en ese caso aparece "El formulario expiró. Vuelve a intentarlo."

### 15. Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| `Python was not found` (Microsoft Store) | Python no estaba instalado; luego, terminal abierta antes de instalarlo | Instalar Python 3.14 y reabrir VS Code |
| `Cannot open database "TeamUp"` (4060) | La base no existía en esta máquina | `CREATE DATABASE TeamUp` |
| `405 Method Not Allowed` al enviar formularios | Las rutas solo aceptaban GET | `methods=["GET", "POST"]` |
| `NameError: app` | `app.config` se usaba antes de `app = Flask(__name__)` | Crear la app primero |
| `cannot import name 'UserMixin' from 'flask_sqlalchemy'` | `UserMixin` es de `flask_login` | `from flask_login import UserMixin` e instalar Flask-Login |
| Columnas nuevas no aparecían en SQL Server | `create_all()` no altera tablas existentes | Borrar la tabla vacía y dejar que se recree |
| Imports en amarillo en VS Code | VS Code usaba otro intérprete | Seleccionar `venv\Scripts\python.exe` |

### 16. Siguiente paso

- **Modelo `Proyecto`** (título, descripción, categoría, fechas, creador como FK a `usuario`) y, si da el tiempo, `Rol`.
- **CRUD de proyectos** en `controllers/proyectos.py` con `@login_required`: listar mis proyectos, crear, ver, editar y eliminar. Solo el creador puede editar o eliminar.
- Plantillas: lista de proyectos y formulario de crear/editar (con un `ProyectoForm` de WTForms).
- Mostrar los proyectos en Explorar.
- Grabar el **video** (máx. 3 min): login, registro y que `/explorar` y el CRUD no abren sin sesión.
- Pasar `stage` → `main`.
- Pendientes menores: footer del landing.
