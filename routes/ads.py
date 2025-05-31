from flask import Blueprint, request, jsonify
from database import cnx

auth = Blueprint('auth', __name__)

# Маршрут для регистрации пользователей
@auth.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    # Добавление пользователя в базу данных
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    cnx.commit()
    return jsonify({'message': 'Пользователь создан'})

# Маршрут для входа пользователей
@auth.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    # Проверка пользователя в базе данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        return jsonify({'message': 'Пользователь авторизован'})
    else:
        return jsonify({'message': 'Неправильный логин или пароль'})

if __name__ == '__main__':
    auth.run(debug=True)
