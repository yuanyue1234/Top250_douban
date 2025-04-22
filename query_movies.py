#!/usr/bin/env python
import os
import sys
from pathlib import Path

# 将项目路径添加到环境变量
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

import django
django.setup()

from myapp.models import Movie

def print_movie_info(movie):
    print(f"ID: {movie.id}")
    print(f"豆瓣ID: {movie.douban_id}")
    print(f"标题: {movie.title}")
    print(f"评分: {movie.score}")
    print(f"年份: {movie.year}")
    print(f"国家: {movie.countries}")
    print(f"类型: {movie.genres}")
    print(f"引用: {movie.quote}")
    print(f"链接: {movie.href}")
    print(f"图片: {movie.img}")
    print("-" * 40)

def query_movies():
    print(f"数据库中共有 {Movie.objects.count()} 部电影")
    
    # 显示评分最高的5部电影
    print("\n评分最高的5部电影:")
    for movie in Movie.objects.order_by('-score')[:5]:
        print(f"{movie.title} - 评分: {movie.score}")
    
    # 显示按年份分组的电影数量
    print("\n按年份分组的电影数量:")
    year_stats = {}
    for movie in Movie.objects.all():
        year = movie.year
        if year in year_stats:
            year_stats[year] += 1
        else:
            year_stats[year] = 1
    
    for year, count in sorted(year_stats.items()):
        print(f"{year}: {count}部")
    
    # 搜索功能
    search_term = input("\n请输入要搜索的电影名称 (直接回车查看第一部电影详情): ")
    if search_term:
        results = Movie.objects.filter(title__contains=search_term)
        print(f"\n找到 {results.count()} 个结果:")
        for movie in results:
            print_movie_info(movie)
    else:
        # 显示第一部电影的详细信息
        first_movie = Movie.objects.first()
        if first_movie:
            print("\n第一部电影详情:")
            print_movie_info(first_movie)

if __name__ == "__main__":
    query_movies() 