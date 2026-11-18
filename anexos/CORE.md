# Plan del core (para la presentación)

> **Este archivo vive solo en `stage` (y en las ramas personales), nunca en `main`.** Ver "Este archivo no va a main" al final.
>
> **Estado: en curso.** Sale de los apuntes de Camilo y Sebastián. Lo programado está marcado como **Hecho** en "Orden de trabajo"; lo decidido, en "Decisiones tomadas"; lo pendiente, en "Preguntas abiertas".

## Qué es "el core"

El core es lo que hace que TeamUp sea TeamUp: **publicar un proyecto con vacantes, postularse y armar el equipo**. Para la presentación eso tiene que funcionar de punta a punta. Lo demás (notificaciones, moderación, filtros) suma, pero va después.

## Lo que falta, según los apuntes

**Usuario**
- Perfil completo: sobre mí, habilidades, disponibilidad y enlaces.
- Proyecto completo: nombre, descripción larga, categoría, modalidad, dedicación, fechas y contacto.
- Vacantes por proyecto: cada una con su rol y la carrera que se busca.
- Página de detalle del proyecto.
- Editar proyecto.
- Postularse a una vacante con un mensaje, y que el creador acepte o rechace.
- "Mis proyectos" (los que creé) y "Mis postulaciones" (en qué estado está cada una).
- Filtrar proyectos en Explorar.
- Notificaciones con una campana en la barra.
- Reportar un proyecto.
- Forma de contacto.

**Administrador**
- Filtro de palabras: una lista de palabras que el sistema marca.
- Validaciones: si un proyecto tiene una palabra marcada (o lo reportan), no se publica hasta que el admin lo revise.
- Moderar los proyectos reportados.

## Cambios en la base (propuesta)

### Tablas que cambian

**`users`**: se agregan los datos del perfil.

| Columna nueva | Qué guarda |
|---|---|
| `bio` | "Sobre mí", texto largo, opcional |
| `availability` | Disponibilidad en horas por semana, elegida de una lista (por ejemplo 1–2 h, 3–4 h…) |
| `phone` | Número de contacto |
| `portfolio_url`, `linkedin_url` | Enlaces, opcionales |

El **número de proyectos** y los **proyectos realizados** no se guardan: se cuentan desde las otras tablas, así nunca quedan desactualizados.

**`projects`**: se completa el proyecto.

| Columna | Qué guarda |
|---|---|
| `title` | Nombre (ya existe) |
| `summary` | Descripción corta, para las tarjetas de Explorar |
| `description` | Descripción larga (hoy tiene 1000 caracteres; pasa a texto largo) |
| `category_id` | FK a `categories` (se elige de un dropdown) |
| `modality` | Presencial, remota o híbrida |
| `weekly_hours` | Dedicación semanal, de la **misma lista** que la disponibilidad del perfil, para poder compararlas |
| `start_date` | Fecha de inicio |
| `estimated_end_date` | Fecha estimada de cierre |
| `finished_at` | Fecha real en que se terminó. La duración en días = `finished_at` − `start_date`, calculada, no guardada |
| `status` | `draft` → `pending_review` → `open` → `in_progress` → `finished` (o `cancelled`) |

`is_hidden` se queda: sigue sirviendo para que el admin oculte un proyecto.

**Contacto del proyecto:** no se guarda en `projects`. Se muestra el **número** y el **correo institucional** del creador, que ya están en `users`.

### Tablas nuevas

| Tabla | Columnas principales | Para qué |
|---|---|---|
| **`categories`** | `name` | Cortometraje, startup, investigación, arte, evento, podcast, tecnología… Se cargan solas, como las facultades |
| **`skills`** + **`user_skills`** | `name` / (`user_id`, `skill_id`) | Habilidades del perfil. Una persona tiene muchas y una habilidad la tienen muchos |
| **`vacancies`** | `project_id`, `role_name`, `major_id` (vacío = cualquier carrera), `requires_experience`, `slots`, `status` | Las vacantes de cada proyecto. La carrera se elige con la cascada facultad → carrera que ya existe |
| **`applications`** | `vacancy_id`, `user_id`, `message`, `status`, `created_at`, `decided_at` | Las postulaciones. Estados: `pending`, `accepted`, `rejected`, `withdrawn` |
| **`notifications`** | `user_id`, `text`, `link`, `is_read`, `created_at` | Lo que muestra la campana |
| **`banned_words`** | `word` | El filtro de palabras. El admin las agrega o quita |
| **`validation_requests`** | `project_id`, `source`, `detail`, `status`, `reviewed_by`, `reviewed_at` | La cola del admin: proyectos que esperan revisión antes de publicarse |

**Reportes:** los organiza Sebastián (tablas, reglas y pantallas). Lo único que hay que acordar es cómo un reporte llega a la cola del admin (`validation_requests`).

**"Quién" ocupa una vacante** no es una columna: son las postulaciones aceptadas de esa vacante. Así no hay que actualizar dos lugares.

### Cómo se relaciona todo

```
users ──< projects ──< vacancies ──< applications >── users
             │
             ├──> categories
             └──< validation_requests
users ──< notifications
users >──< skills
```

## Reglas importantes (validadas en el servidor)

- Una persona no puede postular dos veces a la misma vacante.
- Al aceptar una postulación, el servidor vuelve a contar los cupos; si ya no hay, rechaza.
- Solo el creador del proyecto acepta o rechaza postulaciones y edita su proyecto.
- Un proyecto con una palabra marcada queda en `pending_review` y crea una `validation_request`; no aparece en Explorar hasta que el admin lo apruebe.
- El creador no puede postular a su propio proyecto.

## Páginas nuevas

| Página | Qué muestra |
|---|---|
| Detalle del proyecto | Toda la información, las vacantes y el botón "Postularme" |
| Crear / editar proyecto | Por pasos, como en Figma: Información → Roles → Fechas → Vista previa |
| Mis proyectos | Los proyectos que creé, con sus postulaciones para aceptar o rechazar |
| Mis postulaciones | Dónde me postulé y en qué estado está cada una |
| Perfil público | Sobre mí, habilidades, disponibilidad, enlaces y proyectos |
| Explorar con filtros | Por categoría, facultad o carrera, modalidad y dedicación |
| Admin: validaciones | La cola de proyectos por revisar (aprobar o rechazar) |
| Admin: palabras | Agregar y quitar palabras del filtro |

## Orden de trabajo (propuesta)

1. **Base del core:** `categories`, campos nuevos de `projects`, `vacancies`. **Hecho (2026-11-17), aplicado en Neon `dev`.**
    - Modelos: `teamup/models/category.py`, `teamup/models/vacancy.py` y las columnas nuevas en `teamup/models/project.py`.
    - Listas compartidas en `teamup/choices.py`: `WEEKLY_HOURS` (la disponibilidad del perfil usa **esta misma lista**), `MODALITIES`, estados del proyecto y de las vacantes, y `label()` para mostrar su texto en español.
    - Los proyectos nuevos nacen como `draft`; los que ya existían quedaron como `open`. Mientras no esté el paso 2, el formulario actual publica directo como `open`.
    - Las postulaciones (`applications`) ya se pueden construir sobre `vacancies`.
2. **Proyecto completo:** crear y editar por pasos, y la página de detalle. **Hecho (2026-11-17).**
    - Rutas en `teamup/controllers/projects.py`: `/projects/new` (paso 1, crea el borrador), `/projects/<id>/info`, `/roles`, `/dates`, `/preview`, `/publish` y el detalle `/projects/<id>`.
    - Formularios: `ProjectInfoForm`, `VacancyForm` (sin facultad = cualquier carrera) y `ProjectDatesForm`, en `teamup/forms.py`.
    - Lo que falta para publicar lo decide `Project.missing_for_publish()`; el servidor no publica si falta algo.
    - Un borrador o un proyecto oculto solo lo ven su dueño y el admin; Explorar muestra solo los `open` no ocultos.
    - Plantillas: `project_step_*.html`, `project_preview.html`, `project_detail.html`; piezas en `_project_steps.html` y `_projects.html` (el macro `sections` arma el contenido del proyecto). Estilos en `static/css/projects.css`.
    - **Para Sebastián:** en `_projects.html` (macro `sections`) hay un comentario donde va el botón "Postularme" de cada rol, y en `project_detail.html` otro donde va el número de contacto cuando exista en el perfil.
3. **Postulaciones:** `applications`, postularse, aceptar o rechazar, Mis proyectos y Mis postulaciones.
4. **Perfil:** bio, habilidades, disponibilidad, enlaces y perfil público.
5. **Explorar con filtros.** **Hecho (2026-11-17), junto con "Mis proyectos" y terminar un proyecto.**
    - Filtros por categoría, facultad, carrera, modalidad y dedicación, por `GET` (quedan en la dirección). Los valores que no existen se ignoran (`ExploreFilterForm.filters()`); la búsqueda está en `Project.search()`.
    - Por facultad o carrera salen los proyectos con un rol abierto para esa carrera **o para cualquier carrera**.
    - "Mis proyectos" (`/my-projects`): publicados, borradores y terminados, con sus acciones. "Terminar proyecto" pone `finished_at` y muestra la duración en días (`Project.finish()`; no se puede antes de la fecha de inicio).
    - **Para Sebastián:** en `my_projects.html` hay un comentario donde van las postulaciones de cada proyecto (aceptar o rechazar).
    - **Gestión del proyecto (2026-11-18):** el dueño maneja su proyecto desde la página del proyecto, no desde las tarjetas. En Mis proyectos cada tarjeta tiene solo "Gestionar" (o "Continuar" si es borrador). En la página hay un panel "Gestión" con el estado (Abierto → En curso → Terminado) y los botones:
        - **Arrancar proyecto** (`open` → `in_progress`): el equipo ya está; sale de Explorar pero su página sigue visible.
        - **Volver a buscar gente** (`in_progress` → `open`): si alguien se va; vuelve a Explorar.
        - **Terminar proyecto**, y además Editar, Ocultar y Borrar.
        - Rutas: `POST /projects/<id>/start`, `/reopen`, `/finish` (`change_status`); la lógica está en `Project.start()`, `reopen()` y `finish()`.
        - **Un proyecto terminado es solo para ver:** su dueño ya no lo edita, no cambia su estado, no lo oculta ni lo borra (lo bloquea `finished_is_read_only()` en `controllers/projects.py`). El admin sí lo puede ocultar o borrar desde su panel.
    - **Vitrina (`/showcase`):** muestra los terminados que **el admin aprobó**. Al terminar un proyecto se crea un pedido en la cola "Revisión" con el motivo "Vitrina" (`Project.request_showcase()`). Aprobar pone `in_showcase = True`; rechazar lo deja terminado pero fuera de la Vitrina. Los que ya estaban terminados antes de esta migración entraron solos a la cola.
    - La página del proyecto sigue el diseño de Figma: portada con categoría y estado, "La idea", roles, "Creado por" (sin "Enviar mensaje": el contacto es el correo) y "Equipo actual".
    - **Para Sebastián:** en `project_detail.html` hay comentarios donde van el botón "Postularme" (solo si el proyecto está `open` y no es del usuario), el "Sobre mí" y el número del creador, y los integrantes aceptados en "Equipo actual". En `my_projects.html` puede ir cuántas postulaciones nuevas tiene cada proyecto.
6. **Notificaciones** (la campana).
7. **Moderación:** filtro de palabras, reportes y cola de validación del admin. **Hecha la parte de Camilo (2026-11-18): filtro de palabras y cola de revisión, aplicado en Neon `dev`.** Los reportes son de Sebastián.
    - Tablas `banned_words` y `validation_requests` (modelos `BannedWord` y `ValidationRequest`).
    - Al **publicar**, y al **editar** un proyecto ya publicado (paso 1 o un rol nuevo), se buscan las palabras del filtro en el título, los resúmenes y los nombres de los roles. Cuentan como palabra completa y sin importar mayúsculas ni tildes ("estafa" marca "Estafá", no "estafador"). Si aparece alguna, el proyecto pasa a `pending_review`, sale de Explorar y entra en la cola.
    - Panel del admin con dos pestañas nuevas: **Revisión** (aprobar o rechazar) y **Palabras** (agregar y quitar). Aprobar devuelve el proyecto al estado que tenía (`open`, `in_progress`…); rechazar lo vuelve `draft` y el dueño ve el motivo en la vista previa.
    - En la barra lateral, "Admin" lleva al panel.
    - **Para Sebastián (reportes):** ver la respuesta a la pregunta 2 en "Preguntas abiertas".

Del 1 al 3 es el core mínimo para presentar.

## Reparto

Cada uno hace **su parte completa: back-end y front-end** (modelos, rutas, validaciones y pantallas). Sebastián sigue cuidando que todo el diseño se vea igual.

| Camilo | Sebastián |
|---|---|
| Flask-Migrate (primero, porque lo usan los dos) | Perfil: sobre mí, habilidades, disponibilidad, número, enlaces y perfil público |
| Proyectos: tablas (`projects`, `categories`, `vacancies`), crear y editar por pasos, detalle | Postulaciones: `applications`, postularse, aceptar o rechazar, Mis postulaciones |
| Cómo se ven los proyectos: Explorar, tarjetas, filtros, Mis proyectos | Reportes: los organiza él |
| Administración: filtro de palabras, cola de validación y panel | Lo demás que falte (por confirmar): notificaciones |

**Dependencias (quién espera a quién):**
- Las postulaciones van sobre las vacantes, así que **Camilo hace primero `vacancies`** y Sebastián después `applications`.
- "Aceptar o rechazar" aparece en Mis proyectos (de Camilo), pero la lógica es de postulaciones (de Sebastián): Camilo deja el espacio en la pantalla y Sebastián pone los botones.
- La cola del admin (Camilo) recibe proyectos del filtro de palabras y de los reportes (Sebastián): hay que acordar ese punto.

## Cómo escribimos los commits

Formato:

```
tipo(área): qué se hizo, en presente - iniciales
```

**Tipos**

| Tipo | Cuándo |
|---|---|
| `feat` | Algo nuevo que hace la app |
| `fix` | Se arregla un error |
| `style` | Diseño o CSS, sin cambiar cómo funciona |
| `refactor` | Se reordena código sin cambiar lo que hace |
| `db` | Cambios en tablas o datos iniciales |
| `docs` | README, anexos, comentarios |
| `chore` | Configuración, dependencias, deploy |

**Áreas:** `auth`, `perfil`, `proyectos`, `vacantes`, `postulaciones`, `explorar`, `notificaciones`, `admin`, `moderacion`, `deploy`.

**Ejemplos**

```
db(vacantes): agrega la tabla de vacantes por proyecto - CN
feat(postulaciones): permite aceptar o rechazar una postulacion - CN
style(proyectos): diseña la pagina de detalle - SR
fix(auth): corrige el login con mayusculas - CN
```

**Reglas**
- Un commit = un cambio con sentido propio. No mezclar, por ejemplo, una tabla nueva con el CSS del perfil.
- En español, en presente, sin punto final, corto (máximo unas 70 letras antes de las iniciales).
- Iniciales: ` - CN` (Camilo) y ` - SR` (Sebastián).
- Los merges a `stage` y `main` mantienen su mensaje automático.

## Decisiones tomadas

- **Flask-Migrate:** configurado. Las tablas se cambian con migraciones, sin borrar datos (ver "Base de datos").
- **Solo Neon (PostgreSQL):** SQL Server se quitó de todo el proyecto, en todas las ramas.
- **Contacto:** solo el número y el correo institucional del creador.
- **Reportes:** los organiza Sebastián.
- **Reparto:** cada uno hace back-end y front-end de su parte (ver "Reparto").
- **Categorías:** una categoría por proyecto, elegida de un dropdown (no etiquetas).
- **Sin más JavaScript:** lo nuevo se resuelve con Flask (formularios que se envían al servidor).
- **Disponibilidad:** horas por semana, elegidas de una lista (1–2 h, 3–4 h…). La dedicación semanal del proyecto usa la misma lista.
- **Crear proyecto por pasos:** una página por paso (Información → Roles → Fechas → Vista previa). El proyecto se guarda como borrador (`draft`) desde el paso 1, cada paso se valida en el servidor y en "Vista previa" se publica.

## Preguntas abiertas

1. **Para Sebastián:** ¿hace las notificaciones?
2. **Para Sebastián:** ¿cómo pasa un proyecto reportado a la cola de validación del admin? **Propuesta de Camilo (ya programada):** cuando decidas que un reporte debe llegar al admin, llama a:

    ```python
    from teamup.choices import REVIEW_REPORT
    project.send_to_review(REVIEW_REPORT, "Reportado por @usuario: motivo")
    db.session.commit()
    ```

    Eso saca el proyecto de Explorar y lo pone en la pestaña "Revisión" con ese texto como motivo. Si ya hay un reporte pendiente de ese proyecto, actualiza el mismo pedido en lugar de crear otro. Tú decides cuándo llamarlo (con el primer reporte, a partir de varios…) y guardas los reportes en tus tablas.

## Convenciones de código

Reglas para todo lo que se escriba en el repo, a mano o con ayuda de un asistente.

**Idioma**
- **Código en inglés:** archivos, clases, funciones, variables, tablas, columnas, rutas (`/explore`, `/profile`), clases CSS e ids de HTML. Python en `snake_case`.
- **Lo que ve el usuario en español:** textos de las plantillas, etiquetas, mensajes de error de los formularios y `flash()`.
- **Comentarios en español,** cortos y en texto simple, solo cuando aportan algo. En CSS, una etiqueta simple por sección (`/* Botones */`), sin líneas decorativas (`/* ===== */`).
- En los textos generales (README, documentos, textos de la página) se habla de "tu campus" o "tu universidad", sin nombrar la universidad.

**Estructura (MVC con Flask)**
- `teamup/models/`: un archivo por tabla. Los datos iniciales (como facultades o categorías) se cargan con el evento `after_create`.
- `teamup/controllers/`: un Blueprint por área, solo con rutas. Reciben la petición, usan formularios y modelos, y responden.
- `teamup/forms.py`: los formularios (WTForms). Las reglas que consultan la base van en métodos `validate_<campo>`.
- `teamup/validators.py`: validadores que se reutilizan en varios formularios.
- `teamup/permissions.py`: permisos por rol (`@role_required`).
- `teamup/templates/`: plantillas Jinja. Las piezas repetidas van en macros (`_fields.html`, `_projects.html`).

**Reglas**
- **Toda validación se hace en el servidor.** Los formularios llevan `novalidate`; nunca se confía en lo que valida el navegador.
- **Nada de JavaScript nuevo.** Lo nuevo se resuelve con formularios que se envían a Flask. Solo se mantienen los dos archivos que ya existen (`faculty-major.js` y `confirm-delete.js`).
- **En las plantillas, las direcciones siempre van con `url_for`,** nunca escritas a mano.
- **Clases CSS con BEM:** `bloque__elemento--modificador` (por ejemplo `project-card__title`, `btn--primary`). Cada elemento con estilo lleva su clase; no se usan selectores por etiqueta como `.hero h1`.
- **Los botones sueltos** (ocultar, borrar, aceptar…) van en un `<form method="POST">` con el token CSRF de `ActionForm`.
- **Los permisos se revisan en el servidor:** ocultar un botón no basta. Si no tiene permiso, `abort(403)`.
- **Cambios en la base con Flask-Migrate,** nunca borrando tablas ni usando `db.create_all()` (ver "Base de datos").
- **Nombre de usuario y correo** se guardan en minúsculas (PostgreSQL distingue mayúsculas).
- **Los commits** siguen el formato de "Cómo escribimos los commits" y no llevan líneas de coautoría.

**Ramas**
- Cada uno trabaja en la suya (`devCamilo`, `devSebas`). Antes de empezar: `git merge origin/stage`.
- Lo que funciona pasa a `stage`; cuando `stage` está probado, pasa a `main`.

## Base de datos

**Se usa solo PostgreSQL en Neon.** SQL Server se quitó del código, de `requirements.txt` y del README, en todas las ramas. No volver a agregarlo: las migraciones solo se prueban en PostgreSQL.

**Neon tiene dos ramas:**

| Rama de Neon | La usa |
|---|---|
| `production` | La página oficial (rama `main` en Vercel) |
| `dev` (pruebas) | La página de prueba (rama `stage` en Vercel) y la compu de cada uno |

**En Vercel** cada ambiente ya tiene su `DATABASE_URL`; no hay que hacer nada.

**En la compu** hace falta un archivo `.env` en la carpeta `TeamUp` (no se sube a Git) con la dirección de la rama `dev`:

```
DATABASE_URL=postgresql://...
```

Sin ese archivo la app no arranca y avisa: *"Falta DATABASE_URL"*. La dirección se pide a Camilo por un medio privado; nunca se escribe en el código ni en el repo.

**Flask-Migrate** cambia la forma de las tablas sin borrar datos. Las tablas ya no se crean con `db.create_all()`. Neon no conoce los modelos de Python: si se agrega una columna en un modelo, alguien tiene que aplicarla en la base, y eso hace la migración. Los comandos se corren desde la carpeta `TeamUp`:

| Cuándo | Comando |
|---|---|
| Cambiaste o agregaste un modelo | `python -m flask --app run db migrate -m "qué cambió"` (crea el archivo en `migrations/versions/`) |
| Aplicar las migraciones a la base | `python -m flask --app run db upgrade` |
| Cargar los datos iniciales que falten (roles, facultades, carreras) | `python -m flask --app run seed` (no duplica; se puede correr siempre) |
| Ver en qué versión está la base | `python -m flask --app run db current` |

**Reglas:**
- **Antes de cada `db upgrade`, comprobar a qué rama de Neon apunta el `.env`** (`python -m flask --app run db current` y revisar el host en Neon). En la compu siempre va la rama `dev`; la de `production` solo se usa al pasar a `main`.
- Revisar el archivo que crea `db migrate` antes de aplicarlo: a veces no detecta bien un cambio de nombre.
- El archivo de la migración se sube a Git en el **mismo commit** que el cambio del modelo.
- Una migración ya subida a `stage` no se edita: si algo quedó mal, se hace una migración nueva que lo corrige.
- Como los dos usan la misma rama `dev`, quien crea la migración la aplica con `db upgrade`; el otro no tiene que hacer nada con la base al bajar los cambios.
- Los datos iniciales nuevos (por ejemplo, las categorías) se agregan al comando `seed` en `teamup/commands.py`, no a una migración.
- **Antes de pasar a `main`:** Camilo corre `db upgrade` apuntando a la rama `production` de Neon, para que la base real tenga las tablas nuevas antes de que llegue el código.

## Este archivo no va a main

`main` es lo que se entrega y se publica. Este plan es interno, así que se queda en `stage`. Al pasar `stage` a `main`, se quita en el mismo merge:

```powershell
git switch main
git merge --no-ff --no-commit stage
git rm -f --ignore-unmatch anexos/CORE.md
git commit -m "Merge branch 'stage'"
```

- Funciona igual si Git avisa de un conflicto con `anexos/CORE.md`: el `git rm` lo resuelve.
- **Nunca traer `main` hacia `stage`** (ni a las ramas personales): traería también el borrado y `CORE.md` desaparecería de `stage`. Lo nuevo siempre va de `stage` a `main`, no al revés.
