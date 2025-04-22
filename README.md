# 豆瓣Top250电影数据导入工具

这个项目包含了一个简单的脚本，用于将豆瓣Top250电影数据导入Django数据库。

## 依赖安装

首先，确保安装了所有必要的依赖：

```bash
pip install -r requirements.txt
```

对于Windows用户，可能需要单独安装mysqlclient：

```bash
pip install mysqlclient
```

## 数据库配置

确保在`djangoProject/settings.py`中配置了正确的数据库连接信息：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4'
        }
    }
}
```

根据你的实际数据库配置修改上述信息。

## 初始化数据库

**重要：** 在导入数据前，必须先初始化数据库创建必要的表结构。

### Windows用户

直接双击`initialize_db.bat`文件执行数据库迁移并导入数据。

### 其他平台用户

执行以下命令：

```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移到数据库
python manage.py migrate

# 导入数据
python import_movies.py
```

## 仅运行数据导入

如果您已经初始化了数据库，只想导入数据：

### Windows用户

直接双击`import_data.bat`文件运行导入过程。

### 其他平台用户

在命令行中运行：

```bash
python import_movies.py
```

## 数据格式

JSON数据格式示例：

```json
{
    "1": {
        "id": "1",
        "img": "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.jpg",
        "title": "肖申克的救赎",
        "tags": {
            "时间": "1994",
            "国家": [
                "美国"
            ],
            "属性": [
                "犯罪",
                "剧情"
            ]
        },
        "score": 9.7,
        "quote": "希望让人自由。",
        "href": "https://movie.douban.com/subject/1292052/"
    }
}
```

数据将被导入到`Movie`模型中，各字段映射如下：
- id → douban_id
- title → title
- img → img
- href → href
- quote → quote
- score → score
- tags.时间 → year
- tags.国家 → countries (逗号分隔)
- tags.属性 → genres (逗号分隔) 