from flask import Flask, render_template, request, redirect, url_for, flash
from teamup.extensions import db


def create_app():
  
    app = Flask(__name__)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://@localhost/TeamUp?driver=ODBC+Driver+17+for+SQL+Server"
    
    db.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")
      
    
    @app.route("/login")
    def login():
        return render_template("login.html")
    
    @app.route("/register")
    def register():
        return render_template("register.html")

    return app
