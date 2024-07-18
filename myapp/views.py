from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import os

def index(request):
    data_list = []

    # 读取所有JSON文件并合并数据
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    for i in range(1, 11):
        file_path = os.path.join(data_dir, f'豆瓣_{i}.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_list.extend(list(data.values()))

    paginator = Paginator(data_list, 25)  # 每页显示50条数据

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {'page_obj': page_obj})
