from django.urls import path
from django.shortcuts import redirect
from portal_estudante import views

app_name = 'portal_estudante'

urlpatterns = [
    path('', lambda request: redirect('portal_estudante:dashboard'), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('oauth/callback/', views.OAuthCallbackView.as_view(), name='oauth_callback'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('report/', views.ReportView.as_view(), name='report'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('simulator/', views.SimulatorView.as_view(), name='simulator'),
] 