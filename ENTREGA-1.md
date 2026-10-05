# Entrega 1: CRUD y Login con MVC

> Esta tarea es parte del proyecto del semestre y se revisa en la próxima sesión presencial como parte de la calificación.

## Enunciado

### Desarrollo de la aplicación (CRUD y Login con MVC)

- Crear una aplicación básica aplicando el patrón **MVC** y las operaciones **CRUD** (Crear, Leer, Actualizar, Eliminar). **(3 pts)**
- Implementar un sistema de **autenticación (Login)** dentro del mismo proyecto MVC. **(5 pts)**
  - El usuario accede con usuario y contraseña a una sección protegida (CRUD).
  - Las URLs protegidas no deben ser accesibles sin autenticación.

### Entregar

- **Video breve** (máx. 3 minutos) en [Loom](https://www.loom.com/) o [YouTube](https://youtube.com/) mostrando: **(1 pt)**
  - El funcionamiento del Login.
  - Que no es posible acceder a la sección protegida sin iniciar sesión.
- **Repositorio en Git** con el código ordenado y un README bien elaborado. **(1 pt)**
  - Referencia: [Cómo escribir un buen README](https://www.aluracursos.com/blog/como-escribir-un-readme-increible-en-tu-github)

## Puntaje

| Criterio | Puntos |
|---|---|
| Aplicación con patrón MVC y CRUD | 3 |
| Login con sección y URLs protegidas | 5 |
| Video demostrativo (máx. 3 min) | 1 |
| Repositorio ordenado y README | 1 |
| **Total** | **10** |

## Cómo se aplica en TeamUp

- **CRUD:** gestión de **proyectos** (crear, ver, editar y eliminar un proyecto con sus roles).
- **Login:** registro e inicio de sesión de estudiantes con usuario (correo) y contraseña.
- **Sección protegida:** publicar, editar y eliminar proyectos solo con sesión iniciada. Si alguien entra a esas URLs sin sesión, se le redirige al login.

## Checklist

- [ ] Estructura MVC en Flask (modelos, vistas/plantillas, controladores/rutas)
- [ ] CRUD de proyectos funcionando
- [ ] Registro e inicio de sesión
- [ ] Cierre de sesión
- [ ] URLs del CRUD protegidas (redirigen al login sin sesión)
- [ ] README actualizado con instrucciones para correr el proyecto
- [ ] Video de máximo 3 minutos grabado y enlazado
