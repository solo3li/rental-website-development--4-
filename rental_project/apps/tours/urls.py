from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('book/', views.book_tour, name='book'),
]
