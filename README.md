# Yatube

## Социальная сеть Yatube

> Социальная сеть Yatube это онлайн-сервис, где каждый желающий может опубликовать свои дневники.
Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи.

## Технологии проекта

- Python 3, Django 2.2, PostgreSQL, Unittest.
- Gunicorn, nginx, Яндекс.Облако(Ubuntu 20.04)

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/BuriloT/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
