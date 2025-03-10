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
from django.urls import path, include
from Estate_App import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from Estate_App.floor_plan import generate_blueprint, generate_3d

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('Admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('remove/<int:user_id>/', views.remove_user, name='remove_user'),
    path('change-role/<int:user_id>/<str:role>/', views.change_role, name='change_role'),
    path('logout/', views.logout_view, name='logout'),
    path('dealer-dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('upload/', views.upload_property, name='upload_property'),
    path('api/properties/', views.property_list, name='property_list'),
    path('api/properties/create/', views.property_create, name='property_create'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('property/<int:property_id>/', views.property_details, name='property_details'),
    path('request-modification/<int:property_id>/', views.request_modification, name='request_modification'),
    path('dealer/manage-requests/', views.dealer_manage_requests, name='dealer_manage_requests'),
    path('engineer/dashboard/', views.engineer_dashboard, name='engineer_dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('admin/verify-users/', views.verify_users, name='verify_users'),
    path('model_3d/', views.model_3d, name='model_3d'),  
    path('generate-plan/', views.generate_plan, name='generate_plan'),  
    path("floor-plan/", views.floor_plan_view, name="floor_plan"),
    path('api/floorplan/<int:plan_id>/', views.api_floorplan, name='api_floorplan'),
    path('generate-blueprint/', generate_blueprint, name='generate_blueprint'),
    path('blueprint/', views.blueprint, name='blueprint'),
    path("generate-3d/", generate_3d, name="generate_3d"),
    path("print_2d/", views.print_2d, name="print_2d"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
