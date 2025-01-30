from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'portal_estudante'

urlpatterns = [
    path('', lambda request: redirect('portal_estudante:dashboard'), name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.report, name='report'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('simulator/', views.simulator, name='simulator'),
] 