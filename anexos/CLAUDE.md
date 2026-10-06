# TeamUp: contexto del proyecto

Proyecto integrador de la materia **Ingeniería Web**, hecho en pareja por Camilo (CAMILO-N) y Sebastián.

## Qué es

TeamUp es una plataforma web donde estudiantes de una misma universidad publican proyectos de cualquier área (cortometrajes, startups, investigación, arte, eventos, podcasts) y arman equipos interdisciplinarios con compañeros de otras carreras.

- Slogan: **"Juntos, las ideas despegan."**
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

- Backend: Python + **Flask**, con patrón **MVC**.
- Base de datos: **SQL Server**.
- Conexión: **pyodbc** con el **ODBC Driver 18 for SQL Server** (cadena tipo `mssql+pyodbc://...?driver=ODBC+Driver+18+for+SQL+Server`).
- Acceso a datos: **ORM con Flask-SQLAlchemy**. Los modelos (`Usuario`, `Proyecto`, `Rol`, etc.) son la capa "M" del MVC. Si alguna consulta compleja lo justifica, se puede usar SQL directo puntual, siempre parametrizado.
- Autenticación: Flask-Login sobre el modelo `Usuario`, con contraseñas hasheadas.
- Vistas: archivos HTML en `app/templates/` servidos con `render_template` de Flask, **sin sintaxis Jinja** (nada de `{% %}` ni `{{ }}`). CSS, JS e imágenes en `app/static/`.

## Entrega actual

Ver `anexos/ENTREGA-1.md`. Resumen:

- CRUD aplicando MVC. En TeamUp, el CRUD es de **proyectos**.
- Login con usuario y contraseña. Las URLs del CRUD deben estar protegidas: sin sesión iniciada, redirigir al login.
- Repositorio ordenado y README bien hecho.
- Video de máximo 3 minutos mostrando el login y que la sección protegida no es accesible sin sesión.

## Ramas y commits

- `main`: versión estable. `stage`: pruebas e integración. `dev`: desarrollo diario.
- Trabajar en `dev` (o en ramas `feature/...` que salen de `dev`). Luego pasar a `stage` y al final a `main`. Nunca hacer push directo a `main`.
- Commits a nombre de CAMILO-N con el correo `153507573+CAMILO-N@users.noreply.github.com`.
- **No agregar líneas de coautoría ni menciones a Claude** en commits, PRs ni archivos del repo.
- Mensajes de commit en español, cortos y claros.

## README

- Sin emojis.
- No incluir modelo de datos, flujo de ramas, siguientes etapas, tipos de usuario ni sección de equipo, salvo que se pida.
- Mantener: qué es, el problema, cómo funciona (diagrama), funcionalidades y la sección "Prototipo y arte" con el enlace de Figma.

## Diseño y marca

- Prototipo en Figma: https://www.figma.com/make/egdPMLaIE0ehRj88IliyMb/Responsive-Web-Prototype-for-TeamUp?t=sDEuayFbezUxM6km-1
- Logo: dos personitas chocando la mano en alto (una coral, otra ocre) más la palabra "teamup" en minúsculas, con "up" en coral. Archivo: `assets/logo.png`.
- Estilo: modo oscuro con cuadrícula de puntos sutil, tarjetas muy redondeadas, brillo coral suave en elementos clave, chips y botones en píldora.
- Colores: coral `#E4572E` (principal), rojo teja `#C4402A`, ocre `#F2B33D` (etiquetas), carbón `#17161A` (fondo oscuro), superficies `#222126`, bordes `#34323A`, hueso `#FAF7F2`, gris cálido `#A29D97`.
- Tipografías: Space Grotesk (títulos) e IBM Plex Sans (texto).
