import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from flask_sqlalchemy import SQLAlchemy

# Создаем приложение
app = Flask(__name__)

# Загрузка аватаров
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img', 'avatars')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movify.db'
db = SQLAlchemy(app)

app.secret_key = "super-secret-key"

# ----- МОДЕЛИ -----


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    about = db.Column(db.Text)
    genres = db.Column(db.String(255))
    avatar = db.Column(db.String(255))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))


# ----- ГЛАВНЫЕ СТРАНИЦЫ -----


@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/a")
@app.route("/about")
def about():
    return render_template("about.html")


# ----- ФІЛЬМИ (в константе + id) -----


FILMS_DATA = {
    "Хоррор": [
        {"id": 101, "title": "Закляття",
         "desc": "Сім'я стикається з лякаючою потойбічною силою в новому будинку",
         "image": "Zak.jpg"},
        {"id": 102, "title": "Астрал",
         "desc": "Хлопчик впадає в кому, а його свідомість застрягає в іншому світі.",
         "image": "astral.jpg"},
        {"id": 103, "title": "Сяйво",
         "desc": "Письменник з родиною переїжджає в порожній готель, де починає божеволіти.",
         "image": "sianie.jpg"},
        {"id": 104, "title": "Тихе місце",
         "desc": "Світ, де небезпека реагує на будь-який звук.",
         "image": "quiet_place.jpg"},
        {"id": 105, "title": "Воно",
         "desc": "Дітям доводиться зіткнутися з древнім злом в образі клоуна.",
         "image": "it.jpg"},
    ],
    "Драма": [
        {"id": 201, "title": "Зелена миля",
         "desc": "Історія наглядача в'язниці та в'язня з незвичайним даром.",
         "image": "green_mile.jpg"},
        {"id": 202, "title": "1+1",
         "desc": "Дружба багатого аристократа і його доглядальника змінює життя обох.",
         "image": "intouchables.jpg"},
        {"id": 203, "title": "Форрест Гамп",
         "desc": "Життя простої людини на тлі важливих подій епохи.",
         "image": "forrest_gump.jpg"},
        {"id": 204, "title": "Ігри розуму",
         "desc": "Геніальний математик бореться з власним розумом.",
         "image": "beautiful_mind.jpg"},
        {"id": 205, "title": "Врятувати рядового Райана",
         "desc": "Загін солдатів відправляють на складну місію під час війни.",
         "image": "saving_ryan.jpg"},
    ],
    "Комедія": [
        {"id": 301, "title": "Хлопці в Вегасі",
         "desc": "Весела вечірка перетворюється на хаос і пошуки нареченого.",
         "image": "hangover.jpg"},
        {"id": 302, "title": "Ми – Міллери",
         "desc": "Несправжня сім'я їде через кордон з небезпечним вантажем.",
         "image": "millers.jpg"},
        {"id": 303, "title": "Містер Бiн",
         "desc": "Незручні та смішні пригоди дивакуватого героя.",
         "image": "mr_bean.jpg"},
        {"id": 304, "title": "Один вдома",
         "desc": "Хлопчик захищає будинок від двох невдалих грабіжників.",
         "image": "home_alone.jpg"},
        {"id": 305, "title": "Клік",
         "desc": "Чоловік отримує пульт, що керує реальністю.",
         "image": "click.jpg"},
    ],
}


def find_film_by_id(film_id: int):
    for films in FILMS_DATA.values():
        for film in films:
            if film["id"] == film_id:
                return film
    return None


@app.route("/films")
def films():
    return render_template("films.html", genres=FILMS_DATA)


# ----- ПРОФІЛЬ -----


@app.route("/profile", methods=["GET", "POST"])
def profile():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("login"))

    user = User.query.get(uid)
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        user.username = request.form["username"]
        user.email = request.form.get("email")
        user.about = request.form.get("about")
        selected_genres = request.form.getlist("genres")
        user.genres = ",".join(selected_genres)

        file = request.files.get("avatar")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"user_{user.id}_{filename}"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            user.avatar = filename

        db.session.commit()
        flash("Профіль оновлено!")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ----- МУЛЬТФІЛЬМИ + УЛЮБЛЕНІ -----


CARTOONS_DATA = {
    "Пригоди": [
        {"id": 1, "title": "Коко",
         "desc": "Хлопчик Міґель потрапляє до Країни Мертвих, щоб розкрити таємницю своєї родини.",
         "image": "coco.jpg"},
        {"id": 2, "title": "У пошуках Немо",
         "desc": "Рибка-клоун вирушає в далеку подорож, щоб знайти свого сина Немо.",
         "image": "nemo.jpg"},
        {"id": 3, "title": "Хоробра серцем",
         "desc": "Принцеса Меріда кидає виклик традиціям і змінює свою долю.",
         "image": "merida.jpg"},
        {"id": 4, "title": "Рататуй",
         "desc": "Щур Ремі мріє стати шеф-кухарем у французькому ресторані.",
         "image": "ratatouille.jpg"},
        {"id": 5, "title": "Корпорація монстрів",
         "desc": "Монстри збирають дитячі крики, але все змінюється через одну дівчинку.",
         "image": "monsters_inc.jpg"},
    ],
    "Комедія": [
        {"id": 6, "title": "Шрек",
         "desc": "Огр Шрек змушений врятувати принцесу, щоб повернути собі болото.",
         "image": "shrek.jpg"},
        {"id": 7, "title": "Таємне життя домашніх тварин",
         "desc": "Тварини влаштовують пригоди, поки господарів немає вдома.",
         "image": "pets.jpg"},
        {"id": 8, "title": "Алладін",
         "desc": "Хлопець з вулиці знаходить чарівну лампу з джином.",
         "image": "aladdin.jpg"},
        {"id": 9, "title": "Зоотрополіс",
         "desc": "Кролиця-поліцейська та лис-авантюрист розслідують змову у місті тварин.",
         "image": "zootopia.jpg"},
        {"id": 10, "title": "Льодовиковий період",
         "desc": "Команда тварин переживає пригоди під час льодовикового періоду.",
         "image": "ice_age.jpg"},
    ],
    "Сімейні": [
        {"id": 11, "title": "Крижане серце",
         "desc": "Анна вирушає на пошуки сестри Ельзи, яка володіє крижаною магією.",
         "image": "frozen.jpg"},
        {"id": 12, "title": "Король Лев",
         "desc": "Сімба має прийняти своє королівське призначення після трагедії.",
         "image": "lion_king.jpg"},
        {"id": 13, "title": "Ральф-руйнівник",
         "desc": "Лиходій з відеогри мріє стати героєм і змінити свою роль.",
         "image": "ralph.jpg"},
        {"id": 14, "title": "Вгору",
         "desc": "Дідусь і хлопчик летять на будинку з повітряними кулями до мрії.",
         "image": "up.jpg"},
        {"id": 15, "title": "Історія іграшок",
         "desc": "Іграшки оживають і потрапляють у справжні пригоди, коли людей немає поруч.",
         "image": "toy_story.jpg"},
    ],
}


def find_cartoon_by_id(cartoon_id: int):
    for films in CARTOONS_DATA.values():
        for film in films:
            if film["id"] == cartoon_id:
                return film
    return None


@app.route("/cartoons")
def cartoons():
    return render_template("cartoons.html", genres=CARTOONS_DATA)


@app.route("/favorite/add", methods=["POST"])
def add_favorite():
    if "user_id" not in session:
        flash("Щоб додати в улюблені, увійдіть в акаунт.")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cartoon_id = request.form.get("cartoon_id", type=int)
    film_id = request.form.get("film_id", type=int)

    if not cartoon_id and not film_id:
        abort(400)

    # Визначаємо, що додаємо / видаляємо: мультфільм чи фільм
    item = None
    obj_id = None
    redirect_endpoint = None

    if cartoon_id is not None:
        item = find_cartoon_by_id(cartoon_id)
        redirect_endpoint = "cartoons"
        obj_id = cartoon_id
    elif film_id is not None:
        item = find_film_by_id(film_id)
        redirect_endpoint = "films"
        obj_id = film_id

    if item is None or obj_id is None or redirect_endpoint is None:
        abort(404)

    # Перевіряємо, чи вже є в улюблених (toggle)
    existing = Favorite.query.filter_by(user_id=user_id, movie_id=obj_id).first()

    if existing:
        # Якщо є – видаляємо (повторне натискання)
        db.session.delete(existing)
        db.session.commit()
        flash("Видалено з улюблених.")

        if redirect_endpoint == "cartoons":
            return redirect(url_for("cartoons") + "#cartoons-section")
        elif redirect_endpoint == "films":
            return redirect(url_for("films") + "#films-section")
        return redirect(url_for(redirect_endpoint))

    # Якщо немає – додаємо
    movie = Movie.query.get(obj_id)
    if not movie:
        movie = Movie(id=obj_id, title=item["title"])
        db.session.add(movie)
        db.session.commit()

    fav = Favorite(user_id=user_id, movie_id=movie.id)
    db.session.add(fav)
    db.session.commit()
    flash("Додано в улюблені!")

    if redirect_endpoint == "cartoons":
        return redirect(url_for("cartoons") + "#cartoons-section")
    elif redirect_endpoint == "films":
        return redirect(url_for("films") + "#films-section")
    return redirect(url_for(redirect_endpoint))


@app.route("/favorite")
def favorite():
    if "user_id" not in session:
        flash("Увійдіть, щоб переглянути улюблені.")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    movies = []

    # будуємо повноцінні картки з даних мультфільмів/фільмів
    for fav in favorites:
        mid = fav.movie_id

        cartoon = find_cartoon_by_id(mid)
        if cartoon:
            movies.append({
                "id": mid,
                "title": cartoon["title"],
                "desc": cartoon["desc"],
                "image": cartoon["image"],
                "type": "cartoon",
            })
            continue

        film = find_film_by_id(mid)
        if film:
            movies.append({
                "id": mid,
                "title": film["title"],
                "desc": film["desc"],
                "image": film["image"],
                "type": "film",
            })

    return render_template("favorite.html", movies=movies)


def get_favorite_ids_for_current_user():
    uid = session.get("user_id")
    if not uid:
        return set()
    favs = Favorite.query.filter_by(user_id=uid).all()
    return {f.movie_id for f in favs}


@app.context_processor
def inject_current_user():
    uid = session.get("user_id")
    user = User.query.get(uid) if uid else None
    favorite_ids = get_favorite_ids_for_current_user()
    return {
        "current_user": user,
        "favorite_ids": favorite_ids,
    }


# ----- НАЛАШТУВАННЯ -----


@app.route("/settings")
def settings():
    return render_template("settings.html")


# ----- АВТОРИЗАЦІЯ -----


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Користувач з таким ім'ям уже існує. Оберіть інший логін.")
            return redirect(url_for("register"))

        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        flash("Реєстрація успішна! Тепер увійдіть.")
        return redirect(url_for("login"))

    return render_template("register.html", body_class="login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user:
            session["user_id"] = user.id
            flash("Вхід успішний!")
            return redirect(url_for("profile"))
        else:
            flash("Користувача не знайдено.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Ви вийшли з акаунту.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
