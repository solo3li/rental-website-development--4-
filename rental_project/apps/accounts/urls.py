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
    path('tour-cancel/<int:booking_id>/', views.student_cancel_tour_view, name='student_cancel_tour'),
    path('roommate-toggle/<int:post_id>/', views.student_toggle_roommate_post_view, name='student_toggle_roommate_post'),
    path('roommate-delete/<int:post_id>/', views.student_delete_roommate_post_view, name='student_delete_roommate_post'),
]
