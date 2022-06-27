![workflow](https://github.com/pkrfc/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Cайт Foodgram, «Продуктовый помощник». 

http://foodgram-bykorolev.ddns.net

```

Сайт с рецептами. Рецепты публикуют сами пользователи.
 В рецепте указаны ингридиенты, фото, описание. Всё это 
возможно редактировать. Есть возможность подписаться на пользователя,
добавить рецепт в избранное и корзину. 

```

http://foodgram-bykorolev.ddns.net/


Стек технологий: python, django, DRF, git, PostgreSQL, docker, workflows
```

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:pkrfc/foodgram-project-react.git

```

Запустите docker-compose
```
cd infra/
docker-compose up -d
```

Выполните миграции, создайте суперпользователя, перенесите статику:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```