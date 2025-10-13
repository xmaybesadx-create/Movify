from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "index.html"

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/movies")
def movies():
    return render_template("movies.html")

@main.route("/profile")
def profile():
    return render_template("profile.html")
