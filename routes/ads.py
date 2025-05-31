from flask import Blueprint, request, jsonify
from database import cnx

ads = Blueprint('ads', __name__)

# Маршрут для создания объявления
@ads.route('/create', methods=['POST'])
def create_ad():
    title = request.json['title']
    description = request.json['description']
    price = request.json['price']
    # Добавление объявления в базу данных
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO ads (title, description, price) VALUES (%s, %s, %s)", (title, description, price))
    cnx.commit()
    return jsonify({'message': 'Объявление создано'})

# Маршрут для получения всех объявлений
@ads.route('/all', methods=['GET'])
def get_all_ads():
    # Получение всех объявлений из базы данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM ads")
    ads = cursor.fetchall()
    return jsonify({'ads': ads})

if __name__ == '__main__':
    ads.run(debug=True)
