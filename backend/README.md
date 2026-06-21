# FastApi_test
fast api testing

# OpenAPI
http://0.0.0.0:8000/docs

# Install
sudo apt-get install libpq-dev python3-dev

# Notice
alembic revision --autogenerate -m 'name' создать миграцию
alembic upgrade head обновить до последней миграции

# initialize db
python3 scripts/init_db.py