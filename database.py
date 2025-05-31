import mysql.connector

# Настройки базы данных
db_host = 'localhost'
db_user = 'root'
db_password = 'password'
db_name = 'p2p_database'

# Создание соединения с базой данных
cnx = mysql.connector.connect(
    user=db_user,
    password=db_password,
    host=db_host,
    database=db_name
)

# Создание таблицы пользователей
cursor = cnx.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT,
        username VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255),
        PRIMARY KEY (id)
    );
""")

# Создание таблицы объявлений
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ads (
        id INT AUTO_INCREMENT,
        user_id INT,
        title VARCHAR(255),
        description TEXT,
        price DECIMAL(10, 2),
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
""")

# Создание таблицы операций
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT,
        user_id INT,
        ad_id INT,
        amount DECIMAL(10, 2),
        status VARCHAR(255),
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (ad_id) REFERENCES ads (id)
    );
""")
