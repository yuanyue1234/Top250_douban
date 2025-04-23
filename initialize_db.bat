@echo off
echo 正在创建数据库迁移文件...
python manage.py makemigrations

echo 正在应用数据库迁移...
python manage.py migrate

echo 正在导入数据...
python import_movies.py

echo 数据库设置完成!
pause 