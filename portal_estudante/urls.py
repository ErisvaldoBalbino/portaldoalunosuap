from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'portal_estudante'

urlpatterns = [
    path('', lambda request: redirect('portal_estudante:dashboard'), name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('student/<str:registration>/', views.get_student_info, name='student_info'),
    path('report/', views.generate_report, name='report'),
] 