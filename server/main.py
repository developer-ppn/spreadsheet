from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

# Initialize Flask app
app = Flask(__name__)
CORS(app) 

# MySQL connection details
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'  
MYSQL_PASSWORD = 'root@123' 

def create_database_if_not_exists(database_name):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_table_with_headers(database_name, headers, types):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=database_name
        )
        cursor = connection.cursor()

        columns = []
        for header, type_ in zip(headers, types):
            # Map type values to MySQL column types
            if type_ == 'TEXT':
                column_type = 'TEXT'
            elif type_ == 'VARCHAR':
                column_type = 'VARCHAR(255)'
            elif type_ == 'INT':
                column_type = 'INT'
            elif type_ == 'DATE':
                column_type = 'DATE'
            else:
                column_type = 'VARCHAR(255)'  

            columns.append(f"`{header}` {column_type}")

        columns_str = ", ".join(columns)
        create_table_query = f"CREATE TABLE IF NOT EXISTS dynamic_table ({columns_str})"
        cursor.execute(create_table_query)
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/submit', methods=['POST'])
def submit_table():
    data = request.json  
    if not data or 'file_name' not in data or 'rows' not in data or 'headers' not in data or 'types' not in data:
        return jsonify({"error": "Invalid data"}), 400

    file_name = data['file_name']
    rows = data['rows']
    headers = data['headers']
    types = data['types']  

   
    database_name = file_name.replace(" ", "_").replace("-", "_").lower()

    try:
        create_database_if_not_exists(database_name)  
        create_table_with_headers(database_name, headers, types)  

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=database_name
        )
        cursor = connection.cursor()

        # for row in rows:
        #     values = tuple(row.get(header, None) for header in headers)
        #     insert_query = f"INSERT INTO dynamic_table ({', '.join(headers)}) VALUES ({', '.join(['%s'] * len(headers))})"
        #     cursor.execute(insert_query, values)

        connection.commit()
        return jsonify({"message": "Data saved successfully"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
