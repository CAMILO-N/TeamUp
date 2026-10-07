# TeamUp: contexto del proyecto

Proyecto integrador de la materia **Ingeniería Web**, hecho en pareja por Camilo (CAMILO-N) y Sebastián.

## Qué es

TeamUp es una plataforma web donde estudiantes de **una sola universidad** publican proyectos de cualquier área (cortometrajes, startups, investigación, arte, eventos, podcasts) y arman equipos interdisciplinarios con compañeros de otras carreras.

- Slogan: **"Juntos, las ideas despegan."**
- El alcance es **una sola universidad**: no hay selector de universidad en el registro ni en ningún otro lado.
- No mencionar ninguna universidad por nombre en el producto ni en el repo. Hablar de "tu campus" o "tu universidad".

## Flujo principal

1. Un estudiante publica un proyecto y define los **roles** que necesita. Cada rol tiene una carrera sugerida (o "cualquier carrera"), si requiere experiencia o no, y número de cupos.
2. Otros estudiantes se postulan a esos roles.
3. El creador acepta o rechaza postulaciones y arma su equipo.
4. Al terminar, el proyecto pasa a la **vitrina** con créditos para cada participante y queda como experiencia en su perfil.

Ejemplo de referencia: un estudiante de cine que hace un corto busca guionista (Letras), director de fotografía (Audiovisuales) y 3 extras sin experiencia.

## Módulos

- **MVP:** autenticación, perfil, publicar proyecto con roles, explorar con filtros, postulaciones, vitrina.
- **Después:** foro de pitch (votos y comentarios), notificaciones, chat del equipo, recomendaciones, app móvil.

## Stack

- **Python 3.14** + **Flask 3**, con patrón **MVC** y *application factory* (`create_app()` en `teamup/__init__.py`, `run.py` es el único punto de entrada).
- Base de datos: **SQL Server** local (instancia predeterminada, `localhost`, Autenticación de Windows), base **`TeamUp`**.
- Conexión: **pyodbc** con el **ODBC Driver 17 for SQL Server**: `mssql+pyodbc://@localhost/TeamUp?driver=ODBC+Driver+17+for+SQL+Server`. (El 18 también está instalado; con él hay que agregar `&TrustServerCertificate=yes`).
- Acceso a datos: **ORM con Flask-SQLAlchemy**. Las tablas se crean con `db.create_all()` al arrancar. `create_all()` **no modifica tablas que ya existen**: si cambia un modelo, hay que borrar la tabla (si no tiene datos importantes) para que se vuelva a crear.
- Autenticación: **Flask-Login** sobre el modelo `Usuario`, contraseñas hasheadas con `werkzeug.security` (`generate_password_hash` / `check_password_hash`).
- Formularios: **Flask-WTF / WTForms** (validación por campo en el servidor y protección **CSRF**). `email-validator` lo requiere el validador `Email()`.
- Vistas: HTML en `teamup/templates/` con Jinja (`url_for`, macros). CSS, JS e imágenes en `teamup/static/`.

## Entorno y dependencias

- Cada integrante crea **su propio** entorno virtual `venv/` dentro de `TeamUp/`. El `venv` **no se sube** (está en `.gitignore`): guarda rutas absolutas de la máquina donde se creó y no funciona en otra.
- Lo que se comparte es **`requirements.txt`** con versiones exactas.
  - Al bajar cambios: `pip install -r requirements.txt`.
  - Al agregar una librería: `pip install <libreria>` y luego `pip freeze > requirements.txt`, y se hace commit del archivo.

## Estructura

```
TeamUp/
├── run.py                      crea y arranca la app (puerto 80)
├── requirements.txt
└── teamup/
    ├── __init__.py             create_app(): configuración, db, Flask-Login, user_loader, registra Blueprints
    ├── extensions.py           db = SQLAlchemy(), login_manager = LoginManager()  (evita importaciones circulares)
    ├── forms.py                RegistroForm, LoginForm (WTForms)
    ├── models/
    │   ├── carrera.py          Carrera + lista CARRERAS que se inserta al crear la tabla
    │   └── usuario.py          Usuario (UserMixin)
    ├── controllers/
    │   ├── auth.py             Blueprint "auth": /register, /login, /logout
    │   └── principal.py        Blueprint "principal": / (landing), /explorar (protegida)
    ├── templates/
    │   ├── _campos.html        macros: token(form), campo(field), selector(field)
    │   ├── index.html          landing
    │   ├── login.html, register.html
    │   └── explorar.html       página principal después del login
    └── static/                 css/styles.css (landing y app), css/auth.css (login y registro), img/logo.png
```

- En `url_for` se usa el nombre del Blueprint: `url_for('auth.login')`, `url_for('principal.explorar')`.

## Modelos actuales

**Carrera:** `idCarrera` (PK), `nombreCarrera` (único). Las 15 carreras de `CARRERAS` se insertan solas con el evento `after_create`.

**Usuario:**

| Columna | Regla |
|---|---|
| `idUsuario` | PK |
| `nombreUsuario` | alias, obligatorio y único (3 a 25: letras, números, `_`, `.`) |
| `primerNombreUsuario` / `primerApellidoUsuario` | obligatorios, máx. 25 |
| `segundoNombreUsuario` / `segundoApellidoUsuario` | opcionales, máx. 25 |
| `emailUsuario` | obligatorio, único, máx. 100, se guarda en minúsculas |
| `passwordUsuario` | hash de la contraseña (mín. 8 caracteres al registrarse) |
| `semestreUsuario` | 1 a 10 |
| `carreraUsuario` | FK a `carrera.idCarrera` |

`get_id()` devuelve `idUsuario` para Flask-Login.

## Autenticación

- Rutas públicas: `/`, `/login`, `/register`. Todo lo demás lleva `@login_required` y redirige a `/login?next=...`.
- Se inicia sesión con **correo o alias** + contraseña. Error genérico: "Correo o contraseña incorrectos."
- Al registrarse se inicia sesión automáticamente y se va a `/explorar`.
- Con sesión iniciada, `/`, `/login` y `/register` redirigen a `/explorar`.
- `SECRET_KEY` se lee de la variable de entorno `SECRET_KEY`; si no existe usa un valor de desarrollo.

## Entrega actual

Ver `anexos/ENTREGA-1.md`. Resumen:

- CRUD aplicando MVC. En TeamUp, el CRUD es de **proyectos**.
- Login con usuario y contraseña. Las URLs del CRUD deben estar protegidas: sin sesión iniciada, redirigir al login.
- Repositorio ordenado y README bien hecho.
- Video de máximo 3 minutos mostrando el login y que la sección protegida no es accesible sin sesión.

**Hecho:** registro, login, logout, Explorar protegida, estructura MVC con Blueprints, validaciones con WTForms, `requirements.txt`, instrucciones en el README.
**Falta:** modelo `Proyecto` y su CRUD protegido, video.

## Ramas y commits

- `main`: versión estable. `stage`: pruebas e integración. `dev`: desarrollo diario. Ramas personales: `devCamilo`, `devSebas`.
- Trabajar en `dev` (o en ramas que salen de `dev`). Luego pasar a `stage` y al final a `main`, con merge (`--no-ff`) o pull request. Como es un proyecto de clase y no está en producción, se puede hacer el merge `stage` → `main` localmente y subirlo.
- Commits a nombre de CAMILO-N con el correo `153507573+CAMILO-N@users.noreply.github.com`.
- **No agregar líneas de coautoría ni menciones a Claude** en commits, PRs ni archivos del repo.
- Mensajes de commit en español, cortos y claros, terminados en ` - CN`.

## README

- Sin emojis.
- No incluir modelo de datos, flujo de ramas, siguientes etapas, tipos de usuario ni sección de equipo, salvo que se pida.
- Mantener: qué es, el problema, cómo funciona (diagrama), funcionalidades, cómo correr el proyecto y la sección "Prototipo y arte" con el enlace de Figma.

## Diseño y marca

- Prototipo en Figma: https://www.figma.com/make/egdPMLaIE0ehRj88IliyMb/Responsive-Web-Prototype-for-TeamUp?t=sDEuayFbezUxM6km-1
- Logo: dos personitas chocando la mano en alto (una coral, otra ocre) más la palabra "teamup" en minúsculas, con "up" en coral. Original: `assets/LOGO TEAMUP.png` (3712×1152). Copia para la web: `teamup/static/img/logo.png` (800 px).
- Estilo: modo oscuro con cuadrícula de puntos sutil, tarjetas muy redondeadas, brillo coral suave en elementos clave, chips y botones en píldora.
- Colores: coral `#E4572E` (principal), rojo teja `#C4402A`, ocre `#F2B33D` (etiquetas), carbón `#17161A` (fondo oscuro), superficies `#222126`, bordes `#34323A`, hueso `#FAF7F2`, gris cálido `#A29D97`.
- Tipografías: Space Grotesk (títulos) e IBM Plex Sans (texto).
