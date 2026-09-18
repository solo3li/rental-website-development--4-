from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/student/', views.register_student_view, name='register_student'),
    path('register/landlord/', views.register_landlord_view, name='register_landlord'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
]
