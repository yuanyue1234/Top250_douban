#!/usr/bin/env python
import os
import sys
import json
import glob
from pathlib import Path

# 将项目路径添加到环境变量
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

import django
django.setup()

from myapp.models import Movie

def import_movies():
    # 查找所有JSON文件
    json_files = glob.glob(os.path.join(BASE_DIR, 'myapp', 'data', '*.json'))

    total_imported = 0
    total_skipped = 0

    for json_file in json_files:
        print(f"正在处理文件: {json_file}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                movies_data = json.load(f)

            for movie_id, movie_data in movies_data.items():
                douban_id = movie_data.get('id')
                if not douban_id:
                    print(f"跳过无ID的数据: {movie_data}")
                    total_skipped += 1
                    continue

                # 检查是否已存在
                if Movie.objects.filter(douban_id=douban_id).exists():
                    total_skipped += 1
                    continue

                try:
                    countries = ','.join(movie_data.get('tags', {}).get('国家', []))
                    genres = ','.join(movie_data.get('tags', {}).get('属性', []))

                    Movie.objects.create(
                        douban_id=douban_id,
                        title=movie_data.get('title', ''),
                        img=movie_data.get('img', ''),
                        href=movie_data.get('href', ''),
                        quote=movie_data.get('quote', ''),
                        score=movie_data.get('score', 0),
                        year=movie_data.get('tags', {}).get('时间', ''),
                        countries=countries,
                        genres=genres
                    )
                    total_imported += 1

                except Exception as e:
                    print(f"导入电影 {movie_data.get('title', '未知')} 时出错: {e}", file=sys.stderr)

        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}", file=sys.stderr)

    print(f"\n导入完成! 共导入 {total_imported} 部电影, 跳过 {total_skipped} 部已存在或异常的电影")

if __name__ == "__main__":
    import_movies()
