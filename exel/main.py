import pandas as pd
import mysql.connector
from mysql.connector import Error

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'f1s22731S',
    'database': 'samui_real_estate'
}

def import_excel_to_mysql(db_config, excel_file):
    data = pd.read_excel(excel_file, sheet_name='ДЛЯ БОТА')
    data = data.replace({pd.NA: None, "NaN": None, "-": None, "nan": None})  # Замена NaN и "-" на None

    # Преобразование данных в стандартные типы Python
    for column in data.columns:
        if data[column].dtype == 'Int64' or data[column].dtype == 'int64':
            data[column] = data[column].astype('Int64').astype('object')
        elif data[column].dtype == 'Float64' or data[column].dtype == 'float64':
            data[column] = data[column].astype('float64').astype('object')
        elif data[column].dtype == 'O' or data[column].dtype == 'object':
            data[column] = data[column].astype('object')

    # Проверка диапазона значений для столбца 'депозит для брони %'
    if 'депозит для брони %' in data.columns:
        data['депозит для брони %'] = data['депозит для брони %'].apply(lambda x: min(max(x, 0), 100) if x is not None else x)

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute("DROP TABLE IF EXISTS properties;")
            connection.commit()

            cursor.execute("""
                CREATE TABLE properties (
                    property_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    photo1 TEXT,
                    photo2 TEXT,
                    photo3 TEXT,
                    location VARCHAR(255),
                    distance_to_sea VARCHAR(255),
                    property_type VARCHAR(255),
                    monthly_price TEXT,
                    daily_price INT,
                    minimum_nights INT,
                    booking_deposit_fixed TEXT,
                    booking_deposit_percentage TEXT,
                    security_deposit INT,
                    bedrooms INT,
                    beds INT,
                    bathrooms INT,
                    pool VARCHAR(255),
                    kitchen VARCHAR(255),
                    air_conditioners INT,
                    cleaning VARCHAR(255),
                    description TEXT,
                    utility_bill VARCHAR(255)
                );
            """)
            connection.commit()

            insert_query = """
                INSERT INTO properties (name, photo1, photo2, photo3, location, distance_to_sea,
                                        property_type, monthly_price, daily_price, minimum_nights,
                                        booking_deposit_fixed, booking_deposit_percentage, security_deposit,
                                        bedrooms, beds, bathrooms, pool, kitchen, air_conditioners,
                                        cleaning, description, utility_bill)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            # Замена всех NaN значений на None перед конвертацией в список
            data = data.where(pd.notnull(data), None)

            tuple_data = data.values.tolist()
            tuple_data = [[None if str(cell).strip().lower() == 'nan' else cell for cell in row] for row in tuple_data]

            # Проверка каждой строки на наличие 'nan'
            for row in tuple_data:
                row = tuple(None if x == 'nan' else x for x in row)  # Замена 'nan' на None
                print(row)  # Печать строки для отладки

            cursor.executemany(insert_query, tuple_data)
            connection.commit()
            print("Данные успешно импортированы")

    except Error as e:
        print(f"Ошибка при подключении к MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Соединение с MySQL закрыто")

# Основной запуск
import_excel_to_mysql(db_config, 'КАРТОЧКИ ВИЛЛЫ.xlsx')
