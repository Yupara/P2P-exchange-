from flask import Blueprint, request, jsonify
from database import cnx

admin = Blueprint('admin', __name__)

# Маршрут для входа в администраторский кабинет
@admin.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    # Проверка администратора в базе данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()
    if admin:
        return jsonify({'message': 'Администратор авторизован'})
    else:
        return jsonify({'message': 'Неправильный логин или пароль'})

# Маршрут для получения всех пользователей
@admin.route('/users', methods=['GET'])
def get_all_users():
    # Получение всех пользователей из базы данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify({'users': users})

if __name__ == '__main__':
    admin.run(debug=True)
