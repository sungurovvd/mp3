from flask import Flask, request, jsonify, send_file
from uuid import uuid4
from pydub import AudioSegment
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Подключение
connection = psycopg2.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME')
)

cursor = connection.cursor()

# Создание таблицы для пользователей
create_users_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    token UUID
)
"""
cursor.execute(create_users_table_query)
connection.commit()

# Создание таблицы для аудиозаписей
create_records_table_query = """
CREATE TABLE IF NOT EXISTS records (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users (id),
    file_path VARCHAR(255),
    mp3_file_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
"""
cursor.execute(create_records_table_query)
connection.commit()


# Создание пользователя
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')

    if name:
        user_id = str(uuid4())
        token = str(uuid4())

        insert_user_query = "INSERT INTO users (id, name, token) VALUES (%s, %s, %s)"
        cursor.execute(insert_user_query, (user_id, name, token))
        connection.commit()

        return jsonify({'user_id': user_id, 'token': token}), 201
    else:
        return jsonify({'error': 'Name is required.'}), 400


# Добавление аудиозаписи
@app.route('/records', methods=['POST'])
def add_record():
    user_id = request.form.get('user_id')
    token = request.form.get('token')
    audio_file = request.files.get('audio')

    if user_id and token and audio_file:
        select_user_query = "SELECT * FROM users WHERE id = %s AND token = %s"
        cursor.execute(select_user_query, (user_id, token))
        user = cursor.fetchone()

        if user:
            record_id = str(uuid4())
            file_path = f"audio/{record_id}.wav"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            mp3_file_path = f"audio/{record_id}.mp3"

            audio_file.save(file_path)

            audio = AudioSegment.from_wav(file_path)
            audio.export(mp3_file_path, format='mp3')

            insert_record_query = "INSERT INTO records (id, user_id, file_path, mp3_file_path) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_record_query, (record_id, user_id, file_path, mp3_file_path))
            connection.commit()

            return jsonify({'download_url': f"http://localhost:5000/record?id={record_id}&user={user_id}"}), 201
        else:
            return jsonify({'error': 'Invalid user credentials.'}), 401
    else:
        return jsonify({'error': 'Missing required fields.'}), 400


# Скачивание аудиозаписи
@app.route('/record', methods=['GET'])
def download_record():
    record_id = request.args.get('id')
    user_id = request.args.get('user')

    if record_id and user_id:
        select_record_query = "SELECT * FROM records WHERE id = %s AND user_id = %s"
        cursor.execute(select_record_query, (record_id, user_id))
        record = cursor.fetchone()

        if record:
            mp3_file_path = record[3]
            return send_file(mp3_file_path)
        else:
            return jsonify({'error': 'Record not found.'}), 404
    else:
        return jsonify({'error': 'Missing required fields.'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
