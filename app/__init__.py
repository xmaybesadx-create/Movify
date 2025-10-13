from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Основная"
    
    @app.route("/about")
    def about():
        return "Про приложение"
    
    @app.route("/movies")
    def about():
        return "Фильмы"
    
    @app.route("/profile")
    def about():
        return "Профиль"
        

    from app.routes import main #Підключаем блупринт
    app.register_blueprint(main) #Підключаем маршрути

    return app
