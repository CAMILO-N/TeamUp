// Ventana para confirmar un borrado (misma que "Eliminar cuenta").
// Cualquier botón con data-confirm-delete la abre:
//   data-action = a dónde se envía el POST, data-name = qué se va a borrar
(function () {
    var dialog = document.getElementById("delete-dialog");
    if (!dialog) return;

    var form = dialog.querySelector("form");
    var name = dialog.querySelector("[data-delete-name]");

    document.addEventListener("click", function (event) {
        var button = event.target.closest("[data-confirm-delete]");
        if (!button) return;
        form.action = button.dataset.action;
        name.textContent = button.dataset.name;
        dialog.showModal();
    });

    dialog.querySelector("[data-cancel]").addEventListener("click", function () { dialog.close(); });
    // Clic fuera de la tarjeta la cierra
    dialog.addEventListener("click", function (event) { if (event.target === dialog) dialog.close(); });
})();
