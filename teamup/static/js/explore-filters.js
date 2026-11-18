// Filtros de Explorar al instante: esconde y muestra las tarjetas en el navegador, sin recargar la página.
// Cada tarjeta trae sus datos en data-* (los arma filter_data() en controllers/main.py) y sigue las mismas
// reglas que Project.search(): por carrera o facultad cuentan los roles para esa carrera o para cualquiera.
// La dirección se actualiza (?category=2...), así que recargar o compartir el enlace conserva los filtros.
// Sin JavaScript la página funciona igual: los atajos son enlaces y el formulario se envía por GET.
(function () {
    var form = document.querySelector("[data-explore-filters]");
    var grid = document.querySelector("[data-explore-results]");
    if (!form || !grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll("[data-project]"));
    var chips = Array.prototype.slice.call(document.querySelectorAll("[data-category-chip]"));
    var clearLinks = Array.prototype.slice.call(document.querySelectorAll("[data-filter-clear]"));
    var forYou = document.querySelector("[data-for-you]");
    var empty = document.querySelector("[data-results-empty]");
    var count = document.querySelector("[data-results-count]");
    var title = document.querySelector("[data-results-title]");
    var eyebrow = document.querySelector("[data-results-eyebrow]");
    var filterCount = document.querySelector("[data-filter-count]");
    var submit = form.querySelector("[data-filter-submit]");

    // Mismos nombres que en la dirección y en ExploreFilterForm
    var names = ["category", "faculty", "major", "modality", "weekly_hours"];
    var field = {};
    names.forEach(function (name) { field[name] = form.elements[name]; });

    // Los filtros se aplican al elegir: el botón ya no hace falta
    if (submit) submit.hidden = true;

    function words(text) {
        return text ? text.split(" ") : [];
    }

    function current() {
        var values = {};
        names.forEach(function (name) {
            var select = field[name];
            // La carrera solo cuenta si su lista está activa (ya cargó las carreras de la facultad)
            values[name] = select && !select.disabled ? select.value : "";
        });
        return values;
    }

    function matches(card, v) {
        var d = card.dataset;
        if (v.category && d.category !== v.category) return false;
        if (v.modality && d.modality !== v.modality) return false;
        if (v.weekly_hours && d.hours !== v.weekly_hours) return false;
        if (v.major) return d.anyMajor === "1" || words(d.majors).indexOf(v.major) !== -1;
        if (v.faculty) return d.anyMajor === "1" || words(d.faculties).indexOf(v.faculty) !== -1;
        return true;
    }

    function apply() {
        var v = current();
        var filtering = names.some(function (name) { return v[name]; });
        var shown = 0;

        cards.forEach(function (card) {
            var visible = matches(card, v);
            card.hidden = !visible;
            if (visible) shown += 1;
        });

        count.textContent = shown;
        if (title) title.textContent = filtering ? "Proyectos que coinciden" : "Proyectos abiertos";
        if (eyebrow) eyebrow.textContent = filtering ? "Resultados" : "Todo el campus";
        if (empty) empty.hidden = shown > 0;
        if (forYou) forYou.hidden = filtering;
        clearLinks.forEach(function (link) {
            // El enlace del mensaje vacío siempre se ve cuando aparece; el del formulario, solo con filtros
            if (link.closest("[data-explore-filters]")) link.hidden = !filtering;
        });

        // Igual que el servidor: la carrera no se cuenta aparte de la facultad
        var active = ["category", "faculty", "modality", "weekly_hours"].filter(function (n) { return v[n]; }).length;
        if (filterCount) {
            filterCount.textContent = active;
            filterCount.hidden = active === 0;
        }

        chips.forEach(function (chip) {
            chip.classList.toggle("category-bar__chip--active", chip.dataset.categoryChip === v.category);
        });

        // Deja los filtros en la dirección, sin agregar una página nueva al historial
        var params = new URLSearchParams();
        names.forEach(function (name) { if (v[name]) params.set(name, v[name]); });
        var query = params.toString();
        history.replaceState(null, "", window.location.pathname + (query ? "?" + query : ""));
    }

    function clearAll() {
        names.forEach(function (name) { if (field[name]) field[name].value = ""; });
        // Avisa a faculty-major.js para que vacíe la lista de carreras
        field.faculty.dispatchEvent(new Event("change"));
        apply();
    }

    chips.forEach(function (chip) {
        chip.addEventListener("click", function (event) {
            event.preventDefault();
            field.category.value = chip.dataset.categoryChip;
            apply();
        });
    });

    clearLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            clearAll();
        });
    });

    // Cambiar la facultad también vacía la carrera (lo hace faculty-major.js), así que se filtra igual
    form.addEventListener("change", apply);
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        apply();
    });
})();
