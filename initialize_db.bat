@echo off
echo 正在初始化数据库...
python manage.py makemigrations myapp
python manage.py migrate
echo 数据库初始化完成！

echo 开始导入电影数据...
python import_movies.py
echo 按任意键退出...
pause > nul 