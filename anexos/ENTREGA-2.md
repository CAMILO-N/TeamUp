# Entrega 2: qué hacemos y quién lo hace

## Qué pide el profe (en palabras simples)

1. **Validar un dato importante en el servidor.** No basta con revisarlo en la página con JavaScript: el servidor tiene que revisarlo antes de guardarlo.
2. **Nada de escribir ids a mano.** Si un dato depende de otra tabla, se elige de una lista. Y si hay dos listas relacionadas, la segunda cambia según lo que elijas en la primera (como país y provincia).
3. **Administración.** Un administrador que maneja usuarios, permisos y lo más importante del sistema, con pantallas que solo él puede ver.
4. **Subirlo a internet.** La página tiene que funcionar en un servidor, no solo en nuestra computadora. Y el código va en Git con su README.

## Qué vamos a hacer en TeamUp

1. **Cédula y correo.** Al registrarse, el servidor revisa que la cédula ecuatoriana sea válida y que no esté repetida, y que el correo sea el institucional.
2. **Facultad y carrera.** Primero eliges tu facultad; la lista de carreras muestra solo las de esa facultad.
3. **Administrador.** Puede ver a todos los usuarios, cambiarles el rol y desactivar cuentas.
4. **Proyectos (versión mínima).** Un estudiante crea un proyecto con título y descripción. El administrador puede ocultarlo o borrarlo. El dueño también puede, pero solo con los suyos.
5. **Subir la página a internet.**

**No entra todavía:** unirse a proyectos, postulaciones, vitrina ni créditos.

---

## Camilo: lo que pasa por dentro (servidor)

1. **Revisar la cédula.**
   El servidor comprueba que la cédula tenga el formato correcto y que nadie más la haya registrado. Si está mal, no se guarda y se muestra el error.
   *Terminado cuando:* una cédula inventada o repetida da error, aunque alguien modifique la página.

2. **Revisar el correo.**
   Solo se aceptan correos del dominio institucional.
   *Terminado cuando:* un correo de Gmail da error.

3. **Mandar las carreras de cada facultad.**
   Una dirección a la que la página le pregunta "¿qué carreras tiene esta facultad?" y responde la lista. Además, el servidor revisa que la carrera elegida sí sea de esa facultad.
   *Terminado cuando:* Sebas puede pedir las carreras desde su JavaScript.

4. **Roles.**
   Cada usuario es **estudiante** o **administrador**. Las pantallas de administración solo se abren para los administradores; los demás ven un "No tienes permiso".
   *Terminado cuando:* un estudiante que escribe la dirección del panel a mano no puede entrar.

5. **Panel del administrador.**
   Ver la lista de usuarios, cambiarles el rol (eligiéndolo de una lista) y desactivar cuentas.
   *Terminado cuando:* funciona, aunque todavía se vea feo.

6. **Proyectos mínimos.**
   Crear un proyecto, ocultarlo, volver a mostrarlo y borrarlo. Los proyectos ocultos no aparecen en Explorar.
   *Terminado cuando:* el administrador puede ocultar o borrar cualquier proyecto y el dueño solo los suyos.

7. **Subir la página a internet.**
   *Terminado cuando:* se puede abrir desde otro celular o computadora.

Cada pantalla nueva sale funcionando pero sin diseño. Después Sebas la deja bonita.

## Sebastián: lo que ve el usuario (diseño y página)

1. **Las dos listas de facultad y carrera** en el registro y en "Mi perfil".
   Al elegir una facultad, la lista de carreras se actualiza sola. Mientras no se elija facultad, la de carreras queda bloqueada.
   *Necesita de Camilo:* la tarea 3. Mientras tanto, puede armar el diseño con datos de prueba.

2. **Campo de cédula** en el registro. En "Mi perfil" se muestra, pero no se puede cambiar.

3. **Diseño de las pantallas nuevas**, con el mismo estilo de TeamUp:
   - Panel del administrador con la lista de usuarios.
   - Lista de proyectos para el administrador, con botones para ocultar, mostrar y borrar (el de borrar pide confirmación, como "Eliminar cuenta").
   - Formulario para crear un proyecto, y los proyectos en Explorar.
   - Página de "No tienes permiso".

4. **Enlace al panel** en la barra de arriba, que solo lo vean los administradores.

---

## Antes de empezar (los dos)

Las tablas de la base cambiaron. Después de bajar los cambios, hay que borrar las tablas viejas en SQL Server; al arrancar la app se vuelven a crear solas, con las facultades y carreras ya cargadas:

```sql
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS majors;
DROP TABLE IF EXISTS faculties;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS carrera;
```

Después hay que registrarse de nuevo.

## Nombres que acordamos (para consulta)

Para que lo de cada uno encaje, usamos estos nombres. Si alguien necesita cambiar uno, avisa.

- **Pedir las carreras de una facultad:** `/faculties/<id>/majors`. Responde algo así: `[{"id": 7, "name": "Ingeniería Civil"}]`
- **Campos del registro:** `id_number` (cédula), `faculty` (facultad), `major` (carrera)
- **Campo para crear un proyecto:** `title` y `description`
- **Pantallas nuevas:** `/admin/users` (usuarios), `/admin/projects` (proyectos), `/projects/new` (crear proyecto)
- **Saber si quien está viendo la página es administrador:** `current_user.is_admin`

## Avance

- [x] Facultades y carreras en la base
- [ ] Revisar la cédula (Camilo)
- [ ] Revisar el correo (Camilo)
- [ ] Mandar las carreras de cada facultad (Camilo)
- [ ] Listas de facultad y carrera en la página (Sebastián)
- [ ] Roles y pantallas protegidas (Camilo)
- [ ] Panel del administrador (Camilo)
- [ ] Proyectos mínimos (Camilo)
- [ ] Diseño de las pantallas nuevas (Sebastián)
- [ ] Subir la página a internet (Camilo)
- [ ] README con el enlace a la página
