// Lista de carreras que depende de la lista de facultades.
// Al elegir una facultad pide sus carreras a /faculties/<id>/majors
// y responde algo así: [{"id": 7, "name": "Ingeniería Civil"}]
(function () {
    var major = document.querySelector("select[data-parent]");
    if (!major) return;

    var faculty = document.getElementById(major.dataset.parent);
    if (!faculty) return;

    var urlTemplate = major.dataset.url;
    var selected = major.dataset.selected || "";
    var lastRequest = 0;

    function reset(text, disabled) {
        major.innerHTML = "";
        var option = document.createElement("option");
        option.value = "";
        option.disabled = true;
        option.selected = true;
        option.textContent = text;
        major.appendChild(option);
        major.disabled = disabled;
    }

    function fill(majors) {
        reset("Elige", false);
        majors.forEach(function (m) {
            var option = document.createElement("option");
            option.value = m.id;
            option.textContent = m.name;
            if (String(m.id) === String(selected)) option.selected = true;
            major.appendChild(option);
        });
        // Solo la primera carga recuerda la carrera guardada
        selected = "";
    }

    function load() {
        var facultyId = faculty.value;
        var request = ++lastRequest;

        if (!facultyId) {
            reset("Primero elige tu facultad", true);
            return;
        }

        reset("Cargando carreras…", true);

        fetch(urlTemplate.replace("{id}", encodeURIComponent(facultyId)), {
            headers: { "Accept": "application/json" }
        })
            .then(function (response) {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(function (majors) {
                // Si eligió otra facultad mientras tanto, esta respuesta ya no sirve
                if (request === lastRequest) fill(majors);
            })
            .catch(function () {
                if (request === lastRequest) reset("No se pudieron cargar. Elige la facultad otra vez.", true);
            });
    }

    faculty.addEventListener("change", load);

    // Al abrir la página (o si el formulario volvió con error) carga según la facultad ya elegida
    if (faculty.value) load();
})();
