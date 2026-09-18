from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='list'),
    path('property/<int:pk>/', views.property_detail, name='detail'),
    path('property/create/', views.property_create, name='create'),
]
