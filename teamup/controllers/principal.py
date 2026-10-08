from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

principal = Blueprint("principal", __name__)


@principal.route("/")
def index():
    # Si ya inicio  va directo a Explorar
    if current_user.is_authenticated:
        return redirect(url_for("principal.explorar"))
    return render_template("index.html")


@principal.route("/explorar")
@login_required
def explorar():
    return render_template("explorar.html")
