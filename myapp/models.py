from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)  # 电影标题
    img = models.URLField()  # 电影封面图 URL
    href = models.URLField()  # 电影链接
    quote = models.TextField()  # 电影引用（或简介）
    # 其他字段...

    def __str__(self):
        return self.title
