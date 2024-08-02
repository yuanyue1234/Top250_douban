from django.urls import path
from . import views
urlpatterns = [
    # index.html
    path('', views.index, name='index'),
    # path('get-data/', views.get_data, name='get_data'),
    path('get-paginated-data/', views.get_paginated_data, name='get_paginated_data'),
]
