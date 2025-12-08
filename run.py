import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask import session
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy

# Создаем приложение
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img', 'avatars')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movify.db'
db = SQLAlchemy(app)

db.Model.metadata.remove(db.Model.metadata.tables.get("user", None)) if "user" in db.Model.metadata.tables else None

app.secret_key = "super-secret-key"

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

@app.route("/")
@app.route("/home")
def index():
    return  render_template("index.html")

@app.route("/a")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/films")
def films():
    genres = {
        "Хоррор": [
            {"title": "Закляття", "desc": "Сім'я стикається з лякаючою потойбічною силою в новому будинку", "image": "Zak.jpg"},
            {"title": "Астрал", "desc": "Хлопчик впадає в кому, а його свідомість застрягає в іншому світі.", "image": "astral.jpg"},
            {"title": "Сяйво", "desc": "Письменник з родиною переїжджає в порожній готель, де починає божеволіти.", "image": "sianie.jpg"},
            {"title": "Тихе місце", "desc": "Світ, де небезпека реагує на будь-який звук.", "image": "quiet_place.jpg"},
            {"title": "Воно", "desc": "Дітям доводиться зіткнутися з древнім злом в образі клоуна.", "image": "it.jpg"},
        ],
        "Драма": [
            {"title": "Зелена миля", "desc": "Історія наглядача в'язниці та в'язня з незвичайним даром.", "image": "green_mile.jpg"},
            {"title": "1+1", "desc": "Дружба багатого аристократа і його доглядальниці змінює життя обох.", "image": "intouchables.jpg"},
            {"title": "Форрест Гамп", "desc": "Життя простої людини на тлі важливих подій епохи.", "image": "forrest_gump.jpg"},
            {"title": "Ігри розуму", "desc": "Геніальний математик бореться з власним розумом.", "image": "beautiful_mind.jpg"},
            {"title": "Врятувати рядового Райана", "desc": "Загін солдатів відправляють на складну місію під час війни.", "image": "saving_ryan.jpg"},
        ],
        "Комедія": [
            {"title": "Хлопці в Вегасі", "desc": "Весела вечірка перетворюється на хаос і пошуки нареченого.", "image": "hangover.jpg"},
            {"title": "Ми – Міллери", "desc": "Несправжня сім'я їде через кордон з небезпечним вантажем.", "image": "millers.jpg"},
            {"title": "Містер Бiн", "desc": "Незручні та смішні пригоди дивакуватого героя.", "image": "mr_bean.jpg"},
            {"title": "Один вдома", "desc": "Хлопчик захищає будинок від двох невдалих грабіжників.", "image": "home_alone.jpg"},
            {"title": "Клік", "desc": "Чоловік отримує пульт, що керує реальністю.", "image": "click.jpg"},
        ],
    }
    return render_template("films.html", genres=genres)



@app.route("/profile", methods=["GET", "POST"])
def profile():
    # берем id залогиненого користувача із сесії
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("login"))

    user = User.query.get(uid)
    if not user:
        # якщо раптом користувача з таким id нема — просимо залогінитись
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


@app.route("/cartoons")
def cartoons():
    genres = {
        "Пригоди": [
            {"title": "Коко", "desc": "Хлопчик Міґель потрапляє до Країни Мертвих, щоб розкрити таємницю своєї родини.", "image": "coco.jpg"},
            {"title": "У пошуках Немо", "desc": "Рибка-клоун вирушає в далеку подорож, щоб знайти свого сина Немо.", "image": "nemo.jpg"},
            {"title": "Хоробра серцем", "desc": "Принцеса Меріда кидає виклик традиціям і змінює свою долю.", "image": "merida.jpg"},
            {"title": "Рататуй", "desc": "Щур Ремі мріє стати шеф-кухарем у французькому ресторані.", "image": "ratatouille.jpg"},
            {"title": "Корпорація монстрів", "desc": "Монстри збирають дитячі крики, але все змінюється через одну дівчинку.", "image": "monsters_inc.jpg"},
        ],
        "Комедія": [
            {"title": "Шрек", "desc": "Огр Шрек змушений врятувати принцесу, щоб повернути собі болото.", "image": "shrek.jpg"},
            {"title": "Таємне життя домашніх тварин", "desc": "Тварини влаштовують пригоди, поки господарів немає вдома.", "image": "pets.jpg"},
            {"title": "Алладін", "desc": "Хлопець з вулиці знаходить чарівну лампу з джином.", "image": "aladdin.jpg"},
            {"title": "Зоотрополіс", "desc": "Кролиця-поліцейська та лис-авантюрист розслідують змову у місті тварин.", "image": "zootopia.jpg"},
            {"title": "Льодовиковий період", "desc": "Команда тварин переживає пригоди під час льодовикового періоду.", "image": "ice_age.jpg"},
        ],
        "Сімейні": [
            {"title": "Крижане серце", "desc": "Анна вирушає на пошуки сестри Ельзи, яка володіє крижаною магією.", "image": "frozen.jpg"},
            {"title": "Король Лев", "desc": "Сімба має прийняти своє королівське призначення після трагедії.", "image": "lion_king.jpg"},
            {"title": "Ральф-руйнівник", "desc": "Лиходій з відеогри мріє стати героєм і змінити свою роль.", "image": "ralph.jpg"},
            {"title": "Вгору", "desc": "Дідусь і хлопчик летять на будинку з повітряними кулями до мрії.", "image": "up.jpg"},
            {"title": "Історія іграшок", "desc": "Іграшки оживають і потрапляють у справжні пригоди, коли людей немає поруч.", "image": "toy_story.jpg"},
        ],
    }
    return render_template("cartoons.html", genres=genres)


@app.route("/settings")
def settings():
    return  render_template("settings.html")

@app.route("/favorite")
def favorite():
    return  render_template("favorite.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]

        # проверка, есть ли уже такой пользователь
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

@app.context_processor
def inject_current_user():
    uid = session.get("user_id")
    user = User.query.get(uid) if uid else None
    return {"current_user": user}

if __name__ == "__main__":
    app.run(debug=True)        
