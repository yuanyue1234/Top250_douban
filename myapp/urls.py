from django.urls import path
from . import views
urlpatterns = [
    # index.html
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('index2',views.index2,name='index2'),
]
