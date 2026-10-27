# Entrega 2: Administración, validaciones y deploy

## Enunciado

1. El Admin debe tener al menos 1 validación en Back-End de algún dato sensible para su core. Por ejemplo, si la cédula es un dato sensible, no puede validarse solo con JS: tiene que validarse en el back-end antes de grabarse en la base de datos.
2. Cuando se tiene referencia a otra tabla para ingresar datos, esta no puede ser un input simple. Ejemplo: para cargar una ciudad nueva se escribe su nombre, pero el país se escoge de un dropdown, y al escoger el país, el dropdown de provincias se carga con las provincias de ese país.
3. El código debe estar versionado en Git (con README) y desplegado en un servidor (no localhost).

## Cómo se aplica en TeamUp

| Requisito | En TeamUp |
|---|---|
| Validación de un dato sensible en el back-end | **Cédula ecuatoriana** (algoritmo completo y que no esté repetida) y **dominio del correo institucional**. Las dos se validan en Flask antes de guardar, nunca con JS |
| Llave foránea con dropdown dependiente | **Facultad → Carrera**: al elegir la facultad, el dropdown de carreras muestra solo las de esa facultad. Además, el admin elige el **rol** de un usuario desde un dropdown |
| Administración (back office) | **Roles** (estudiante y administrador) y **vistas protegidas por rol**. El admin gestiona usuarios y puede **inhabilitar o eliminar proyectos** |
| Git, README y deploy | Rama `dev` con merge a `stage` y `main`, README actualizado y app desplegada en un servidor |

## Alcance de esta entrega

**Entra:**
- Validador de cédula y validador de dominio del correo, en el back-end.
- Cascada Facultad → Carrera en el registro y en el perfil.
- Tabla de roles, vistas protegidas por rol y panel de administración.
- Proyectos mínimos: un estudiante crea un proyecto (título y descripción). El admin puede inhabilitarlo, habilitarlo o eliminarlo. El dueño puede hacer lo mismo, pero solo con los suyos.
- Deploy.

**No entra todavía:** integrantes de un proyecto, postulaciones, vitrina, créditos ni el CRUD completo de proyectos.

## Reparto

### Camilo: back-end

1. **Validadores** (`teamup/validators.py`)
   - Cédula: 10 dígitos, provincia válida (01 a 24, o 30), tercer dígito menor que 6, dígito verificador (módulo 10) y que no exista ya en la base.
   - Dominio del correo: debe terminar en el dominio institucional. El dominio sale de la variable de entorno `ALLOWED_EMAIL_DOMAIN`, no se escribe en el código.
   - Columna `id_number` en `users` (texto, única). La cédula no se puede editar desde el perfil.
2. **Cascada (parte del servidor)**
   - Ruta en JSON con las carreras de una facultad.
   - Campo `faculty` en los formularios de registro y perfil.
   - Validación de que la carrera pertenezca a la facultad elegida.
3. **Roles**
   - Tabla `roles` (`student`, `admin`) y columna `role_id` en `users`.
   - Decorador `@role_required("admin")`: si el usuario no tiene el rol, responde 403.
   - Comando `flask create-admin` para crear el primer administrador desde la consola.
4. **Panel de administración**
   - Lista de usuarios, cambio de rol desde un dropdown y activar o desactivar cuentas.
5. **Proyectos mínimos**
   - Modelo `Project` (título, descripción, dueño, estado activo o inhabilitado).
   - Crear proyecto, inhabilitar o habilitar y eliminar. Los permisos se revisan en el servidor (admin, o dueño del proyecto).
   - Los proyectos inhabilitados no aparecen en Explorar.
6. **Deploy**
   - Configuración por variables de entorno, `debug` apagado, `gunicorn` y base de datos en la nube.

Cada pantalla nueva sale con una plantilla funcional y sin estilos, que después Sebastián diseña.

### Sebastián: front-end

1. **Cascada en el navegador**
   - Dropdown de facultad y dropdown de carreras en `register.html` y `profile.html`.
   - JS que, al cambiar la facultad, pide las carreras a la ruta del servidor y llena el segundo dropdown.
   - Mientras no haya facultad elegida, el dropdown de carreras queda deshabilitado.
2. **Campo de cédula** en el registro. Se muestra en el perfil, pero no se puede editar.
3. **Diseño de las pantallas nuevas** (con BEM y los colores de la marca):
   - Panel de administración: lista de usuarios con su rol.
   - Lista de proyectos para el admin, con los botones Inhabilitar, Habilitar y Eliminar (con ventana de confirmación, como la de "Eliminar cuenta").
   - Formulario para crear un proyecto y los proyectos en Explorar.
   - Página de error 403 ("No tienes permiso para ver esto").
4. **Enlace al panel** en la barra superior, visible solo para administradores.

## Acuerdos entre back y front

Los dos trabajan con estos nombres para no pisarse. Si alguno cambia, se avisa.

**Ruta de la cascada**

```
GET /faculties/<faculty_id>/majors
→ [{"id": 7, "name": "Ingeniería Civil"}, {"id": 9, "name": "Ingeniería de Software"}]
```

**Campos de los formularios** (WTForms usa el nombre del campo como `id` y `name` del HTML)

| Formulario | Campos nuevos |
|---|---|
| Registro | `id_number` (cédula), `faculty`, `major` |
| Perfil | `faculty`, `major` (la cédula solo se muestra) |
| Crear proyecto | `title`, `description` |
| Cambiar rol (admin) | `role` |

**Rutas nuevas**

| Ruta | Quién | Qué hace |
|---|---|---|
| `GET /admin/users` | admin | Lista de usuarios |
| `POST /admin/users/<id>/role` | admin | Cambia el rol |
| `POST /admin/users/<id>/toggle` | admin | Activa o desactiva la cuenta |
| `GET /admin/projects` | admin | Lista de todos los proyectos |
| `GET, POST /projects/new` | estudiante | Crear proyecto |
| `POST /projects/<id>/toggle` | admin o dueño | Inhabilita o habilita |
| `POST /projects/<id>/delete` | admin o dueño | Elimina |

**Plantillas nuevas:** `admin/users.html`, `admin/projects.html`, `project_new.html` y `403.html`.

**Variable disponible en todas las plantillas:** `current_user.is_admin`, para mostrar u ocultar el enlace al panel.

## Base de datos local

Los modelos de facultades y carreras ya cambiaron (`faculties` y `majors`, cada carrera con su facultad). `create_all()` no modifica tablas que ya existen, así que al bajar estos cambios hay que borrar las tablas viejas para que se vuelvan a crear:

```sql
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS majors;
DROP TABLE IF EXISTS faculties;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS carrera;
```

Al arrancar la app se crean de nuevo, con las facultades y las carreras ya cargadas. Después hay que registrarse otra vez.

## Checklist

- [x] Modelos de facultades y carreras relacionados
- [ ] Validador de cédula
- [ ] Validador de dominio del correo
- [ ] Ruta JSON y validación de la cascada
- [ ] Cascada en el navegador (dropdowns y JS)
- [ ] Roles, `@role_required` y `flask create-admin`
- [ ] Panel de administración de usuarios
- [ ] Proyectos mínimos: crear, inhabilitar, habilitar y eliminar
- [ ] Diseño de las pantallas nuevas y página 403
- [ ] Deploy en un servidor
- [ ] README con el enlace al sitio desplegado
