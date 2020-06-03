#Instructions

1. Создать виртуальное окружение
2. Установить зависимостри 'pip install -r requirements.txt'
3. Установить переменные окружения:
    set PYTHONPATH=src
    set FLASK_APP=app:create_app
4. Создать директорию Images для загрузки изображений
flask run

**Пример запроса для создания пользователя**

1. POST "http://127.0.0.1:5000/users"

2. Все ниже указанные данные передаются в теле запроса "body" в формате JSON

3. {

  "email": "test@mail.ru",
  
  "password": "123456",
  
  "first_name": "Diana",
  
  "last_name": "Smith",
  
  "is_seller": true, 
  
  "phone": "1565665",
  
  "zip_code": 454000,
  
  "city_id": 1,
  
  "street": "Денина",
  
  "home": "53"
  
}

**Предполагаемый ответ сервера - 201** 

{

  "city_id": 1,
  
  "email": "Test@mail.ru",
  
  "first_name": "Diana",
  
  "home": "53",
  
  "id": 1,
  
  "is_seller": 1,
  
  "last_name": "Smith",
  
  "phone": "1565665",
  
  "street": "Денина",
  
  "zip_code": 454000
  
}

**В базе данных создан этот тестовый аккаунт для знакомства с интерфейсом приложения. Далее
представлен список комманд и их краткое описание:** 

Авторизация: вход и выход.

POST /auth/login

Request:
{
  "email": str,
  "password": str
}

POST /auth/logout


Получение пользователя. Доступно только авторизованным пользователям.

GET /users/`<id>`

Response:
{

  "id": int,
  
  "email": str,
  
  "first_name": str,
  
  "last_name": str,
  
  "is_seller": bool,
  
  "phone": str?,
  
  "zip_code": int?,
  
  "city_id": int?,
  
  "street": str?,
  
  "home": str?
  
}
 


PATCH /users/`<id>`


Получение списка объявлений: всех и принадлежащих пользователю. 
Список можно фильтровать с помощью query string параметров, все параметры необязательные.

GET /ads

GET /users/`<id>`/ads

Query string:

  seller_id: int?
  
  tags: str?
  
  make: str?
  
  model: str?
  

Публикация объявления. 
Доступно только авторизованным пользователям. 
Доступно только если пользователь является продавцом.

POST /ads

POST /users/`<id>/`ads

Request:
{

  "title": str,
  
  "tags": [str, ...], // Список тегов строками
  
  "car": {  
    "make": str,    
    "model": str,    
    "colors": [int], // Список ID цветов    
    "mileage": int,    
    "num_owners": int?,    
    "reg_number": str,    
    "images": [    
      {    
        "title": str,
        "url": str
      }
    ]
  }
}

Получение объявления.

GET /ads/`<id>`

Частичное редактирование объявления. 
Доступно только авторизованным пользователям. 
Может совершать только владелец объявления.

PATCH /ads/`<id>`
Request:
{
  "title": str?,
  
  "tags": [str]?, // Список тегов строками
  
  "car": {  
    "make": str?,    
    "model": str?,
    "colors": [int]?, // Список ID цветов
    "mileage": int?,
    "num_owners": int?,
    "reg_number": str?,
    "images": [
      {
        "title": str,
        "url": str
      }
    ]?
  }
}
 

DELETE /ads/`<id>` Удаление объявления. 


GET /cities  Получение списка городов.

Response:
[
  {
    "id": int,
    "name": str
  }
]
 

Создание города. 

POST /cities

Request:
{
  "name": str
}

GET /colors Получение списка цветов. Доступно только авторизованным пользователям.

POST /colors Создание цвета. Доступно только авторизованным пользователям. 
Доступно только если пользователь является продавцом. 

Request:
{
  "name": str,
  "hex": str
}

POST /images - Загрузка изображения. Доступно только авторизованным пользователям. 
Доступно только если пользователь является продавцом.

Request:
  файл изображения в поле формы file

GET /images/`<name>` - Получение изображения.





