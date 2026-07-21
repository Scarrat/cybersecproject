from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('security/', views.security_index, name='security_index'),
    path('security/sql/', views.sql_search, name='sql_search'),
    path('security/register/', views.register_user, name='register_user'),
    path('security/login/', views.login_user, name='login_user'),
    path('security/admin-panel/', views.admin_panel, name='admin_panel'),
    path('security/xss/', views.xss_search, name='xss_search'),
]

