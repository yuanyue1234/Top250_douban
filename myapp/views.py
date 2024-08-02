import random

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import json
import os

def index(request):
    return render(request, 'index.html')


# js使用动态内容加载
from django.http import JsonResponse

# def get_data(request):
#     data_list = []
#     data_dir = os.path.join(os.path.dirname(__file__), 'data')
#     for i in range(1, 11):
#         file_path = os.path.join(data_dir, f'豆瓣_{i}.json')
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             data_list.extend(list(data.values()))
#     return JsonResponse(data_list, safe=False)

def get_paginated_data(request):
    # 获取分页数据
    data_list = []
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    for i in range(1, 11):
        file_path = os.path.join(data_dir, f'豆瓣_{i}.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_list.extend(list(data.values()))

    paginator = Paginator(data_list, 25)  # 每页显示25条数据

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    data = list(page_obj)
    random_number = random.randint(1, 1000000)  # 生成一个随机数
    return JsonResponse({
        'data': data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_pages': paginator.num_pages,
        'random_number': random_number  # 将随机数添加到返回的 JSON 数据中
    })


# 数据可视化

