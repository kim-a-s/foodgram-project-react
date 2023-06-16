![Yamdb](https://github.com/kim-a-s/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Продуктовый помощник Foodgram - дипломный проект студента 50 когорты Яндекс.Практикум Ким Алексея.
Проект упакован в контейнеры.
Развернутый проект на боевом сервере доступен по адресу: http://158.160.69.6/recipes

Админка: http://158.160.69.6/admin/
Суперпользователь: admin
Пароль: admin

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты кулинарных изделий, подписываются на публикации других авторов и добавляют рецепты в избранное.
Пользователь может добавлять рецепты в список покупок и скачивать его. В списке будут все необходимые ингридиенты и их суммарное количество.

## Технологии
* Django, Postgresql, Nginx, Gunicorn, Docker, React.
* Проект размещен в контейнерах Docker.

## Шаблон наполнения .env файла
* Файл .env включает следующие переменные:
	* DB_ENGINE=django.db.backends.postgresql (проект работает с postresql)
	* DB_NAME (название базы данных)
	* POSTGRES_USER (имя пользователя)
	* POSTGRES_PASSWORD (пароль пользователя)
	* DB_HOST (название контейнера, по умолчанию - db)
	* DB_PORT (порт для подключения к БД)
    * SECRET_KEY (секретный код для Django в settings.py)

### Инструкция по развертыванию проекта локально:

Склонируйте проект
```bash
  git clone https://link-to-project
```

Перейдите в папку infra, содержащую файл docker-compose.yaml

```bash
  cd infra
```

Разверните проект в контейнерах

```bash
  docker-compose up -d --build
```

Выполните миграции

```bash
  docker-compose exec web python3 manage.py migrate
```

Загрузите статику

```bash
  docker-compose exec web python3 manage.py collectstatic --no-input
```

Создайте суперпользователя

```bash
  docker-compose exec web python3 manage.py createsuperuser
```

Загружаем данные ингредиентов в базу данных:
```bash
docker-compose exec web python3 manage.py load_ingrs
```

Загружаем данные тегов в базу данных:
```bash
docker-compose exec web python3 manage.py load_tags
```

# Автор:
* [Алексей Ким](https://github.com/kim-a-s)
