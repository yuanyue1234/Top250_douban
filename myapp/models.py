from django.db import models

class Movie(models.Model):
    douban_id = models.CharField(max_length=10, unique=True)  # 豆瓣ID
    title = models.CharField(max_length=255)  # 电影标题
    img = models.URLField()  # 电影封面图 URL
    href = models.URLField()  # 电影链接
    quote = models.TextField()  # 电影引用（或简介）
    score = models.FloatField()  # 评分
    year = models.CharField(max_length=10)  # 年份
    countries = models.CharField(max_length=255)  # 国家，以逗号分隔
    genres = models.CharField(max_length=255)  # 类型/属性，以逗号分隔

    def __str__(self):
        return self.title