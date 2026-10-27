# Lo que las pantallas de Sebastián esperan de Camilo

Las plantillas ya están hechas. Para que funcionen, el servidor tiene que darles estos datos.
Las direcciones de los botones están escritas tal cual (no usan `url_for`), así que no importa cómo se llamen los blueprints.

## Formularios (forms.py)
- `RegisterForm`: campos `id_number`, `faculty` (SelectField con las facultades) y `major`. `major` no necesita opciones: las carga el JavaScript.
- `ProfileForm`: **`id_number = None`** (como `password`), porque en "Mi perfil" la cédula solo se muestra. Además hay que pasarle `"faculty": current_user.major.faculty_id` en `data=`, para que la facultad aparezca marcada.
- `ProjectForm`: `title` y `description`.
- Un formulario vacío `FlaskForm` (como `DeleteAccountForm`) para el token de los botones: se pasa como `csrf_form`.

## Pantallas
| Plantilla | Se la pasa | Recibe |
|---|---|---|
| `admin_users.html` | `/admin/users` | `users`, `csrf_form` |
| `admin_projects.html` | `/admin/projects` | `projects` (todos, con los ocultos), `csrf_form` |
| `project_new.html` | `/projects/new` | `form` (`ProjectForm`) |
| `explore.html` | `/explore` | `projects` (solo visibles), `my_projects` (los del usuario, con ocultos), `csrf_form` |
| `403.html` | `@app.errorhandler(403)` | nada |

## Atributos
- Usuario: `id`, `username`, `first_name`, `last_name`, `email`, `id_number`, `is_admin`, `is_active`, `major.name`
- Proyecto: `id`, `title`, `description`, `is_hidden`, `owner.username`

## Direcciones que reciben un POST
| Dirección | Campo |
|---|---|
| `/admin/users/<id>/role` | `role` = `student` o `admin` |
| `/admin/users/<id>/active` | `active` = `1` (activar) o `0` (desactivar) |
| `/admin/projects/<id>/hide`, `/show`, `/delete` | ninguno |
| `/projects/<id>/hide`, `/show`, `/delete` (dueño) | ninguno |
| `/projects/new` | `title`, `description` |

Después de cada POST: `flash("texto", "success")` y `redirect` de vuelta; los avisos ya se muestran solos.
Recordar que el servidor debe volver a revisar el rol (y que el dueño solo toque lo suyo) aunque los botones estén ocultos en la página.
