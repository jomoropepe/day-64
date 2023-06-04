from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests

# API URL to search information about the movies
MOVIES_URL = "https://api.themoviedb.org/3/search/movie"
FIND_MOVIE_URL = "https://api.themoviedb.org/3/movie/"
# Headers of the movies API
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxZTEzODFiNjA4ZTZiZTVkMjczZjg4ZTA5Yjg4MTU1ZSIsInN1YiI6IjY0NzkxNGEzY2FlZjJkMDBkZjg3NjYzMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.2Sl2y4TcJdVVORkSHcnhnVok1dMG4VuptkYrNc1KwFI"
}
# URL to show an image of an specific movie
IMG_URL = "http://image.tmdb.org/t/p/w500/"

# Create Flask app, with Bootstrap included
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///D:/Estudio/Investigaciones/Programar/Udemy - 100 Days of Code The Complete Python Pro Bootcamp for 2022 2021-11/64 - Day 64 - Advanced -My Top 10 Movies Website/37400910-Starting-Files-movie-project-start/movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(500))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

with app.app_context():
    db.create_all()


# EDIT RATING FORM
class RatingForm(FlaskForm):
    rating = FloatField(label="Your Raing out of 10", validators=[DataRequired(), NumberRange(min=0, max=10, message="You should enter a number between 0 and 10")])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


# NEW MOVIE FORM
class MovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    add_movie = SubmitField(label="Add Movie")

# Example of values of a new object in the Database
# with app.app_context():
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()


# READ ALL RECORDS
with app.app_context():
    all_movies = db.session.query(Movie).all()

# Home page wich shows all the movies in the DB, ordered by the rating of each one.
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


# Add a movie to the database
@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = MovieForm()
    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        paramaters = {
            "query": movie_title,
            "page": 1
        }
        response = requests.get(url=MOVIES_URL, headers=headers, params=paramaters)
        data = response.json()["results"]
        print(data)
        return render_template("select.html", movies=data)
    return render_template("add.html", form=add_form)


# Find the data about the movie selected to be added
@app.route("/find")
def find():
    movie_id = request.args.get("id")
    print(movie_id)
    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_id}", headers=headers)
    data= response.json()
    print(data)
    # new_movie_id = len(all_movies) + 1
    new_movie = Movie(title=data["original_title"],year=data["release_date"].split("-")[0], description=data["overview"], img_url=f"{IMG_URL}{data['poster_path']}")
    db.session.add(new_movie)
    db.session.commit()
    print(new_movie.id)
    return redirect(url_for("edit", id=new_movie.id))


# Edit the rating and the review of the movie selected
@app.route("/edit", methods=["GET", "POST"])
def edit():
    rating_form = RatingForm()
    movie_id = request.args.get("id")
    print(movie_id)
    movie_selected = Movie.query.get(movie_id)
    print(movie_selected)
    if rating_form.validate_on_submit():
        movie_selected.rating = request.form["rating"]
        movie_selected.review = request.form["review"]
        db.session.commit()
        print(movie_selected.rating)
        print(movie_selected.review)
        return redirect(url_for('home'))
    # EDIT RATING RECORD
    return render_template("edit.html", movie=movie_selected, form=rating_form)


# Delete the movie selected
@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
