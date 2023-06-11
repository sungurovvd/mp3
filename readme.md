# wav to mp3
---
###
Проект - тестовое задание, выполненное с использованием фреймворка Flask.
## Инструкции по запуску
 - клонируйте репозиторий
 - создайте файл .env и заполните его необходимыми для БД переменными окружения
> По умолчанию:  

    DB_HOST=db
    DB_PORT=5432
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_NAME=mp3_db
    
 - запустите контейнер с БД Postgres следующей командой:  
    docker-compose up -d --build 

---
## Примеры запросов к API
>Cоздание пользователя:  

URL: http://localhost:5000/users  
Метод: POST  
Тело запроса:

    {
        "name": "John"
    }
Ответ:

    {
        "user_id": "generated_user_id",
        "token": "generated_token"
    }

> Добавление аудиозаписи

URL: http://localhost:5000/records  
Метод: POST  
Тело запроса (multipart/form-data):  

    user_id: "generated_user_id"
    token: "generated_token"
    audio: audio_file.wav
Ответ:

    {
        "download_url": "http://localhost:5000/record?id=generated_record_id&user=generated_user_id"
    }

> Скачивание аудиозаписи:    

URL: http://localhost:5000/record?id=generated_record_id&user=generated_user_id  
Метод: GET