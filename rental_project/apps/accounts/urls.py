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
    path('dashboard/update-beds/<int:property_id>/', views.update_beds_view, name='update_beds'),
    path('dashboard/tour-status/<int:booking_id>/', views.update_tour_status_view, name='update_tour_status'),
]
