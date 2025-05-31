from flask import Blueprint, request, jsonify
from database import cnx

transactions = Blueprint('transactions', __name__)

# Маршрут для создания операции
@transactions.route('/create', methods=['POST'])
def create_transaction():
    user_id = request.json['user_id']
    ad_id = request.json['ad_id']
    amount = request.json['amount']
    # Добавление операции в базу данных
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO transactions (user_id, ad_id, amount) VALUES (%s, %s, %s)", (user_id, ad_id, amount))
    cnx.commit()
    return jsonify({'message': 'Операция создана'})

# Маршрут для получения всех операций
@transactions.route('/all', methods=['GET'])
def get_all_transactions():
    # Получение всех операций из базы данных
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    return jsonify({'transactions': transactions})

if __name__ == '__main__':
    transactions.run(debug=True)
