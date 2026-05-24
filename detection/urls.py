from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name='home'),
    path('detect/', views.detect, name='detect'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('appointment/', views.appointment, name='appointment'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('update-status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('drug-check/', views.drug_check, name='drug_check'),
]