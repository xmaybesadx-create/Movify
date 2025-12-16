# Movify — Пошук та каталогізація фільмів

## Опис

Movify — це веб-додаток, який дозволяє користувачам шукати фільми, переглядати детальну інформацію про них, додавати у “Вибране” та створювати власну колекцію переглядів.
Сервіс використовує TMDB API для отримання даних про фільми та реалізований на Flask (Python) з базою даних SQLite.

### Структура репозиторію
1. /backend — серверна частина на Flask (Python)
2. /frontend — HTML/CSS/JS інтерфейс
3. /docs — технічна документація (архітектура, діаграми, user stories)

### Технології

1. Frontend: HTML5, CSS3, JavaScript (Vanilla)
2. Backend: Python, Flask, Flask-Login, Requests
3. Database: SQLite + SQLAlchemy
4. API: The Movie Database (TMDB)
5. Інструменти: Postman (тестування API), GitHub (контроль версій)
6. CI/CD: Git + GitHub Actions (планується)

### Автор
- Марія Лагодна — повний цикл розробки (Frontend + Backend + база даних + API інтеграція + UI)
- Роль: Full-Stack Developer, Project Manager

### Архітектура
Проєкт побудовано за модульною архітектурою, де клієнтська частина (Frontend) взаємодіє з серверною (Backend) через HTTP/REST API.
Усі дані про користувачів, обрані фільми та запити зберігаються у реляційній базі даних SQLite.
Основні компоненти:
1. Frontend: відображення сторінок, пошук, інтерактивність, передача запитів на сервер
2. Backend (Flask): бізнес-логіка, маршрути, авторизація, з’єднання з API TMDB
3. Database: збереження користувачів та їх вибраних фільмів
4. TMDB API: зовнішнє джерело даних про фільми

### Документація

- [Список компонентів](docs/architecture/components.md)
- [Діаграма архітектури (v1)](docs/architecture/architecture_v1.drawio)
- [Таблиця відповідальностей](docs/architecture/ownership.md)
