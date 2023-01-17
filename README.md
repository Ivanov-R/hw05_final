## Описание проекта:

Проект для опубликования дневников.

Можно публиковать свои посты, подписываться на понравившихся авторов, комментировать записи.

Десять последних записей выводятся на главную страницу.

В админ-зоне доступно управление объектами моделей Post, Group, Comment, Follow.

Пользователь может перейти на страницу любого сообщества, где отображаются десять последних публикаций из этой группы.

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Ivanov-R/hw05_final.git
cd yatube
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```

## Об авторе:

Иванов Роман, студент Яндекс.Практикума 
