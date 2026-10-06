

from flask import Flask, render_template, request, redirect, url_for, flash


def create_app():
  
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
