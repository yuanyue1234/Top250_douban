# 分页
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import os
import re
import json
# 数据可视化
from pyecharts.charts import Pie, Bar, Line, WordCloud, Scatter, Bar3D
from pyecharts import options as opts
from django.shortcuts import render
from myapp.models import Movie

def lode_data():
    # 从数据库获取所有电影数据
    movies = Movie.objects.all()
    data_list = []
    
    for movie in movies:
        # 将数据库对象转换为与原JSON格式兼容的字典
        movie_dict = {
            'id': movie.douban_id,
            'title': movie.title,
            'img': movie.img,
            'href': movie.href,
            'quote': movie.quote,
            'score': movie.score,
            'tags': {
                '时间': movie.year,
                '国家': movie.countries.split(',') if movie.countries else [],
                '属性': movie.genres.split(',') if movie.genres else []
            }
        }
        data_list.append(movie_dict)
    
    return data_list

# 原来从JSON文件读取数据的函数，保留作为备份
def lode_data_from_json():
    # 初始化一个空列表来存储分页数据
    data_list = []
    # 获取当前脚本所在目录下的 'data' 文件夹路径
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    # 循环从 1 到 10
    for i in range(1, 11):
        # 构建每个 JSON 文件的完整路径
        file_path = os.path.join(data_dir, f'豆瓣_{i}.json')
        # 以读取和 UTF-8 编码方式打开文件
        with open(file_path, 'r', encoding='utf-8') as f:
            # 加载 JSON 数据
            data = json.load(f)
            # 将当前文件中的数据值扩展到 data_list 中
            data_list.extend(list(data.values()))

    return data_list


def index(request):
    # 获取搜索查询参数
    search_query = request.GET.get('query','')
    
    # 直接从数据库查询
    if search_query:
        movies = Movie.objects.filter(title__icontains=search_query)
    else:
        movies = Movie.objects.all()
    
    # 将数据库对象转换为与原JSON格式兼容的字典
    data_list = []
    for movie in movies:
        movie_dict = {
            'id': movie.douban_id,
            'title': movie.title,
            'img': movie.img,
            'href': movie.href,
            'quote': movie.quote,
            'score': movie.score,
            'tags': {
                '时间': movie.year,
                '国家': movie.countries.split(',') if movie.countries else [],
                '属性': movie.genres.split(',') if movie.genres else []
            }
        }
        data_list.append(movie_dict)

    # 创建分页器对象
    paginator = Paginator(data_list, 25)

    # 获取当前页码
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 构建上下文字典
    context = {
        'movies': page_obj,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'pages': paginator.page_range,
        'form': SearchForm(initial={'query': search_query}),  # 将搜索表单传递给模板
        'query': search_query,  # 添加搜索查询参数到上下文
    }

    return render(request, 'index.html', context)

# 搜索字段
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='搜索', max_length=255)

# 数据可视化
def chart(request):
    data_list = lode_data()
    from collections import defaultdict

    # 数据处理
    # 初始化统计字典
    tag_count = defaultdict(int)
    country_count = defaultdict(int)
    year_count = defaultdict(int)
    score_count = defaultdict(int)

    # 初始化列表
    top20_movie = []
    year_score = []
    country_year_count = []
    count = 0
    # 遍历data_list，统计标签、国家和时间的电影数量
    for movie in data_list:
        tags = movie["tags"]["属性"]
        years = movie["tags"]["时间"]
        countries = movie["tags"]["国家"]
        scores = movie["score"]
        for tag in tags:
            tag_count[tag] += 1

        for country in countries:
            country_count[country] += 1

        score_count[scores] += 1
        if (count < 20):
            top20_movie.append([movie["title"], movie["score"]])
            count += 1
        # year_score
        years = re.findall(r'\d+', years)[0] if years else "0"
        year_count[years] += 1
        year_score.append([years, movie["score"]])

        country_year_count.append((countries, years, scores))

    # 将结果转换为普通字典
    tag_count = dict(tag_count)
    country_count = dict(country_count)
    year_count = dict(year_count)
    score_count = dict(score_count)
    year_score = dict(year_score)
    # print(year_score)
    # print(score_count)
    top20_movie = dict(top20_movie)
    # print(top20_movie)

    # 对 year_count 字典的项按照电影数量排序
    sorted_year_count = sorted(year_count.items(), key=lambda x: x[1])  # 按评分排序
    sorted_count_year = sorted(year_count.items(), key=lambda x: x[0])  # 按照年份排序
    sorted_year_score = sorted(year_score.items(), key=lambda x: x[0])  # 按照年份排序
    # print(sorted_year_score)
    sorted_country_year_count = sorted(country_year_count, key=lambda x: x[1])
    print(country_year_count)
    sorted_tag_count = sorted(tag_count.items(), key=lambda x: x[1])  # 按照年份排序

    def create_pie_chart():
        """
        pie:根据不同国家统计电影数量

        :return:
        """
        # 处理饼图数据，小于 5 的国家归为 "其他"
        other_count = 0
        new_country_count = {}
        for country, count in country_count.items():
            if count < 5:
                other_count += count
            else:
                new_country_count[country] = count
        if other_count > 0:
            new_country_count["其他国家"] = other_count

        # 创建饼图
        pie = Pie()
        pie.add(
            "国家",
            [list(z) for z in zip(new_country_count.keys(), new_country_count.values())],
            color_by='data',
            radius=["5%", "85%"],
            itemstyle_opts=opts.ItemStyleOpts(border_color='white', border_width=2, border_radius='8px', ),
            selected_offset=30
        )
        pie.set_colors(
            ["#8c9eff", "#ff6b6b", "#920000", "#ffd700", "#9370db", "#00bfff", "#ff7f50", "#66cdaa", "#d87093",
             "#00ff00", 'red', "#24273A"])
        pie.set_global_opts(
            title_opts=opts.TitleOpts(title="不同国家的电影数量", subtitle="根据不同国家统计电影数量"),
            legend_opts=opts.LegendOpts(is_show=True, orient="vertical", pos_right='8%', pos_top='20%'),
            # 图例 orient排列方式
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature=opts.ToolBoxFeatureOpts(
                    # save_as_image={"show": True},  # 下载原图工具
                    # data_view={"show": True},  # 数据视图工具
                    # 将其他工具设为不显示
                    magic_type={"show": False},  # 动态类型切换。
                    restore={"show": False},  # 配置项还原
                    data_zoom={"show": False},  # 数据区域缩放
                    brush={"show": False},  # 选框组件的控制按钮
                )
            ),

        )
        pie.set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}"),
            tooltip_opts=opts.TooltipOpts(formatter="{b}: {c} ({d}%)")
        )

        return pie.render_embed()  # 返回嵌入的HTML字符串

    def create_bar_year_chart():
        """
        根据不同的年代统计电影数量的bar和line
        :return:
        """
        years_bar, counts_bar = zip(*sorted_count_year)

        # 定义年代范围和对应的标签
        decades = {
            "很久以前": (1900, 1969),
            "70年代": (1970, 1979),
            "80年代": (1980, 1989),
            "90年代": (1990, 1999),
            "2000年": (2000, 2009),
            "2010年": (2010, 2019),
            "近代": (2020, 3000),
        }

        # 初始化存储每个年代的电影数量的字典
        count_by_decade = {decade: 0 for decade in decades.keys()}

        # 遍历排序后的年份统计数据，按照年代进行统计
        for year, count in sorted_year_count:
            # year = re.findall(r'\d+',year)[0]
            decade_found = False
            for decade_label, (start_year, end_year) in decades.items():
                # 检查年份是否在当前年代范围内
                if start_year <= int(year) <= end_year:
                    # 将电影数量累计到相应的年代
                    count_by_decade[decade_label] += count
                    decade_found = True
                    break  # 年代一旦匹配就跳出内层循环
            if not decade_found:
                print(f"Year {year} does not fall into any defined decade.")

        # print("Count by Decade:", count_by_decade)  # 调试：打印年代统计数据
        # print("Years (Decades):", years)  # 调试：打印年代标签
        # print("Counts:", counts)  # 调试：打印每个年代的电影数量
        # print("Sorted Year Count:", sorted_year_count)  # 调试：打印排序后的年份统计数据
        # 对年代进行排序并获取标签和数量
        years = list(count_by_decade.keys())
        counts = list(count_by_decade.values())
        # 创建柱状图 - 时间
        bar_year = Bar()
        bar_year.add_xaxis(years)  # 添加X轴数据（年代标签）
        bar_year.add_yaxis("电影数量", counts, color_by='data',
                           itemstyle_opts={
                               "barBorderRadius": [10, 10, 0, 0],
                               "shadowColor": "rgb(0, 160, 221)",

                           }
                           )  # 添加Y轴数据（电影数量）
        bar_year.set_global_opts(
            # title_opts=opts.TitleOpts(title="不同时间的电影数量",subtitle="根据不同的年代统计电影数量"),  # 设置图表标题
            # xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),  # X轴标签旋转45度，避免重叠
            yaxis_opts=opts.AxisOpts(
                max_=max(counts),
                min_=0,
            ),
            # 图例 orient排列方式
            datazoom_opts=[opts.DataZoomOpts()],  # 添加数据缩放选项

            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image={"show": True,"type_":"png","background_color":"white"},  # 下载原图工具
                    # data_view={"show": False},  # 数据视图工具
                    # 将其他工具设为不显示
                    magic_type={"show": False},  # 动态类型切换。
                    restore={"show": False},  # 配置项还原
                    data_zoom={"show": False},  # 数据区域缩放
                    brush={"show": False},  # 选框组件的控制按钮
                ),
                orient="horizontal",
            ),
        )

        bar_year.set_series_opts(
            label_opts=opts.LabelOpts(text_width='bolder', font_size='12'),
        )

        line_year_Era = Line()
        line_year_Era.add_xaxis(years_bar)
        line_year_Era.add_yaxis('', counts_bar, color_by='data')  # 添加Y轴数据（电影数量）
        line_year_Era.set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
        line_year_Era.set_global_opts(
            datazoom_opts=[opts.DataZoomOpts(
            )],
            title_opts=opts.TitleOpts(title="不同时间的电影数量", subtitle="根据不同的年代统计电影数量"),  # 设置图表标题
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image={"show": True,"type_":"png","background_color":"white"},  # 下载原图工具
                    data_view={"show": False},  # 数据视图工具
                    # 将其他工具设为不显示
                    # magic_type={"show": False},  # 动态类型切换。
                    restore={"show": False},  # 配置项还原
                    data_zoom={"show": False},  # 数据区域缩放
                    # brush={"show": False},  # 选框组件的控制按钮
                ),
                orient="horizontal",
            ),
        )
        return line_year_Era.render_embed(), bar_year.render_embed()  # 返回嵌入的HTML字符串

    def create_bar_tag_chart():
        """
        bar WordCloud 根据标签统计电影数量
        :return:
        """
        # print(sorted_tag_count)
        sorted_tag_count_dict = dict(sorted_tag_count)
        # 创建柱状图 - 标签
        bar_tag = Bar()
        tags = list(sorted_tag_count_dict.keys())
        counts = list(sorted_tag_count_dict.values())
        bar_tag.add_xaxis(tags)
        bar_tag.add_yaxis(
            "电影数量",
            counts,
            # 设置颜色根据数据大小变化，数值越大颜色越深
            color_by="data",
            # 设置柱状图圆角
            label_opts=opts.LabelOpts(is_show=True, position="top", formatter="{c}"),
            # 设置柱状图样式
            itemstyle_opts=opts.ItemStyleOpts(
                border_radius=[10, 10, 0, 0]  # 设置四个角的圆角半径
            ),
        )
        bar_tag.set_global_opts(
            title_opts=opts.TitleOpts(title="电影标签统计", subtitle="根据标签统计电影数量"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
            datazoom_opts=[opts.DataZoomOpts()],
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                    data_view={"show": False},  # 数据视图工具
                    # 将其他工具设为不显示
                    # magic_type={"show": False},  # 动态类型切换。
                    # restore={"show": False},  # 配置项还原
                    # data_zoom={"show": False},  # 数据区域缩放
                    # brush={"show": False},  # 选框组件的控制按钮
                ),
            )
        )

        wordcloud_tag = (
            WordCloud()
            .add(
                "",
                sorted_tag_count,
                word_gap=2,
                word_size_range=[20, 90],
                width=700,
                height=700,
                is_draw_out_of_bound=True,
                textstyle_opts=opts.TextStyleOpts(font_family="cursive"),
                shape='star'
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="标签词云", ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                        data_view={"show": False},  # 数据视图工具
                        # 将其他工具设为不显示
                        magic_type={"show": False},  # 动态类型切换。
                        restore={"show": False},  # 配置项还原
                        data_zoom={"show": False},  # 数据区域缩放
                        brush={"show": False},  # 选框组件的控制按钮
                    ),
                )
            )
        )
        return bar_tag.render_embed(), wordcloud_tag.render_embed()  # 返回嵌入的HTML字符串

    def create_pie_score_chart():
        """
        pie bar 根据电影的评分统计评分数量和总评分数量
        :return:
        """
        pie_chart = (
            Pie()
            .add(
                "评分占比",
                [list(z) for z in zip(score_count.keys(), score_count.values())],
                radius=["5%", "75%"],
                rosetype="radius",
                itemstyle_opts=opts.ItemStyleOpts(border_color='white', border_width=2, border_radius='8px'),

            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="评分总数量"),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                        data_view={"show": False},  # 数据视图工具
                        # 将其他工具设为不显示
                        magic_type={"show": False},  # 动态类型切换。
                        restore={"show": False},  # 配置项还原
                        data_zoom={"show": False},  # 数据区域缩放
                        brush={"show": False},  # 选框组件的控制按钮
                    ),
                )
            )

            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=True, formatter="{b}分"),
                tooltip_opts=opts.TooltipOpts(formatter="{b}分: {c}个 占比:({d}%)"),
            )
            .render_embed()
        )
        top20_movie_title = list(top20_movie.keys())
        top20_movie_score = list(top20_movie.values())
        print(len(top20_movie_title))
        bar_chart = (
            Bar()
            .add_xaxis(top20_movie_title)
            .add_yaxis("Top20", top20_movie_score, color_by='data',
                       itemstyle_opts=opts.ItemStyleOpts(border_radius=[10, 10, 0, 0]))  # Add scores as the Y-axis
            .set_global_opts(
                title_opts=opts.TitleOpts(title="电影top20", subtitle="根据电影的评分统计评分数量"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                yaxis_opts=opts.AxisOpts(name="", min_=9),
                datazoom_opts=opts.DataZoomOpts(
                    is_show=True,
                    type_="inside",
                ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                        # data_view={"show": False},  # 数据视图工具
                        # 将其他工具设为不显示
                        # magic_type={"show": False},  # 动态类型切换。
                        # restore={"show": False},  # 配置项还原
                        data_zoom={"show": False},  # 数据区域缩放
                        # brush={"show": False},  # 选框组件的控制按钮
                    ),
                )

            )
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(formatter="top榜:{b},{c}分")
            )
            .render_embed()
        )
        return bar_chart, pie_chart

    def create_scatter_chart():
        """
        散点图 scatter :根据评分和年份的关系观察图
        :return:
        """
        year, score = zip(*sorted_year_score)
        scatter_chart = (
            Scatter()
            .add_xaxis(year)
            .add_yaxis(
                '',
                score,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width='1'
                ),
            )
            .set_series_opts(

            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="年份评分散点图", subtitle="根据评分和年份的关系观察图"),
                datazoom_opts=[
                    opts.DataZoomOpts(type_="slider"),
                    opts.DataZoomOpts(type_="slider", orient="vertical", range_start=100, range_end=80),
                ],
                visualmap_opts=opts.VisualMapOpts(max_=10, min_=8),  # type_="size" 改颜色类型
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                        data_view={"show": False},  # 数据视图工具
                        # 将其他工具设为不显示
                        magic_type={"show": False},  # 动态类型切换。
                        restore={"show": False},  # 配置项还原
                        data_zoom={"show": False},  # 数据区域缩放
                        brush={"show": False},  # 选框组件的控制按钮
                    ),
                )
            )

            .render_embed()
        )
        return scatter_chart

    def create_bar3D_tag_year_count_chart():
        datas = [[d[0][0], d[1], d[2]] for d in sorted_country_year_count]
        # 定义年代范围和对应的标签
        """
        "很久以前" 0
        "70年代" 1
        "80年代" 2
        "90年代" 3
        "2000年 4
        "2010年 5
        "近代": 6
        """
        decades = {
            0: (1900, 1969),
            1: (1970, 1979),
            2: (1980, 1989),
            3: (1990, 1999),
            4: (2000, 2009),
            5: (2010, 2019),
            6: (2020, 3000),
        }
        countries = {
            0: "韩国",
            1: "法国",
            2: "英国",
            3: "美国",
            4: "日本",
            5: "中国大陆",
            6: "中国香港"
        }
        # 存储筛选后的数据
        filtered_datas = []

        for data in datas:
            # 检查国家是否匹配
            if any(countrie in data[0] for countrie in countries.values()):
                filtered_datas.append(data)

        # print(filtered_datas)

        # 遍历排序后的年份统计数据，按照年代进行统计
        for data in filtered_datas:

            decade_found = False
            # 检查年份是否在当前年代范围内
            for decade_label, (start_year, end_year) in decades.items():
                if start_year <= int(data[1]) <= end_year:
                    # 将电影数量累计到相应的年代
                    data[1] = decade_label
                    decade_found = True
                    break  # 年代一旦匹配就跳出内层循环

            if not decade_found:
                print(f"Year {data[1]} does not fall into any defined decade.")
                continue  # 如果年代不匹配，跳过当前数据

            # 检查国家是否匹配，并替换为对应的 key
            country_key = next((key for key, value in countries.items() if value in data[0]), None)
            if country_key is not None:
                data[0] = country_key

        print(filtered_datas)
        x = list(countries.values())
        y = ["很久以前",
             "70年代",
             "80年代",
             "90年代",
             "2000年",
             "2010年",
             "近代", ]
        # 创建3D柱状图
        bar3d_chart = (
            Bar3D()
            .add(
                "",
                filtered_datas,
                xaxis3d_opts=opts.Axis3DOpts(x, type_="category"),
                yaxis3d_opts=opts.Axis3DOpts(y, type_="category"),
                zaxis3d_opts=opts.Axis3DOpts(type_="value", min_=8.4, max_=9.9),
                shading="lambert",  # 尝试其他 shading 参数

            )
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(max_=9.9, min_=8.4, ),
                title_opts=opts.TitleOpts(
                    title="国家年代评分分布",
                    subtitle="根据国家的不同、发布年代的不同、评分的高低来展示三维图形",

                ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image={"show": True, "type_": "png", "background_color": "white"},  # 下载原图工具
                        # restore={"show": False},  # 配置项还原
                        data_view={"show": False},  # 数据视图工具
                        # 将其他工具设为不显示
                        magic_type={"show": False},  # 动态类型切换。
                        data_zoom={"show": False},  # 数据区域缩放
                        brush={"show": False},  # 选框组件的控制按钮
                    ),
                )

            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=True,
                    color="black",  # 标签颜色为白色
                    position="inside",  # 标签位置
                    text_border_color="white",
                    text_border_width=2,

                )
            )
        )

        # 返回嵌入的 HTML 字符串
        return bar3d_chart.render_embed()

    pie_chart_html = create_pie_chart()
    bar_year_chart_html, bar_year_chart_html_1 = create_bar_year_chart()
    bar_tag_chart_html, bar_tag_chart_html_1 = create_bar_tag_chart()
    pie_score_chart_html, pie_score_chart_html_1 = create_pie_score_chart()
    bar3D_tag_year_count_chart = create_bar3D_tag_year_count_chart()
    scatter_chart_html = create_scatter_chart()
    return render(request, 'chart.html', {
        'pie_chart_html': pie_chart_html,
        'scatter_chart_html': scatter_chart_html,
        'bar_year_chart_html': bar_year_chart_html,
        'bar_year_chart_html_1': bar_year_chart_html_1,
        'bar_tag_chart_html': bar_tag_chart_html,
        'bar_tag_chart_html_1': bar_tag_chart_html_1,
        'pie_score_chart_html': pie_score_chart_html,
        'pie_score_chart_html_1': pie_score_chart_html_1,
        'bar3D_tag_year_count_chart_html': bar3D_tag_year_count_chart,

    })

def index2(request):

    data = {"message": "Hello from the server!"}
    return render(request, 'index2.html', data)