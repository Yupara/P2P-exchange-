from flask import Blueprint, request, jsonify
from database import cnx

support = Blueprint('support', __name__)

# Маршрут для отправки сообщения поддержке
@support.route('/send', methods=['POST'])
def send_message():
    message = request.json['message']
    # Добавление сообщения в базу данных
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO support (message) VALUES (%s)", (message,))
    cnx.commit()
    return jsonify({'message': 'Сообщение отправлено'})

# Маршрут для получения всех сообщений поддержке
@support.route('/all', methods=['GET'])
def get_all_messages():
    # Получение всех сообщений из базы данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM support")
    messages = cursor.fetchall()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    support.run(debug=True)
