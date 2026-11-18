from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from teamup.extensions import db
from teamup.forms import ActionForm
from teamup.models.notification import Notification

notifications = Blueprint("notifications", __name__)

# Cuántos avisos se muestran en la página (los más nuevos)
PAGE_SIZE = 50


@notifications.route("/notifications")
@login_required
def index():
    items = current_user.notifications.limit(PAGE_SIZE).all()
    return render_template("notifications.html", notifications=items, csrf_form=ActionForm())


@notifications.route("/notifications/<int:notification_id>/open", methods=["POST"])
@login_required
def open_one(notification_id):
    """Marca el aviso como leído y lleva a su enlace. Es POST porque cambia datos."""
    notification = db.get_or_404(Notification, notification_id)
    if notification.user_id != current_user.id:
        abort(403)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
        return redirect(url_for("notifications.index"))

    notification.is_read = True
    db.session.commit()
    # Solo direcciones de la misma página (empiezan con /), nunca otro sitio
    if notification.link and notification.link.startswith("/") and not notification.link.startswith("//"):
        return redirect(notification.link)
    return redirect(url_for("notifications.index"))


@notifications.route("/notifications/read-all", methods=["POST"])
@login_required
def read_all():
    if ActionForm().validate_on_submit():
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
        db.session.commit()
        flash("Todos los avisos quedaron como leídos.", "success")
    else:
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    return redirect(url_for("notifications.index"))
