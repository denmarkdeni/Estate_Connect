"""
URL configuration for Estate_Connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Estate_App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('remove/<int:user_id>/', views.remove_user, name='remove_user'),
    path('change-role/<int:user_id>/<str:role>/', views.change_role, name='change_role'),
    path('logout/', views.logout_view, name='logout'),
]
