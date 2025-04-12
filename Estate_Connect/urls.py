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
from Estate_App.floor_plan import generate_blueprint, generate_3d

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('Admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-engineers/', views.admin_engineers, name='admin_engineers'),
    path('admin-dealers/', views.admin_dealers, name='admin_dealers'),
    path('admin-customers/', views.admin_customers, name='admin_customers'),
    path('admin-properties/', views.admin_properties, name='admin_properties'),

    path("engineers/approve/<int:user_id>/", views.approve_engineer, name="approve_engineer"),
    path("dealers/approve/<int:user_id>/", views.approve_dealer, name="approve_dealer"),
    path("engineers/remove/<int:user_id>/", views.remove_engineer, name="remove_engineer"),
    path("dealers/remove/<int:user_id>/", views.remove_dealer, name="remove_dealer"),
    path("customers/remove/<int:user_id>/", views.remove_customer, name="remove_customer"),
    path("properties/approve/<int:property_id>/", views.approve_property, name="approve_property"),
    path("properties/remove/<int:property_id>/", views.remove_property, name="remove_property"),

    path('dealer-dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('engineer-dashboard/', views.engineer_dashboard, name='engineer_dashboard'),

    path('user-profile/', views.user_profile, name='user_profile'),
    path('properties/', views.property_list, name='property_list'),
    path('engineers_list/', views.engineers_list, name='engineers_list'),
    path('property/<int:property_id>/', views.property_details, name='property_details'),
    path('model_3d/<int:property_id>/', views.model_3d, name='model_3d'),

    path('dealer_upload_property/', views.dealer_upload_property, name='dealer_upload_property'),
    path('upload_3d_model/', views.upload_3d_model, name='upload_3d_model'),

    path('request-modification/<int:property_id>/', views.request_modification, name='request_modification'),
    path('dealer/manage-requests/', views.dealer_manage_requests, name='dealer_manage_requests'),
    path('create_order/<property_id>/', views.create_order, name='create_order'),
    path('payment-success/', views.payment_success, name='payment_success'),

    path('generate-plan/', views.generate_plan, name='generate_plan'),  
    path("floor-plan/", views.floor_plan_view, name="floor_plan"),
    path('api/floorplan/<int:plan_id>/', views.api_floorplan, name='api_floorplan'),
    path('generate-blueprint/', generate_blueprint, name='generate_blueprint'),
    path('blueprint/', views.blueprint, name='blueprint'),
    path("generate-3d/", generate_3d, name="generate_3d"),
    path("print_2d/", views.print_2d, name="print_2d"),
    path("fabric_2d/", views.fabric_2d, name="fabric_2d"),
    path("plot_2d/", views.plot_2d, name="plot_2d"),
    path("plot_3d/", views.plot_3d, name="plot_3d"),

    path("input_page/", views.input_page, name="input_page"),
    path("search-engineers/", views.search_engineers, name="search_engineers"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


